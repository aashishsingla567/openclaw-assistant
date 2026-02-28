from __future__ import annotations

import logging
import signal
import threading
from dataclasses import dataclass

import numpy as np
import pvporcupine
import requests
import sounddevice as sd
from faster_whisper import WhisperModel

from config import Settings, load_settings
from tts_pipeline import TTSPipeline


@dataclass(frozen=True)
class WakeResult:
    text: str
    response: str


class OpenClawAssistant:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.stop_event = threading.Event()
        self.pipeline_lock = threading.Lock()
        self.whisper = WhisperModel(
            settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
            download_root=str(settings.whisper_download_root),
        )
        self.tts = TTSPipeline.from_settings(self.settings, reuse_output_stream=True)

    def stop(self) -> None:
        self.stop_event.set()
        self.tts.close()

    def _require_files(self) -> None:
        if not self.settings.porcupine_access_key:
            raise RuntimeError(
                "Missing PORCUPINE_ACCESS_KEY. Set it in your shell environment."
            )
        if not self.settings.porcupine_keyword_path.exists():
            raise RuntimeError(
                f"Missing wake-word model: {self.settings.porcupine_keyword_path}"
            )
        if not self.settings.kokoro_model_path.exists():
            raise RuntimeError(f"Missing Kokoro model: {self.settings.kokoro_model_path}")
        if not self.settings.kokoro_voices_path.exists():
            raise RuntimeError(f"Missing Kokoro voices: {self.settings.kokoro_voices_path}")

    def _speak(self, text: str) -> None:
        self.tts.speak(text)

    def _record_command_audio(self) -> np.ndarray:
        chunk_seconds = 0.1
        frames_per_chunk = int(self.settings.command_sample_rate * chunk_seconds)
        max_chunks = int(self.settings.record_max_seconds / chunk_seconds)
        min_chunks = max(1, int(self.settings.record_min_seconds / chunk_seconds))
        silent_limit = max(1, int(self.settings.silence_seconds / chunk_seconds))

        chunks: list[np.ndarray] = []
        silent_chunks = 0

        with sd.InputStream(
            samplerate=self.settings.command_sample_rate,
            channels=1,
            dtype="int16",
            blocksize=frames_per_chunk,
            device=self.settings.audio_input_device,
        ) as stream:
            for index in range(max_chunks):
                if self.stop_event.is_set():
                    break
                frames, _ = stream.read(frames_per_chunk)
                pcm = np.asarray(frames[:, 0], dtype=np.int16)
                chunks.append(pcm)

                rms = float(np.sqrt(np.mean(np.square(pcm.astype(np.float32)))))
                if rms < self.settings.silence_threshold:
                    silent_chunks += 1
                else:
                    silent_chunks = 0

                if index + 1 >= min_chunks and silent_chunks >= silent_limit:
                    break

        if not chunks:
            return np.zeros(0, dtype=np.float32)
        merged = np.concatenate(chunks).astype(np.float32) / 32768.0
        return merged

    def _speak_prompt(self, text: str) -> None:
        if not text:
            return
        try:
            self._speak(text)
        except Exception as error:
            logging.warning("TTS prompt failed: %s", error)

    def _transcribe(self, audio: np.ndarray) -> str:
        if audio.size == 0:
            return ""
        segments, _ = self.whisper.transcribe(
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

    @staticmethod
    def _extract_response(payload: dict, fallback_text: str = "") -> str:
        for key in ("response", "reply", "text", "message", "output"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return fallback_text.strip()

    def _gateway_http(self, prompt: str) -> str:
        response = requests.post(
            self.settings.openclaw_rest_url,
            json={"text": prompt},
            timeout=self.settings.openclaw_timeout_seconds,
        )
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type.lower():
            payload = response.json()
            if isinstance(payload, dict):
                return self._extract_response(payload)
        return response.text.strip()

    def _process_prompt(self, prompt: str) -> WakeResult:
        prompt = prompt.strip()
        if not prompt:
            return WakeResult(text=prompt, response="")
        with self.pipeline_lock:
            logging.info("Handling prompt: %s", prompt)
            response = self._gateway_http(prompt=prompt)
            if response:
                self._speak(response)
            return WakeResult(text=prompt, response=response)

    def _run_wake_loop(self) -> None:
        porcupine = pvporcupine.create(
            access_key=self.settings.porcupine_access_key,
            keyword_paths=[str(self.settings.porcupine_keyword_path)],
            sensitivities=[self.settings.porcupine_sensitivity],
        )
        logging.info(
            "Wake loop started for '%s' at %d Hz with frame length %d",
            self.settings.wakeword_label,
            porcupine.sample_rate,
            porcupine.frame_length,
        )
        try:
            with sd.RawInputStream(
                samplerate=porcupine.sample_rate,
                blocksize=porcupine.frame_length,
                dtype="int16",
                channels=1,
                device=self.settings.audio_input_device,
            ) as stream:
                while not self.stop_event.is_set():
                    pcm_bytes, _ = stream.read(porcupine.frame_length)
                    pcm = np.frombuffer(pcm_bytes, dtype=np.int16)
                    if porcupine.process(pcm) >= 0:
                        logging.info("Wake word detected.")
                        self._speak_prompt(self.settings.wake_hello_prompt)
                        self._speak_prompt(self.settings.listen_start_prompt)
                        if self.settings.wakeword_start_delay > 0:
                            self.stop_event.wait(self.settings.wakeword_start_delay)
                        audio = self._record_command_audio()
                        text = self._transcribe(audio)
                        if text:
                            self._process_prompt(prompt=text)
                        else:
                            logging.info("No speech detected after wake word.")
        finally:
            porcupine.delete()

    def run(self) -> None:
        self._require_files()
        self._run_wake_loop()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    settings = load_settings()
    assistant = OpenClawAssistant(settings)

    def _handle_stop(signum: int, _frame: object) -> None:
        logging.info("Received signal %d. Stopping.", signum)
        assistant.stop()

    signal.signal(signal.SIGINT, _handle_stop)
    signal.signal(signal.SIGTERM, _handle_stop)

    try:
        assistant.run()
    except KeyboardInterrupt:
        assistant.stop()
    except Exception:
        logging.exception("Assistant exited with error.")
        raise


if __name__ == "__main__":
    main()
