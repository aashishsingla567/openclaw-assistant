from __future__ import annotations

import threading
import time
from typing import Any

import numpy as np
import pvporcupine
import sounddevice as sd

from openclaw_assistant.config.settings import Settings


class PorcupineWakewordDetector:
    def __init__(self, settings: Settings, stop_event: threading.Event) -> None:
        self.settings = settings
        self.stop_event = stop_event

    def _create(self) -> Any:
        return pvporcupine.create(
            access_key=self.settings.porcupine_access_key,
            keyword_paths=[str(self.settings.porcupine_keyword_path)],
            sensitivities=[self.settings.porcupine_sensitivity],
        )

    def audio_params(self) -> tuple[int, int]:
        detector = self._create()
        try:
            return detector.sample_rate, detector.frame_length
        finally:
            detector.delete()

    def wait_for_wakeword(self, timeout_seconds: float | None = None) -> bool:
        detector = self._create()
        deadline = None if timeout_seconds is None else (time.monotonic() + timeout_seconds)
        try:
            with sd.RawInputStream(
                samplerate=detector.sample_rate,
                blocksize=detector.frame_length,
                dtype="int16",
                channels=1,
                device=self.settings.audio_input_device,
            ) as stream:
                while not self.stop_event.is_set():
                    if deadline is not None and time.monotonic() >= deadline:
                        return False
                    pcm_bytes, _ = stream.read(detector.frame_length)
                    pcm = np.frombuffer(pcm_bytes, dtype=np.int16)
                    if detector.process(pcm) >= 0:
                        return True
                return False
        finally:
            detector.delete()
