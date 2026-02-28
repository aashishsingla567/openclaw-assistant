from __future__ import annotations

import threading
from dataclasses import dataclass

import numpy as np

from openclaw_assistant.core.context import RuntimeContext
from openclaw_assistant.core.events import (
    ActionCompleted,
    AudioCaptured,
    ListenStarted,
    ResponseSpoken,
    TextTranscribed,
    WakeDetected,
)
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
        return np.array([0.1, 0.2], dtype=np.float32)


class _Transcriber:
    def transcribe(self, _audio):
        return "hello"


class _Executor:
    def execute(self, prompt: str):
        return f"ok:{prompt}"


class _Speaker:
    def speak(self, _text: str):
        return None


def test_pipeline_event_sequence() -> None:
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
    events = list(orchestrator.run_events())

    assert isinstance(events[0], WakeDetected)
    assert isinstance(events[1], ListenStarted)
    assert isinstance(events[2], AudioCaptured)
    assert isinstance(events[3], TextTranscribed)
    assert isinstance(events[4], ActionCompleted)
    assert isinstance(events[5], ResponseSpoken)
