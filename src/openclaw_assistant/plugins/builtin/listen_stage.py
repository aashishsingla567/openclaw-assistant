from __future__ import annotations

import numpy as np

from openclaw_assistant.core.context import RuntimeContext


class ListenStagePlugin:
    def capture_audio(self, context: RuntimeContext) -> np.ndarray:
        if context.settings.wake_hello_prompt:
            context.speaker.speak(context.settings.wake_hello_prompt)
        if context.settings.listen_start_prompt:
            context.speaker.speak(context.settings.listen_start_prompt)
        if context.settings.wakeword_start_delay > 0:
            context.stop_event.wait(context.settings.wakeword_start_delay)
        return context.listener.record_command_audio()
