# OpenClaw macOS Voice Assistant (Local, Deterministic)

Stack:
- Wake word: Porcupine (`pvporcupine`)
- STT: `faster-whisper`
- TTS: Kokoro ONNX (`kokoro-onnx`)
- Audio I/O: `sounddevice`
- OpenClaw: HTTP REST (`OPENCLAW_REST_URL`)
- Scheduling: **OpenClaw cron** (Gateway built-in; no OS cron in this repo)

---

## 1) Shell Commands (Exact Order)

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
# Clone repo
mkdir -p ~/Projects
cd ~/Projects

git clone https://github.com/<YOUR_GITHUB_USER>/openclaw-assistant.git
cd openclaw-assistant
```

```bash
# One-command onboarding (asks for key + wake word, lets you pick .ppn, then runs)
uv run ./onboard/setup.py
```

```bash
# Update + reload after repo changes
uv run ./onboard/update.py
```

```bash
# Update + run in foreground with logs
uv run ./onboard/update.py --dev
# or:
OPENCLAW_DEV=1 uv run ./onboard/update.py
```

```bash
# Diagnostics: list devices
uv run ./onboard/diagnostics.py --list-devices

# Diagnostics: TTS
uv run ./onboard/diagnostics.py --tts --text "Hello from Kokoro"

# Diagnostics: STT
uv run ./onboard/diagnostics.py --stt --seconds 4

# Diagnostics: OpenClaw REST
uv run ./onboard/diagnostics.py --openclaw --text "Ping"
```

```bash
# Load env and run (first launch)
set -a && source .env && set +a
uv run python assistant.py
```

---

## Next Steps After Onboarding

Onboarding now starts the assistant automatically. If you want to run it manually later:

```bash
set -a && source .env && set +a
uv run python assistant.py
```

(Optional) Install launchd:

```bash
sed "s#__REPO_PATH__#$(pwd)#g" launchd/com.openclaw.assistant.plist > /tmp/com.openclaw.assistant.plist
cp /tmp/com.openclaw.assistant.plist ~/Library/LaunchAgents/com.openclaw.assistant.plist
launchctl unload ~/Library/LaunchAgents/com.openclaw.assistant.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.openclaw.assistant.plist
```

## Manual Setup (if auto setup fails)

If onboarding runs into a dependency or permission issue, use the manual steps below. The onboarding script is designed to be extensible; it will either complete the setup or tell you exactly what to fix.

```bash
# Install system deps (Apple Silicon macOS)
brew install portaudio libsndfile espeak-ng git-lfs
```

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
# Python deps
uv sync
```

```bash
# Model + asset dirs
mkdir -p models/kokoro models/porcupine models/whisper
```

```bash
# Kokoro model files
curl -L -o models/kokoro/kokoro-v1.0.onnx \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
```

```bash
curl -L -o models/kokoro/voices-v1.0.bin \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

```bash
# Environment config
cp .env.example .env
```

```bash
# Edit .env and set PORCUPINE_ACCESS_KEY
# Place wake word model at ./models/porcupine/openclaw_mac.ppn
```

```bash
# Load env and run
set -a && source .env && set +a
uv run python assistant.py
```

---

## 2) Wake-Word Training (Porcupine Custom Keyword)

1. Open `https://console.picovoice.ai/`.
2. Create/login account and copy your AccessKey.
3. Create a custom keyword (example: `OpenClaw`).
4. Platform: `macOS` (Apple Silicon), Language: `English`.
5. Download the `.ppn` file.
6. Save it to:
   `./models/porcupine/openclaw_mac.ppn`
7. Set wake word label in `.env`:

```bash
WAKEWORD_LABEL=OpenClaw
```

8. Export access key before launch:

```bash
export PORCUPINE_ACCESS_KEY='YOUR_PICOVOICE_ACCESS_KEY'
```

9. Tune sensitivity in `.env`:

```bash
PORCUPINE_SENSITIVITY=0.55
```

---

## 3) OpenClaw Requirements

