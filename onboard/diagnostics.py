#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from openclaw_assistant.commands import main as openclaw_main  # noqa: E402


def _run(args: list[str]) -> None:
    argv = ["openclaw", *args]
    old = sys.argv
    try:
        sys.argv = argv
        openclaw_main()
    finally:
        sys.argv = old


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-devices", action="store_true")
    parser.add_argument("--tts", action="store_true")
    parser.add_argument("--stt", action="store_true")
    parser.add_argument("--openclaw", action="store_true")
    parser.add_argument("--wakeword", action="store_true")
    parser.add_argument("--wakeword-pipeline", action="store_true")
    parser.add_argument("--wakeword-pipeline-openclaw", action="store_true")
    parser.add_argument("--text", default="Testing text to speech.")
    parser.add_argument("--seconds", type=float, default=3.0)
    parser.add_argument("--wakeword-timeout", type=float, default=10.0)
    args = parser.parse_args()

    if args.list_devices:
        _run(["diagnostics", "devices"])
        return
    if args.tts:
        _run(["diagnostics", "tts", "--text", args.text])
    if args.stt:
        _run(["diagnostics", "stt", "--seconds", str(args.seconds)])
    if args.openclaw:
        _run(["diagnostics", "openclaw", "--text", args.text])
    if args.wakeword:
        _run(["diagnostics", "wakeword", "--timeout", str(args.wakeword_timeout)])
    if args.wakeword_pipeline:
        _run(["diagnostics", "pipeline", "--timeout", str(args.wakeword_timeout)])
    if args.wakeword_pipeline_openclaw:
        _run(["diagnostics", "pipeline", "--timeout", str(args.wakeword_timeout), "--openclaw"])

    if not (
        args.tts
        or args.stt
        or args.openclaw
        or args.wakeword
        or args.wakeword_pipeline
        or args.wakeword_pipeline_openclaw
        or args.list_devices
    ):
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
