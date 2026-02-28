from __future__ import annotations

from openclaw_assistant.core.context import RuntimeContext


class WakewordListenerPlugin:
    def wait_for_wakeword(
        self,
        context: RuntimeContext,
        timeout_seconds: float | None = None,
    ) -> bool:
        return context.wakeword.wait_for_wakeword(timeout_seconds=timeout_seconds)
