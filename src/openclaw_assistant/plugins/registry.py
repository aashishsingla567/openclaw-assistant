from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

import numpy as np

from openclaw_assistant.core.context import RuntimeContext
from openclaw_assistant.plugins.builtin.action_stage import ActionStagePlugin
from openclaw_assistant.plugins.builtin.listen_stage import ListenStagePlugin
from openclaw_assistant.plugins.builtin.speak_stage import SpeakStagePlugin
from openclaw_assistant.plugins.builtin.transcribe_stage import TranscribeStagePlugin
from openclaw_assistant.plugins.builtin.wakeword_listener import WakewordListenerPlugin

EventHandler = Callable[[object, RuntimeContext], None]


class WakewordListenerStage(Protocol):
    def wait_for_wakeword(
        self,
        context: RuntimeContext,
        timeout_seconds: float | None = None,
    ) -> bool: ...


class ListenStage(Protocol):
    def capture_audio(self, context: RuntimeContext) -> np.ndarray: ...


class TranscribeStage(Protocol):
    def transcribe(self, audio: np.ndarray, context: RuntimeContext) -> str: ...


class ActionStage(Protocol):
    def execute(self, prompt: str, context: RuntimeContext) -> str: ...


class SpeakStage(Protocol):
    def speak(self, response: str, context: RuntimeContext) -> None: ...


@dataclass
class PluginRegistry:
    wakeword_listener: WakewordListenerStage = field(default_factory=WakewordListenerPlugin)
    listen_stage: ListenStage = field(default_factory=ListenStagePlugin)
    transcribe_stage: TranscribeStage = field(default_factory=TranscribeStagePlugin)
    action_stage: ActionStage = field(default_factory=ActionStagePlugin)
    speak_stage: SpeakStage = field(default_factory=SpeakStagePlugin)
    _handlers: list[EventHandler] = field(default_factory=list)

    def register_event_handler(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    def emit(self, event: object, context: RuntimeContext) -> None:
        for handler in self._handlers:
            handler(event, context)

    def validate(self) -> None:
        required = {
            "wakeword_listener": ("wait_for_wakeword",),
            "listen_stage": ("capture_audio",),
            "transcribe_stage": ("transcribe",),
            "action_stage": ("execute",),
            "speak_stage": ("speak",),
        }
        for attr, methods in required.items():
            plugin = getattr(self, attr)
            for method in methods:
                if not hasattr(plugin, method):
                    raise TypeError(f"Plugin '{attr}' is missing method '{method}'")