- OpenClaw must be running locally.
- REST endpoint must be reachable at `OPENCLAW_REST_URL` (default `http://127.0.0.1:3000/v1/assistant`).
- If you run OpenClaw on a different host/port, update `.env`.

Mic permissions (macOS):
- System Settings → Privacy & Security → Microphone → enable for your terminal app.

## 4) OpenClaw Cron (Proactive Prompts)

Use **OpenClaw’s built-in cron** (Gateway scheduler). Example:

```bash
openclaw cron add \
  --name "Morning brief" \
  --cron "0 7 * * *" \
  --session isolated \
  --message "Summarize inbox + calendar for today." \
  --announce
```

One-shot reminder:

```bash
openclaw cron add \
  --name "Reminder" \
  --at "2026-03-01T02:30:00Z" \
  --session main \
  --system-event "Reminder: review the deployment plan." \
  --wake now \
  --delete-after-run
```

---

## 5) launchd Setup (Auto-Start)

```bash
# Replace __REPO_PATH__ in the plist before installing
sed "s#__REPO_PATH__#$(pwd)#g" launchd/com.openclaw.assistant.plist > /tmp/com.openclaw.assistant.plist

cp /tmp/com.openclaw.assistant.plist ~/Library/LaunchAgents/com.openclaw.assistant.plist
```

```bash
launchctl unload ~/Library/LaunchAgents/com.openclaw.assistant.plist 2>/dev/null || true
```

```bash
launchctl load ~/Library/LaunchAgents/com.openclaw.assistant.plist
```

```bash
launchctl list | rg com.openclaw.assistant
```

Logs:
- `/tmp/openclaw-assistant.log`
- `/tmp/openclaw-assistant.err.log`

---

## 6) Directory Structure

```text
openclaw-assistant/
├── assistant.py
├── config.py
├── .env.example
├── launchd/
│   └── com.openclaw.assistant.plist
├── upgrades/
│   └── silence_recording.md
├── models/
│   ├── kokoro/
│   │   ├── kokoro-v1.0.onnx
│   │   └── voices-v1.0.bin
│   ├── porcupine/
│   │   └── openclaw_mac.ppn
│   └── whisper/
├── pyproject.toml
└── README.md
```

---

## 7) Runtime Notes

- Pipeline: wake word -> silence-bounded recording -> faster-whisper -> OpenClaw REST -> Kokoro TTS.
- REST endpoint set via `OPENCLAW_REST_URL` (default `http://127.0.0.1:3000/v1/assistant`).
- `.env` supports relative paths (e.g., `./models/...`).

---

## 8) Performance (M-series Macs)

- `OPENCLAW_WHISPER_COMPUTE_TYPE=int8`
- Prefer `small.en` or `base` models
- Keep sample rate `16000`

## 9) Speech Capture Tuning

If you get "No speech detected":

- Increase `OPENCLAW_WAKEWORD_START_DELAY` (default `0.4`)
- Increase `OPENCLAW_RECORD_MIN_SECONDS` (e.g., `1.5`)
- Lower `OPENCLAW_SILENCE_THRESHOLD` (e.g., `140`)
- Increase `OPENCLAW_SILENCE_SECONDS` (e.g., `1.2`)

Listening feedback uses TTS prompts (`OPENCLAW_WAKE_HELLO_PROMPT`, `OPENCLAW_LISTEN_START_PROMPT`).

TTS smoothing (fade + padding + prewarm):
- `OPENCLAW_TTS_FADE_MS` (default 20)
- `OPENCLAW_TTS_PADDING_MS` (default 40)
- `OPENCLAW_TTS_PREWARM_MS` (default 50)

---

## 9) Troubleshooting

- **No wake word detection**: verify `.ppn` path in `.env` and `PORCUPINE_ACCESS_KEY`.
- **No audio input**: check mic permissions for your terminal.
- **No response**: confirm OpenClaw is running and `OPENCLAW_REST_URL` is reachable.
- **TTS silent**: verify Kokoro files in `models/kokoro/` and `KOKORO_*` paths.
