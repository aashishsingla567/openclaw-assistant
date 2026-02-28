from __future__ import annotations

import numpy as np
from faster_whisper import WhisperModel

from openclaw_assistant.config.settings import Settings


class FasterWhisperTranscriber:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model = WhisperModel(
            settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
            download_root=str(settings.whisper_download_root),
        )

    def transcribe(self, audio: np.ndarray) -> str:
        if audio.size == 0:
            return ""
        segments, _ = self.model.transcribe(
            audio,
            language=self.settings.whisper_language,
            beam_size=1,
            best_of=1,
            temperature=0.0,
            condition_on_previous_text=False,
            vad_filter=True,
        )
        text_parts = [segment.text.strip() for segment in segments if segment.text.strip()]
        return " ".join(text_parts).strip()
