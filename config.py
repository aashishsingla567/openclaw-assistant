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
    beep_frequency_hz: float
    beep_duration_seconds: float
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


def load_settings() -> Settings:
    project_root = Path(__file__).resolve().parent

    return Settings(
        project_root=project_root,
        porcupine_access_key=os.getenv("PORCUPINE_ACCESS_KEY", "").strip(),
        porcupine_keyword_path=Path(
            os.getenv(
                "PORCUPINE_KEYWORD_PATH",
                project_root / "models" / "porcupine" / "openclaw_mac.ppn",
            )
        ).expanduser(),
        porcupine_sensitivity=_env_float("PORCUPINE_SENSITIVITY", 0.55),
        audio_input_device=_maybe_int(os.getenv("OPENCLAW_AUDIO_INPUT_DEVICE")),
        audio_output_device=_maybe_int(os.getenv("OPENCLAW_AUDIO_OUTPUT_DEVICE")),
        command_sample_rate=_env_int("OPENCLAW_COMMAND_SAMPLE_RATE", 16000),
        record_max_seconds=_env_float("OPENCLAW_RECORD_MAX_SECONDS", 8.0),
        record_min_seconds=_env_float("OPENCLAW_RECORD_MIN_SECONDS", 1.0),
        silence_seconds=_env_float("OPENCLAW_SILENCE_SECONDS", 0.9),
        silence_threshold=_env_float("OPENCLAW_SILENCE_THRESHOLD", 180.0),
        wakeword_start_delay=_env_float("OPENCLAW_WAKEWORD_START_DELAY", 0.4),
        beep_frequency_hz=_env_float("OPENCLAW_BEEP_FREQUENCY_HZ", 880.0),
        beep_duration_seconds=_env_float("OPENCLAW_BEEP_DURATION_SECONDS", 0.12),
        whisper_model=os.getenv("OPENCLAW_WHISPER_MODEL", "small.en"),
        whisper_device=os.getenv("OPENCLAW_WHISPER_DEVICE", "cpu"),
        whisper_compute_type=os.getenv(
            "OPENCLAW_WHISPER_COMPUTE_TYPE", "int8"
        ).strip(),
        whisper_language=os.getenv("OPENCLAW_WHISPER_LANGUAGE", "en"),
        whisper_download_root=Path(
            os.getenv(
                "OPENCLAW_WHISPER_DOWNLOAD_ROOT",
                project_root / "models" / "whisper",
            )
        ).expanduser(),
        kokoro_model_path=Path(
            os.getenv(
                "KOKORO_MODEL_PATH",
                project_root / "models" / "kokoro" / "kokoro-v1.0.onnx",
            )
        ).expanduser(),
        kokoro_voices_path=Path(
            os.getenv(
                "KOKORO_VOICES_PATH",
                project_root / "models" / "kokoro" / "voices-v1.0.bin",
            )
        ).expanduser(),
        kokoro_voice=os.getenv("KOKORO_VOICE", "af_heart"),
        kokoro_speed=_env_float("KOKORO_SPEED", 1.0),
        kokoro_language=os.getenv("KOKORO_LANGUAGE", "en-us"),
        openclaw_rest_url=os.getenv(
            "OPENCLAW_REST_URL", "http://127.0.0.1:3000/v1/assistant"
        ).strip(),
        openclaw_timeout_seconds=_env_float("OPENCLAW_TIMEOUT_SECONDS", 10.0),
        wakeword_label=os.getenv("WAKEWORD_LABEL", "wake word").strip(),
    )
