from __future__ import annotations

import signal
from collections.abc import Callable


class SignalLifecycle:
    def __init__(self, stop: Callable[[], None]) -> None:
        self.stop = stop

    def install(self) -> None:
        def _handle(signum: int, _frame: object) -> None:
            self.stop()

        signal.signal(signal.SIGINT, _handle)
        signal.signal(signal.SIGTERM, _handle)
