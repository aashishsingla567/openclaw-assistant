from __future__ import annotations

import threading
from dataclasses import dataclass

import numpy as np

from openclaw_assistant.core.context import RuntimeContext
from openclaw_assistant.core.pipeline import PipelineOrchestrator
from openclaw_assistant.plugins.registry import PluginRegistry


@dataclass
class _S:
    wakeword_label: str = "OpenClaw"
    listen_start_prompt: str = "Listening"
    wake_hello_prompt: str = "Hi"
    wakeword_start_delay: float = 0.0


class _Wake:
    def audio_params(self):
        return (16000, 512)

    def wait_for_wakeword(self, timeout_seconds=None):
        return True


class _Listener:
    def record_command_audio(self):
        return np.zeros(10, dtype=np.float32)


class _Transcriber:
    def transcribe(self, _audio):
        return ""


class _Executor:
    def execute(self, _prompt: str):
        return "unused"


class _Speaker:
    def speak(self, _text: str):
        return None


def test_pipeline_returns_empty_when_no_transcription() -> None:
    context = RuntimeContext(
        settings=_S(),
        stop_event=threading.Event(),
        wakeword=_Wake(),
        listener=_Listener(),
        transcriber=_Transcriber(),
        executor=_Executor(),
        speaker=_Speaker(),
    )
    orchestrator = PipelineOrchestrator(context, PluginRegistry())
    assert orchestrator.run_once_after_wake() == ""
