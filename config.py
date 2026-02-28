from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from openclaw_assistant.config.loader import load_settings  # noqa: E402
from openclaw_assistant.config.settings import (  # noqa: E402
    KokoroConfig,
    Settings,
    TTSPlaybackConfig,
)

__all__ = ["Settings", "KokoroConfig", "TTSPlaybackConfig", "load_settings"]
