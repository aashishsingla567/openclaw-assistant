from __future__ import annotations

from openclaw_assistant.core.context import RuntimeContext


class ActionStagePlugin:
    def execute(self, prompt: str, context: RuntimeContext) -> str:
        return context.executor.execute(prompt)
