from __future__ import annotations

import sounddevice as sd


class AudioOutput:
    @staticmethod
    def create_stream(sample_rate: int, device: str | int | None) -> sd.OutputStream:
        stream = sd.OutputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
            device=device,
        )
        stream.start()
        return stream
