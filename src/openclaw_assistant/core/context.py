from __future__ import annotations

import threading
from dataclasses import dataclass

from openclaw_assistant.config.settings import Settings
from openclaw_assistant.core.contracts import (
    ActionExecutor,
    Listener,
    Speaker,
    Transcriber,
    WakewordDetector,
)


@dataclass
class RuntimeContext:
    settings: Settings
    stop_event: threading.Event
    wakeword: WakewordDetector
    listener: Listener
    transcriber: Transcriber
    executor: ActionExecutor
    speaker: Speaker
