from __future__ import annotations

import argparse

from openclaw_assistant.commands import diagnostics
from openclaw_assistant.commands.run import run_command
from openclaw_assistant.commands.setup import setup_command
from openclaw_assistant.commands.update import update_command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openclaw")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run assistant")
    run.set_defaults(handler=lambda _args: run_command())

    setup = subparsers.add_parser("setup", help="Run onboarding setup")
    setup.set_defaults(handler=lambda _args: setup_command())

    update = subparsers.add_parser("update", help="Update + reload")
    update.add_argument("--dev", action="store_true", help="Run in foreground with logs")
    update.set_defaults(handler=lambda args: update_command(dev=args.dev))

    diagnostics.add_subparser(subparsers)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.handler(args)
