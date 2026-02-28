#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]


def info(msg: str) -> None:
    print(f"\n==> {msg}")


def err(msg: str) -> None:
    print(f"\nERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd: list[str], check: bool = True) -> None:
    subprocess.run(cmd, check=check)


def require_cmd(name: str, install_hint: str) -> None:
    if subprocess.call(["/usr/bin/env", "bash", "-lc", f"command -v {name} >/dev/null 2>&1"]) != 0:
        err(f"{name} is required. {install_hint}")


def main() -> None:
    require_cmd("brew", "Install from https://brew.sh")
    require_cmd("uv", "Install from https://astral.sh/uv")

    info("Opening required sites")
    try:
        run(["open", "https://console.picovoice.ai/"])  # macOS
    except Exception:
        pass

    info("Installing system dependencies")
    run(["brew", "install", "portaudio", "libsndfile", "espeak-ng", "git-lfs"])

    info("Syncing Python dependencies")
    os.chdir(REPO_DIR)
    run(["uv", "sync"])

    info("Creating directories")
    (REPO_DIR / "models" / "kokoro").mkdir(parents=True, exist_ok=True)
    (REPO_DIR / "models" / "porcupine").mkdir(parents=True, exist_ok=True)
    (REPO_DIR / "models" / "whisper").mkdir(parents=True, exist_ok=True)
    (REPO_DIR / "launchd").mkdir(parents=True, exist_ok=True)

    info("Downloading Kokoro models")
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

    info("Preparing .env")
    env_path = REPO_DIR / ".env"
    if not env_path.exists():
        env_example = REPO_DIR / ".env.example"
        if not env_example.exists():
            err(".env.example not found")
        env_path.write_text(env_example.read_text())

    porcupine_key = input("Enter PORCUPINE_ACCESS_KEY: ").strip()
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


if __name__ == "__main__":
    main()
