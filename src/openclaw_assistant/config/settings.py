from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KokoroConfig:
    model_path: Path
    voices_path: Path
    voice: str
    speed: float
    language: str


@dataclass(frozen=True)
class TTSPlaybackConfig:
    output_device: str | int | None
    fade_ms: float
    padding_ms: float
    prewarm_ms: float


@dataclass(frozen=True)
class Settings:
    project_root: Path
    porcupine_access_key: str
    porcupine_keyword_path: Path
    porcupine_sensitivity: float
    audio_input_device: str | int | None
    audio_output_device: str | int | None
    command_sample_rate: int
    record_max_seconds: float
    record_min_seconds: float
    silence_seconds: float
    silence_threshold: float
    wakeword_start_delay: float
    listen_start_prompt: str
    wake_hello_prompt: str
    whisper_model: str
    whisper_device: str
    whisper_compute_type: str
    whisper_language: str
    whisper_download_root: Path
    kokoro_model_path: Path
    kokoro_voices_path: Path
    kokoro_voice: str
    kokoro_speed: float
    kokoro_language: str
    openclaw_rest_url: str
    openclaw_timeout_seconds: float
    wakeword_label: str
    tts_fade_ms: float
    tts_padding_ms: float
    tts_prewarm_ms: float

    @property
    def kokoro(self) -> KokoroConfig:
        return KokoroConfig(
            model_path=self.kokoro_model_path,
            voices_path=self.kokoro_voices_path,
            voice=self.kokoro_voice,
            speed=self.kokoro_speed,
            language=self.kokoro_language,
        )

    @property
    def tts_playback(self) -> TTSPlaybackConfig:
        return TTSPlaybackConfig(
            output_device=self.audio_output_device,
            fade_ms=self.tts_fade_ms,
            padding_ms=self.tts_padding_ms,
            prewarm_ms=self.tts_prewarm_ms,
        )

    def validate_runtime_assets(self, *, include_tts_assets: bool = True) -> None:
        if not self.porcupine_access_key:
            raise RuntimeError("Missing PORCUPINE_ACCESS_KEY. Set it in your environment.")
        if not self.porcupine_keyword_path.exists():
            raise RuntimeError(f"Missing wake-word model: {self.porcupine_keyword_path}")
        if include_tts_assets and not self.kokoro_model_path.exists():
            raise RuntimeError(f"Missing Kokoro model: {self.kokoro_model_path}")
        if include_tts_assets and not self.kokoro_voices_path.exists():
            raise RuntimeError(f"Missing Kokoro voices: {self.kokoro_voices_path}")
