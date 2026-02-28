from __future__ import annotations

from openclaw_assistant.app.lifecycle import SignalLifecycle
from openclaw_assistant.app.runner import AppRunner
from openclaw_assistant.config.loader import load_settings
from openclaw_assistant.observability.logging import configure_logging


def run_command() -> None:
    configure_logging()
    settings = load_settings()
    runner = AppRunner(settings)
    SignalLifecycle(runner.stop).install()
    try:
        runner.run()
    finally:
        runner.stop()
