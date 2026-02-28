from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from openclaw_assistant.adapters.tts.kokoro import KokoroSpeaker  # noqa: E402
from openclaw_assistant.config.settings import Settings  # noqa: E402


@dataclass(frozen=True)
class TTSPipeline:
    _speaker: KokoroSpeaker

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        *,
        reuse_output_stream: bool = True,
    ) -> TTSPipeline:
        return cls(_speaker=KokoroSpeaker(settings, reuse_output_stream=reuse_output_stream))

    def speak(self, text: str) -> None:
        self._speaker.speak(text)

    def close(self) -> None:
        self._speaker.close()
