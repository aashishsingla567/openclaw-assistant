from __future__ import annotations

from typing import Any, cast

import numpy as np
import sounddevice as sd


class AudioInput:
    @staticmethod
    def list_devices() -> list[dict[str, Any]]:
        return cast(list[dict[str, Any]], sd.query_devices())

    @staticmethod
    def record_fixed_seconds(
        seconds: float,
        sample_rate: int,
        device: str | int | None,
    ) -> np.ndarray:
        frames = int(seconds * sample_rate)
        audio = sd.rec(frames, samplerate=sample_rate, channels=1, dtype="int16", device=device)
        sd.wait()
        return cast(np.ndarray, audio.squeeze().astype(np.float32) / 32768.0)

    @staticmethod
    def record_silence_bounded(
        *,
        sample_rate: int,
        device: str | int | None,
        record_max_seconds: float,
        record_min_seconds: float,
        silence_seconds: float,
        silence_threshold: float,
    ) -> np.ndarray:
        chunk_seconds = 0.1
        frames_per_chunk = int(sample_rate * chunk_seconds)
        max_chunks = int(record_max_seconds / chunk_seconds)
        min_chunks = max(1, int(record_min_seconds / chunk_seconds))
        silent_limit = max(1, int(silence_seconds / chunk_seconds))

        chunks: list[np.ndarray] = []
        silent_chunks = 0

        with sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
            blocksize=frames_per_chunk,
            device=device,
        ) as stream:
            for index in range(max_chunks):
                frames, _ = stream.read(frames_per_chunk)
                pcm = np.asarray(frames[:, 0], dtype=np.int16)
                chunks.append(pcm)

                rms = float(np.sqrt(np.mean(np.square(pcm.astype(np.float32)))))
                if rms < silence_threshold:
                    silent_chunks += 1
                else:
                    silent_chunks = 0

                if index + 1 >= min_chunks and silent_chunks >= silent_limit:
                    break

        if not chunks:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(chunks).astype(np.float32) / 32768.0


class SilenceBoundedListener:
    def __init__(
        self,
        *,
        sample_rate: int,
        device: str | int | None,
        record_max_seconds: float,
        record_min_seconds: float,
        silence_seconds: float,
        silence_threshold: float,
    ) -> None:
        self.sample_rate = sample_rate
        self.device = device
        self.record_max_seconds = record_max_seconds
        self.record_min_seconds = record_min_seconds
        self.silence_seconds = silence_seconds
        self.silence_threshold = silence_threshold

    def record_command_audio(self) -> np.ndarray:
        return AudioInput.record_silence_bounded(
            sample_rate=self.sample_rate,
            device=self.device,
            record_max_seconds=self.record_max_seconds,
            record_min_seconds=self.record_min_seconds,
            silence_seconds=self.silence_seconds,
            silence_threshold=self.silence_threshold,
        )
