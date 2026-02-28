from __future__ import annotations

import os
from pathlib import Path

from .settings import Settings


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


def load_settings(project_root: Path | None = None) -> Settings:
    root = project_root or Path(__file__).resolve().parents[3]
    _load_env_file(root / ".env")

    return Settings(
        project_root=root,
        porcupine_access_key=_env_str("PORCUPINE_ACCESS_KEY", "").strip(),
        porcupine_keyword_path=_env_path(
            "PORCUPINE_KEYWORD_PATH",
            root / "models" / "porcupine" / "openclaw_mac.ppn",
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
            root / "models" / "whisper",
        ),
        kokoro_model_path=_env_path(
            "KOKORO_MODEL_PATH",
            root / "models" / "kokoro" / "kokoro-v1.0.onnx",
        ),
        kokoro_voices_path=_env_path(
            "KOKORO_VOICES_PATH",
            root / "models" / "kokoro" / "voices-v1.0.bin",
        ),
        kokoro_voice=_env_str("KOKORO_VOICE", "af_heart"),
        kokoro_speed=_env_float("KOKORO_SPEED", 1.0),
        kokoro_language=_env_str("KOKORO_LANGUAGE", "en-us"),
        openclaw_rest_url=_env_str("OPENCLAW_REST_URL", "http://127.0.0.1:3000/v1/assistant").strip(),
        openclaw_timeout_seconds=_env_float("OPENCLAW_TIMEOUT_SECONDS", 10.0),
        wakeword_label=_env_str("WAKEWORD_LABEL", "wake word").strip(),
        tts_fade_ms=_env_float("OPENCLAW_TTS_FADE_MS", 20.0),
        tts_padding_ms=_env_float("OPENCLAW_TTS_PADDING_MS", 40.0),
        tts_prewarm_ms=_env_float("OPENCLAW_TTS_PREWARM_MS", 50.0),
    )
