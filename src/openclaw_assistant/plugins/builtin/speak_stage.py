from __future__ import annotations

from openclaw_assistant.core.context import RuntimeContext


class SpeakStagePlugin:
    def speak(self, response: str, context: RuntimeContext) -> None:
        context.speaker.speak(response)
