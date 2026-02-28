#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

info() { printf "\n==> %s\n" "$*"; }
err() { printf "\nERROR: %s\n" "$*" >&2; exit 1; }

command -v brew >/dev/null 2>&1 || err "Homebrew is required. Install from https://brew.sh"
command -v uv >/dev/null 2>&1 || err "uv is required. Install from https://astral.sh/uv"

info "Installing system dependencies"
brew install portaudio libsndfile espeak-ng git-lfs

info "Syncing Python dependencies"
cd "$REPO_DIR"
uv sync

info "Creating directories"
mkdir -p models/kokoro models/porcupine models/whisper launchd

info "Downloading Kokoro models"
if [ ! -f models/kokoro/kokoro-v1.0.onnx ]; then
  curl -L -o models/kokoro/kokoro-v1.0.onnx \
    https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
fi
if [ ! -f models/kokoro/voices-v1.0.bin ]; then
  curl -L -o models/kokoro/voices-v1.0.bin \
    https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
fi

info "Preparing .env"
if [ ! -f .env ]; then
  cp .env.example .env
fi

echo
cat <<'EOF'
Next steps:
1) Place your Porcupine wake word model at: ./models/porcupine/openclaw_mac.ppn
2) Edit .env and set PORCUPINE_ACCESS_KEY
3) Run:  set -a && source .env && set +a
4) Start: uv run python assistant.py
5) (Optional) Install launchd:
   sed "s#__REPO_PATH__#$(pwd)#g" launchd/com.openclaw.assistant.plist > /tmp/com.openclaw.assistant.plist
   cp /tmp/com.openclaw.assistant.plist ~/Library/LaunchAgents/com.openclaw.assistant.plist
   launchctl unload ~/Library/LaunchAgents/com.openclaw.assistant.plist 2>/dev/null || true
   launchctl load ~/Library/LaunchAgents/com.openclaw.assistant.plist
EOF
