from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


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


def _maybe_int(value: str | None) -> str | int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return value


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return float(value)


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


def _env_str(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def _env_path(name: str, default: Path) -> Path:
    return Path(_env_str(name, str(default))).expanduser()


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def load_settings() -> Settings:
    project_root = Path(__file__).resolve().parent
    _load_env_file(project_root / ".env")

    return Settings(
        project_root=project_root,
        porcupine_access_key=_env_str("PORCUPINE_ACCESS_KEY", "").strip(),
        porcupine_keyword_path=_env_path(
            "PORCUPINE_KEYWORD_PATH",
            project_root / "models" / "porcupine" / "openclaw_mac.ppn",
        ),
        porcupine_sensitivity=_env_float("PORCUPINE_SENSITIVITY", 0.55),
        audio_input_device=_maybe_int(_env_str("OPENCLAW_AUDIO_INPUT_DEVICE", "")),
        audio_output_device=_maybe_int(_env_str("OPENCLAW_AUDIO_OUTPUT_DEVICE", "")),
        command_sample_rate=_env_int("OPENCLAW_COMMAND_SAMPLE_RATE", 16000),
        record_max_seconds=_env_float("OPENCLAW_RECORD_MAX_SECONDS", 8.0),
        record_min_seconds=_env_float("OPENCLAW_RECORD_MIN_SECONDS", 1.0),
        silence_seconds=_env_float("OPENCLAW_SILENCE_SECONDS", 0.9),
        silence_threshold=_env_float("OPENCLAW_SILENCE_THRESHOLD", 180.0),
        wakeword_start_delay=_env_float("OPENCLAW_WAKEWORD_START_DELAY", 0.4),
        listen_start_prompt=_env_str("OPENCLAW_LISTEN_START_PROMPT", "Listening").strip(),
        wake_hello_prompt=_env_str("OPENCLAW_WAKE_HELLO_PROMPT", "Hi").strip(),
        whisper_model=_env_str("OPENCLAW_WHISPER_MODEL", "small.en"),
        whisper_device=_env_str("OPENCLAW_WHISPER_DEVICE", "cpu"),
        whisper_compute_type=_env_str("OPENCLAW_WHISPER_COMPUTE_TYPE", "int8").strip(),
        whisper_language=_env_str("OPENCLAW_WHISPER_LANGUAGE", "en"),
        whisper_download_root=_env_path(
            "OPENCLAW_WHISPER_DOWNLOAD_ROOT",
            project_root / "models" / "whisper",
        ),
        kokoro_model_path=_env_path(
            "KOKORO_MODEL_PATH",
            project_root / "models" / "kokoro" / "kokoro-v1.0.onnx",
        ),
        kokoro_voices_path=_env_path(
            "KOKORO_VOICES_PATH",
            project_root / "models" / "kokoro" / "voices-v1.0.bin",
        ),
        kokoro_voice=_env_str("KOKORO_VOICE", "af_heart"),
        kokoro_speed=_env_float("KOKORO_SPEED", 1.0),
        kokoro_language=_env_str("KOKORO_LANGUAGE", "en-us"),
        openclaw_rest_url=_env_str(
            "OPENCLAW_REST_URL",
            "http://127.0.0.1:3000/v1/assistant",
        ).strip(),
        openclaw_timeout_seconds=_env_float("OPENCLAW_TIMEOUT_SECONDS", 10.0),
        wakeword_label=_env_str("WAKEWORD_LABEL", "wake word").strip(),
        tts_fade_ms=_env_float("OPENCLAW_TTS_FADE_MS", 20.0),
        tts_padding_ms=_env_float("OPENCLAW_TTS_PADDING_MS", 40.0),
        tts_prewarm_ms=_env_float("OPENCLAW_TTS_PREWARM_MS", 50.0),
    )
