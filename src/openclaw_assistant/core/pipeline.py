from __future__ import annotations

import logging
from collections.abc import Iterable

from openclaw_assistant.core.context import RuntimeContext
from openclaw_assistant.core.events import (
    ActionCompleted,
    AudioCaptured,
    ListenStarted,
    PipelineError,
    ResponseSpoken,
    TextTranscribed,
    WakeDetected,
)
from openclaw_assistant.plugins.registry import PluginRegistry


class PipelineOrchestrator:
    def __init__(self, context: RuntimeContext, registry: PluginRegistry) -> None:
        self.context = context
        self.registry = registry

    def _emit(self, event: object) -> None:
        self.registry.emit(event, self.context)

    def run_once_after_wake(self) -> str:
        self._emit(WakeDetected(label=self.context.settings.wakeword_label))
        self._emit(ListenStarted(prompt=self.context.settings.listen_start_prompt))

        audio = self.registry.listen_stage.capture_audio(self.context)
        self._emit(AudioCaptured(sample_count=audio.size, audio=audio))

        text = self.registry.transcribe_stage.transcribe(audio, self.context).strip()
        self._emit(TextTranscribed(text=text))
        if not text:
            return ""

        response = self.registry.action_stage.execute(text, self.context)
        self._emit(ActionCompleted(prompt=text, response=response))

        if response:
            self.registry.speak_stage.speak(response, self.context)
            self._emit(ResponseSpoken(response=response))
        return text

    def run_forever(self) -> None:
        sample_rate, frame_length = self.context.wakeword.audio_params()
        logging.info(
            "Wake loop started for '%s' at %d Hz with frame length %d",
            self.context.settings.wakeword_label,
            sample_rate,
            frame_length,
        )
        while not self.context.stop_event.is_set():
            detected = self.registry.wakeword_listener.wait_for_wakeword(
                self.context,
                timeout_seconds=None,
            )
            if not detected:
                continue
            logging.info("Wake word detected.")
            try:
                text = self.run_once_after_wake()
                if not text:
                    logging.info("No speech detected after wake word.")
            except Exception as error:
                self._emit(PipelineError(stage="run_once_after_wake", error=str(error)))
                logging.exception("Pipeline cycle failed: %s", error)

    def run_events(self) -> Iterable[object]:
        events: list[object] = []

        def _capture(event: object, _context: RuntimeContext) -> None:
            events.append(event)

        self.registry.register_event_handler(_capture)
        self.run_once_after_wake()
        return events
