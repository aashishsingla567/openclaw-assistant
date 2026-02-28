from __future__ import annotations

import numpy as np

from openclaw_assistant.core.context import RuntimeContext


class TranscribeStagePlugin:
    def transcribe(self, audio: np.ndarray, context: RuntimeContext) -> str:
        return context.transcriber.transcribe(audio)
