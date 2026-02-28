from __future__ import annotations

from pathlib import Path

import pytest

from openclaw_assistant.config.settings import Settings


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        project_root=tmp_path,
        porcupine_access_key="",
        porcupine_keyword_path=tmp_path / "missing.ppn",
        porcupine_sensitivity=0.5,
        audio_input_device=None,
        audio_output_device=None,
        command_sample_rate=16000,
        record_max_seconds=8.0,
        record_min_seconds=1.0,
        silence_seconds=0.9,
        silence_threshold=180.0,
        wakeword_start_delay=0.4,
        listen_start_prompt="Listening",
        wake_hello_prompt="Hi",
        whisper_model="small.en",
        whisper_device="cpu",
        whisper_compute_type="int8",
        whisper_language="en",
        whisper_download_root=tmp_path,
        kokoro_model_path=tmp_path / "k.onnx",
        kokoro_voices_path=tmp_path / "v.bin",
        kokoro_voice="af_heart",
        kokoro_speed=1.0,
        kokoro_language="en-us",
        openclaw_rest_url="http://127.0.0.1:3000/v1/assistant",
        openclaw_timeout_seconds=10.0,
        wakeword_label="OpenClaw",
        tts_fade_ms=20.0,
        tts_padding_ms=40.0,
        tts_prewarm_ms=50.0,
    )


def test_missing_access_key_raises(tmp_path: Path) -> None:
    s = _settings(tmp_path)
    with pytest.raises(RuntimeError, match="PORCUPINE_ACCESS_KEY"):
        s.validate_runtime_assets()
