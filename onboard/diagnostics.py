#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_DIR))

import numpy as np
import pvporcupine
import requests
import sounddevice as sd
from faster_whisper import WhisperModel

from config import load_settings
from tts_pipeline import TTSPipeline


def list_devices() -> None:
    devices = sd.query_devices()
    print(json.dumps(devices, indent=2))


def test_tts(text: str) -> None:
    settings = load_settings()
    print("TTS settings:")
    print(f"  fade_ms={settings.tts_fade_ms}")
    print(f"  padding_ms={settings.tts_padding_ms}")
    print(f"  prewarm_ms={settings.tts_prewarm_ms}")
    print(f"  output_device={settings.audio_output_device}")
    tts = TTSPipeline.from_settings(settings, reuse_output_stream=False)
    try:
        tts.speak(text)
    finally:
        tts.close()


def record_audio(seconds: float, sample_rate: int, device) -> np.ndarray:
    frames = int(seconds * sample_rate)
    audio = sd.rec(frames, samplerate=sample_rate, channels=1, dtype="int16", device=device)
    sd.wait()
    return audio.squeeze().astype(np.float32) / 32768.0


def test_stt(seconds: float) -> None:
    settings = load_settings()
    model = WhisperModel(
        settings.whisper_model,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type,
        download_root=str(settings.whisper_download_root),
    )
    print(f"Recording {seconds:.1f}s... speak now")
    audio = record_audio(seconds, settings.command_sample_rate, settings.audio_input_device)
    segments, _ = model.transcribe(
        audio,
        language=settings.whisper_language,
        beam_size=1,
        best_of=1,
        temperature=0.0,
        condition_on_previous_text=False,
        vad_filter=True,
    )
    text = " ".join([seg.text.strip() for seg in segments if seg.text.strip()])
    print("Transcription:")
    print(text)


def test_openclaw(text: str) -> None:
    settings = load_settings()
    response = requests.post(
        settings.openclaw_rest_url,
        json={"text": text},
        timeout=settings.openclaw_timeout_seconds,
    )
    response.raise_for_status()
    print("OpenClaw response:")
    print(response.text)


def test_wakeword(timeout_seconds: float) -> None:
    settings = load_settings()
    if not settings.porcupine_access_key:
        raise RuntimeError("Missing PORCUPINE_ACCESS_KEY.")
    if not settings.porcupine_keyword_path.exists():
        raise RuntimeError(f"Missing wakeword model: {settings.porcupine_keyword_path}")

    porcupine = pvporcupine.create(
        access_key=settings.porcupine_access_key,
        keyword_paths=[str(settings.porcupine_keyword_path)],
        sensitivities=[settings.porcupine_sensitivity],
    )
    print("Wakeword settings:")
    print(f"  label={settings.wakeword_label}")
    print(f"  keyword_path={settings.porcupine_keyword_path}")
    print(f"  sensitivity={settings.porcupine_sensitivity}")
    print(f"  input_device={settings.audio_input_device}")
    print(f"  sample_rate={porcupine.sample_rate}")
    print(f"  frame_length={porcupine.frame_length}")
    print(
        f"Listening for wakeword for up to {timeout_seconds:.1f}s... "
        f"say '{settings.wakeword_label}'."
    )
    deadline = time.monotonic() + timeout_seconds

    try:
        with sd.RawInputStream(
            samplerate=porcupine.sample_rate,
            blocksize=porcupine.frame_length,
            dtype="int16",
            channels=1,
            device=settings.audio_input_device,
        ) as stream:
            while time.monotonic() < deadline:
                pcm_bytes, _ = stream.read(porcupine.frame_length)
                pcm = np.frombuffer(pcm_bytes, dtype=np.int16)
                if porcupine.process(pcm) >= 0:
                    print("Wakeword detected.")
                    return
    finally:
        porcupine.delete()

    print("Wakeword NOT detected before timeout.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-devices", action="store_true")
    parser.add_argument("--tts", action="store_true")
    parser.add_argument("--stt", action="store_true")
    parser.add_argument("--openclaw", action="store_true")
    parser.add_argument("--wakeword", action="store_true")
    parser.add_argument("--text", default="Testing text to speech.")
    parser.add_argument("--seconds", type=float, default=3.0)
    parser.add_argument("--wakeword-timeout", type=float, default=10.0)
    args = parser.parse_args()

    if args.list_devices:
        list_devices()
        return

    if args.tts:
        test_tts(args.text)
    if args.stt:
        test_stt(args.seconds)
    if args.openclaw:
        test_openclaw(args.text)
    if args.wakeword:
        test_wakeword(args.wakeword_timeout)

    if not (args.tts or args.stt or args.openclaw or args.wakeword or args.list_devices):
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
