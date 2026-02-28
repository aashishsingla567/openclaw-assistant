from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class WakeDetected:
    label: str


@dataclass(frozen=True)
class ListenStarted:
    prompt: str


@dataclass(frozen=True)
class AudioCaptured:
    sample_count: int
    audio: np.ndarray


@dataclass(frozen=True)
class TextTranscribed:
    text: str


@dataclass(frozen=True)
class ActionCompleted:
    prompt: str
    response: str


@dataclass(frozen=True)
class ResponseSpoken:
    response: str


@dataclass(frozen=True)
class PipelineError:
    stage: str
    error: str
