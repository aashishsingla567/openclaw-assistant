from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import sounddevice as sd
from kokoro_onnx import Kokoro

if TYPE_CHECKING:
    from config import Settings


@dataclass(frozen=True)
class KokoroVoiceConfig:
    model_path: Path
    voices_path: Path
    voice: str
    speed: float
    language: str


@dataclass(frozen=True)
class PlaybackConfig:
    output_device: str | int | None
    fade_ms: float
    padding_ms: float
    prewarm_ms: float


def _shape_audio(samples: np.ndarray, sample_rate: int, fade_ms: float, padding_ms: float) -> np.ndarray:
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


class TTSPipeline:
    def __init__(
        self,
        voice: KokoroVoiceConfig,
        playback: PlaybackConfig,
        *,
        reuse_output_stream: bool = True,
    ) -> None:
        self.voice = voice
        self.playback = playback
        self.reuse_output_stream = reuse_output_stream

        self._lock = threading.Lock()
        self._kokoro: Kokoro | None = None
        self._output_stream: sd.OutputStream | None = None

    def close(self) -> None:
        if self._output_stream is None:
            return
        try:
            self._output_stream.stop()
            self._output_stream.close()
        finally:
            self._output_stream = None

    def _init_kokoro(self) -> Kokoro:
        if self._kokoro is None:
            self._kokoro = Kokoro(
                str(self.voice.model_path),
                str(self.voice.voices_path),
            )
        return self._kokoro

    def _open_stream(self, sample_rate: int) -> sd.OutputStream:
        stream = sd.OutputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
            device=self.playback.output_device,
        )
        stream.start()
        return stream

    def _get_stream(self, sample_rate: int) -> sd.OutputStream:
        if not self.reuse_output_stream:
            return self._open_stream(sample_rate)
        if self._output_stream is None:
            self._output_stream = self._open_stream(sample_rate)
        return self._output_stream

    def _play_on_stream(self, stream: sd.OutputStream, audio: np.ndarray, sample_rate: int) -> None:
        prewarm_len = int(sample_rate * (max(0.0, self.playback.prewarm_ms) / 1000.0))
        if prewarm_len > 0:
            stream.write(np.zeros(prewarm_len, dtype=np.float32))
        stream.write(audio)

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
                samples=samples,
                sample_rate=sample_rate,
                fade_ms=self.playback.fade_ms,
                padding_ms=self.playback.padding_ms,
            )

            if self.reuse_output_stream:
                stream = self._get_stream(sample_rate)
                self._play_on_stream(stream=stream, audio=audio, sample_rate=sample_rate)
                return

            with self._get_stream(sample_rate) as stream:
                self._play_on_stream(stream=stream, audio=audio, sample_rate=sample_rate)

    @classmethod
    def from_settings(cls, settings: Settings, *, reuse_output_stream: bool = True) -> TTSPipeline:
        return cls(
            voice=KokoroVoiceConfig(
                model_path=settings.kokoro.model_path,
                voices_path=settings.kokoro.voices_path,
                voice=settings.kokoro.voice,
                speed=settings.kokoro.speed,
                language=settings.kokoro.language,
            ),
            playback=PlaybackConfig(
                output_device=settings.tts_playback.output_device,
                fade_ms=settings.tts_playback.fade_ms,
                padding_ms=settings.tts_playback.padding_ms,
                prewarm_ms=settings.tts_playback.prewarm_ms,
            ),
            reuse_output_stream=reuse_output_stream,
        )
