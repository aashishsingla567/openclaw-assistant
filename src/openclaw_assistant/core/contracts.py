from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


class WakewordDetector(Protocol):
    def audio_params(self) -> tuple[int, int]: ...

    def wait_for_wakeword(self, timeout_seconds: float | None = None) -> bool: ...


class Listener(Protocol):
    def record_command_audio(self) -> np.ndarray: ...


class Transcriber(Protocol):
    def transcribe(self, audio: np.ndarray) -> str: ...


class ActionExecutor(Protocol):
    def execute(self, prompt: str) -> str: ...


class Speaker(Protocol):
    def speak(self, text: str) -> None: ...


@dataclass(frozen=True)
class ActionResult:
    prompt: str
    response: str
