#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="Run in foreground with logs")
    args = parser.parse_args()

    dev_mode = args.dev or os.getenv("OPENCLAW_DEV", "").strip() == "1"

    os.chdir(REPO_DIR)
    run(["git", "pull"])
    run(["uv", "sync"])

    run([
        "/usr/bin/env",
        "bash",
        "-lc",
        "launchctl unload ~/Library/LaunchAgents/com.openclaw.assistant.plist 2>/dev/null || true",
    ])

    if dev_mode:
        print("Dev mode: starting assistant in foreground with logs.")
        run([
            "/usr/bin/env",
            "bash",
            "-lc",
            "set -a && source .env && set +a && uv run openclaw run",
        ])
        return

    run([
        "/usr/bin/env",
        "bash",
        "-lc",
        "launchctl load ~/Library/LaunchAgents/com.openclaw.assistant.plist",
    ])
    print("Updated and reloaded launchd service.")


if __name__ == "__main__":
    main()
