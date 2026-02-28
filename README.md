# OpenClaw Assistant

OpenClaw Assistant is a local voice runtime with a plugin-driven pipeline and installable CLI.

## Quick Start

```bash
uv sync --extra dev
uv run openclaw setup
uv run openclaw run
```

## CLI

```bash
# Runtime
uv run openclaw run

# Onboarding/update
uv run openclaw setup
uv run openclaw update
uv run openclaw update --dev

# Diagnostics
uv run openclaw diagnostics devices
uv run openclaw diagnostics tts --text "Hello from Kokoro"
uv run openclaw diagnostics stt --seconds 4
uv run openclaw diagnostics openclaw --text "Ping"
uv run openclaw diagnostics wakeword --timeout 15
uv run openclaw diagnostics pipeline --timeout 15
uv run openclaw diagnostics pipeline --timeout 15 --openclaw
```

## Architecture

- Core orchestration: `src/openclaw_assistant/core/`
- Vendor adapters: `src/openclaw_assistant/adapters/`
- Builtin plugins: `src/openclaw_assistant/plugins/builtin/`
- App runtime: `src/openclaw_assistant/app/`
- CLI commands: `src/openclaw_assistant/commands/`

Read more:
- `docs/architecture.md`
- `docs/plugin-development.md`
- `docs/diagnostics.md`
