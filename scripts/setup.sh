#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

info() { printf "\n==> %s\n" "$*"; }
err() { printf "\nERROR: %s\n" "$*" >&2; exit 1; }

command -v brew >/dev/null 2>&1 || err "Homebrew is required. Install from https://brew.sh"
command -v uv >/dev/null 2>&1 || err "uv is required. Install from https://astral.sh/uv"

info "Opening required sites"
open "https://console.picovoice.ai/" || true

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

read -r -p "Enter PORCUPINE_ACCESS_KEY: " PORCUPINE_ACCESS_KEY
if [ -z "$PORCUPINE_ACCESS_KEY" ]; then
  err "PORCUPINE_ACCESS_KEY is required"
fi

info "Writing .env"
if grep -q "^PORCUPINE_ACCESS_KEY=" .env; then
  sed -i '' "s#^PORCUPINE_ACCESS_KEY=.*#PORCUPINE_ACCESS_KEY=${PORCUPINE_ACCESS_KEY}#" .env
else
  echo "PORCUPINE_ACCESS_KEY=${PORCUPINE_ACCESS_KEY}" >> .env
fi

cat <<'EOF'

Place your Porcupine wake word model at:
  ./models/porcupine/openclaw_mac.ppn

Generate it here:
  https://console.picovoice.ai/

Next steps:
1) Run:  set -a && source .env && set +a
2) Start: uv run python assistant.py
3) (Optional) Install launchd:
   sed "s#__REPO_PATH__#$(pwd)#g" launchd/com.openclaw.assistant.plist > /tmp/com.openclaw.assistant.plist
   cp /tmp/com.openclaw.assistant.plist ~/Library/LaunchAgents/com.openclaw.assistant.plist
   launchctl unload ~/Library/LaunchAgents/com.openclaw.assistant.plist 2>/dev/null || true
   launchctl load ~/Library/LaunchAgents/com.openclaw.assistant.plist
EOF
