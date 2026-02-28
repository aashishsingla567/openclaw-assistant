#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

REPO_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Step:
    name: str
    action: Callable[[], None]


def info(msg: str) -> None:
    print(f"\n==> {msg}")


def err(msg: str) -> None:
    print(f"\nERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd: list[str], check: bool = True) -> None:
    subprocess.run(cmd, check=check)


def require_cmd(name: str, install_hint: str) -> None:
    result = subprocess.call(["/usr/bin/env", "bash", "-lc", f"command -v {name} >/dev/null 2>&1"])
    if result != 0:
        err(f"{name} is required. {install_hint}")


def open_required_sites() -> None:
    try:
        run(["open", "https://console.picovoice.ai/"])
    except Exception:
        pass


def install_system_deps() -> None:
    run(["brew", "install", "portaudio", "libsndfile", "espeak-ng", "git-lfs"])


def sync_python_deps() -> None:
    os.chdir(REPO_DIR)
    run(["uv", "sync"])


def create_directories() -> None:
    (REPO_DIR / "models" / "kokoro").mkdir(parents=True, exist_ok=True)
    (REPO_DIR / "models" / "porcupine").mkdir(parents=True, exist_ok=True)
    (REPO_DIR / "models" / "whisper").mkdir(parents=True, exist_ok=True)
    (REPO_DIR / "launchd").mkdir(parents=True, exist_ok=True)


def download_kokoro_models() -> None:
    kokoro_model = REPO_DIR / "models" / "kokoro" / "kokoro-v1.0.onnx"
    kokoro_voices = REPO_DIR / "models" / "kokoro" / "voices-v1.0.bin"

    if not kokoro_model.exists():
        run([
            "curl",
            "-L",
            "-o",
            str(kokoro_model),
            "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
        ])
    if not kokoro_voices.exists():
        run([
            "curl",
            "-L",
            "-o",
            str(kokoro_voices),
            "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
        ])


def prepare_env() -> None:
    env_path = REPO_DIR / ".env"
    if not env_path.exists():
        env_example = REPO_DIR / ".env.example"
        if not env_example.exists():
            err(".env.example not found")
        env_path.write_text(env_example.read_text())

    porcupine_key = input("Paste PORCUPINE_ACCESS_KEY: ").strip()
    if not porcupine_key:
        err("PORCUPINE_ACCESS_KEY is required")

    lines = env_path.read_text().splitlines()
    updated = False
    new_lines = []
    for line in lines:
        if line.startswith("PORCUPINE_ACCESS_KEY="):
            new_lines.append(f"PORCUPINE_ACCESS_KEY={porcupine_key}")
            updated = True
        else:
            new_lines.append(line)
    if not updated:
        new_lines.append(f"PORCUPINE_ACCESS_KEY={porcupine_key}")
    env_path.write_text("\n".join(new_lines) + "\n")


def select_wakeword_file() -> None:
    target = REPO_DIR / "models" / "porcupine" / "openclaw_mac.ppn"
    info("Select your Porcupine .ppn wake word file")
    try:
        result = subprocess.run(
            [
                "osascript",
                "-e",
                "POSIX path of (choose file with prompt \"Select your .ppn wake word file\")",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        source_path = result.stdout.strip()
        if not source_path:
            err("No file selected")
        source = Path(source_path)
        if source.suffix.lower() != ".ppn":
            err("Selected file is not a .ppn file")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    except subprocess.CalledProcessError:
        err("File selection cancelled or failed")


def run_assistant() -> None:
    info("Starting assistant")
    run(["/usr/bin/env", "bash", "-lc", "set -a && source .env && set +a && uv run python assistant.py"])


def print_next_steps() -> None:
    print(
        "\nPlace your Porcupine wake word model at:\n"
        "  ./models/porcupine/openclaw_mac.ppn\n\n"
        "Generate it here:\n"
        "  https://console.picovoice.ai/\n\n"
        "Next steps:\n"
        "1) Run:  set -a && source .env && set +a\n"
        "2) Start: uv run python assistant.py\n"
        "3) (Optional) Install launchd:\n"
        "   sed \"s#__REPO_PATH__#$(pwd)#g\" launchd/com.openclaw.assistant.plist > /tmp/com.openclaw.assistant.plist\n"
        "   cp /tmp/com.openclaw.assistant.plist ~/Library/LaunchAgents/com.openclaw.assistant.plist\n"
        "   launchctl unload ~/Library/LaunchAgents/com.openclaw.assistant.plist 2>/dev/null || true\n"
        "   launchctl load ~/Library/LaunchAgents/com.openclaw.assistant.plist\n"
    )


def run_steps(steps: Iterable[Step]) -> None:
    for step in steps:
        info(step.name)
        step.action()


def main() -> None:
    require_cmd("brew", "Install from https://brew.sh")
    require_cmd("uv", "Install from https://astral.sh/uv")

    steps = [
        Step("Opening required sites", open_required_sites),
        Step("Installing system dependencies", install_system_deps),
        Step("Syncing Python dependencies", sync_python_deps),
        Step("Creating directories", create_directories),
        Step("Downloading Kokoro models", download_kokoro_models),
        Step("Preparing .env", prepare_env),
        Step("Selecting wake word file", select_wakeword_file),
        Step("Starting assistant", run_assistant),
    ]

    run_steps(steps)


if __name__ == "__main__":
    main()
