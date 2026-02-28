from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any

import numpy as np
from kokoro_onnx import Kokoro

from openclaw_assistant.adapters.audio.output_stream import AudioOutput
from openclaw_assistant.config.settings import Settings


@dataclass(frozen=True)
class KokoroVoiceConfig:
    model_path: str
    voices_path: str
    voice: str
    speed: float
    language: str


@dataclass(frozen=True)
class PlaybackConfig:
    output_device: str | int | None
    fade_ms: float
    padding_ms: float
    prewarm_ms: float


def _shape_audio(
    samples: np.ndarray,
    sample_rate: int,
    fade_ms: float,
    padding_ms: float,
) -> np.ndarray:
    audio = np.asarray(samples, dtype=np.float32)
    fade_len = int(sample_rate * (max(0.0, fade_ms) / 1000.0))
    pad_len = int(sample_rate * (max(0.0, padding_ms) / 1000.0))

    if fade_len > 0 and audio.size > fade_len * 2:
        fade_in = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
        fade_out = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
        audio[:fade_len] *= fade_in
        audio[-fade_len:] *= fade_out
    if pad_len > 0:
        pad = np.zeros(pad_len, dtype=np.float32)
        audio = np.concatenate([pad, audio, pad])
    return audio


class KokoroSpeaker:
    def __init__(self, settings: Settings, *, reuse_output_stream: bool = True) -> None:
        self.reuse_output_stream = reuse_output_stream
        self.voice = KokoroVoiceConfig(
            model_path=str(settings.kokoro.model_path),
            voices_path=str(settings.kokoro.voices_path),
            voice=settings.kokoro.voice,
            speed=settings.kokoro.speed,
            language=settings.kokoro.language,
        )
        self.playback = PlaybackConfig(
            output_device=settings.tts_playback.output_device,
            fade_ms=settings.tts_playback.fade_ms,
            padding_ms=settings.tts_playback.padding_ms,
            prewarm_ms=settings.tts_playback.prewarm_ms,
        )
        self._lock = threading.Lock()
        self._kokoro: Kokoro | None = None
        self._output_stream = None

    def _init_kokoro(self) -> Kokoro:
        if self._kokoro is None:
            self._kokoro = Kokoro(self.voice.model_path, self.voice.voices_path)
        return self._kokoro

    def _get_stream(self, sample_rate: int) -> Any:
        if not self.reuse_output_stream:
            return AudioOutput.create_stream(sample_rate, self.playback.output_device)
        if self._output_stream is None:
            self._output_stream = AudioOutput.create_stream(
                sample_rate,
                self.playback.output_device,
            )
        return self._output_stream

    def close(self) -> None:
        if self._output_stream is None:
            return
        try:
            self._output_stream.stop()
            self._output_stream.close()
        finally:
            self._output_stream = None

    def speak(self, text: str) -> None:
        if not text:
            return
        with self._lock:
            kokoro = self._init_kokoro()
            samples, sample_rate = kokoro.create(
                text,
                voice=self.voice.voice,
                speed=self.voice.speed,
                lang=self.voice.language,
            )
            audio = _shape_audio(
                samples,
                sample_rate,
                self.playback.fade_ms,
                self.playback.padding_ms,
            )
            stream = self._get_stream(sample_rate)
            prewarm_len = int(sample_rate * (max(0.0, self.playback.prewarm_ms) / 1000.0))
            if prewarm_len > 0:
                stream.write(np.zeros(prewarm_len, dtype=np.float32))
            stream.write(audio)
            if not self.reuse_output_stream:
                stream.stop()
                stream.close()
