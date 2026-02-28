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
cd /Users/aashishsingla/Development/experiment/openclaw-assistant
```

```bash
uv sync
```

```bash
mkdir -p models/kokoro models/porcupine models/whisper upgrades launchd
```

```bash
curl -L -o models/kokoro/kokoro-v1.0.onnx \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
```

```bash
curl -L -o models/kokoro/voices-v1.0.bin \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

```bash
cp .env.example .env
```

```bash
set -a && source .env && set +a
```

```bash
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
   `/Users/aashishsingla/Development/experiment/openclaw-assistant/models/porcupine/openclaw_mac.ppn`
7. Export access key before launch:

```bash
export PORCUPINE_ACCESS_KEY='YOUR_PICOVOICE_ACCESS_KEY'
```

8. Tune sensitivity in `.env`:

```bash
PORCUPINE_SENSITIVITY=0.55
```

---

## 3) OpenClaw Cron (Proactive Prompts)

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

## 4) launchd Setup (Auto-Start)

```bash
cp launchd/com.openclaw.assistant.plist ~/Library/LaunchAgents/com.openclaw.assistant.plist
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

## 5) Directory Structure

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

## 6) Runtime Notes

- Pipeline: wake word -> silence-bounded recording -> faster-whisper -> OpenClaw REST -> Kokoro TTS.
- REST endpoint set via `OPENCLAW_REST_URL` (default `http://127.0.0.1:3000/v1/assistant`).

---

## 7) Performance (M-series Macs)

- `OPENCLAW_WHISPER_COMPUTE_TYPE=int8`
- Prefer `small.en` or `base` models
- Keep sample rate `16000`
