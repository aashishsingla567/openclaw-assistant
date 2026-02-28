#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    os.chdir(REPO_DIR)
    run(["git", "pull"])
    run(["uv", "sync"])
    run([
        "/usr/bin/env",
        "bash",
        "-lc",
        "launchctl unload ~/Library/LaunchAgents/com.openclaw.assistant.plist 2>/dev/null || true",
    ])
    run([
        "/usr/bin/env",
        "bash",
        "-lc",
        "launchctl load ~/Library/LaunchAgents/com.openclaw.assistant.plist",
    ])
    print("Updated and reloaded launchd service.")


if __name__ == "__main__":
    main()
