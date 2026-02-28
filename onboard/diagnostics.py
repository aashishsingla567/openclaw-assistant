#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_DIR))

import numpy as np
import requests
import sounddevice as sd
from faster_whisper import WhisperModel
from kokoro_onnx import Kokoro

from config import load_settings


def list_devices() -> None:
    devices = sd.query_devices()
    print(json.dumps(devices, indent=2))


def test_tts(text: str) -> None:
    settings = load_settings()
    kokoro = Kokoro(str(settings.kokoro_model_path), str(settings.kokoro_voices_path))
    samples, sample_rate = kokoro.create(
        text,
        voice=settings.kokoro_voice,
        speed=settings.kokoro_speed,
        lang=settings.kokoro_language,
    )
    audio = np.asarray(samples, dtype=np.float32)
    sd.play(audio, sample_rate, device=settings.audio_output_device)
    sd.wait()


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-devices", action="store_true")
    parser.add_argument("--tts", action="store_true")
    parser.add_argument("--stt", action="store_true")
    parser.add_argument("--openclaw", action="store_true")
    parser.add_argument("--text", default="Testing text to speech.")
    parser.add_argument("--seconds", type=float, default=3.0)
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

    if not (args.tts or args.stt or args.openclaw or args.list_devices):
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
