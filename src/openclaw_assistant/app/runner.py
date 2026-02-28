from __future__ import annotations

import logging
import threading

from openclaw_assistant.adapters.audio.input_stream import SilenceBoundedListener
from openclaw_assistant.adapters.gateway.openclaw_http import OpenClawHttpExecutor
from openclaw_assistant.adapters.stt.faster_whisper import FasterWhisperTranscriber
from openclaw_assistant.adapters.tts.kokoro import KokoroSpeaker
from openclaw_assistant.adapters.wakeword.porcupine import PorcupineWakewordDetector
from openclaw_assistant.config.settings import Settings
from openclaw_assistant.core.context import RuntimeContext
from openclaw_assistant.core.pipeline import PipelineOrchestrator
from openclaw_assistant.plugins.registry import PluginRegistry


class AppRunner:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.stop_event = threading.Event()

        speaker = KokoroSpeaker(settings, reuse_output_stream=True)
        self.context = RuntimeContext(
            settings=settings,
            stop_event=self.stop_event,
            wakeword=PorcupineWakewordDetector(settings, stop_event=self.stop_event),
            listener=SilenceBoundedListener(
                sample_rate=settings.command_sample_rate,
                device=settings.audio_input_device,
                record_max_seconds=settings.record_max_seconds,
                record_min_seconds=settings.record_min_seconds,
                silence_seconds=settings.silence_seconds,
                silence_threshold=settings.silence_threshold,
            ),
            transcriber=FasterWhisperTranscriber(settings),
            executor=OpenClawHttpExecutor(settings),
            speaker=speaker,
        )
        self.speaker = speaker
        self.registry = PluginRegistry()
        self.registry.validate()
        self.pipeline = PipelineOrchestrator(self.context, self.registry)

    def stop(self) -> None:
        self.stop_event.set()
        self.speaker.close()

    def run(self) -> None:
        self.settings.validate_runtime_assets(include_tts_assets=True)
        logging.info("Starting OpenClaw Assistant runtime.")
        self.pipeline.run_forever()
