# Diagnostics

Use subcommands:

```bash
uv run openclaw diagnostics devices
uv run openclaw diagnostics tts --text "hello"
uv run openclaw diagnostics stt --seconds 4
uv run openclaw diagnostics wakeword --timeout 15
uv run openclaw diagnostics pipeline --timeout 15
uv run openclaw diagnostics pipeline --timeout 15 --openclaw
```

`pipeline` path verifies the same prompt/listen/transcribe/action/speak flow used by runtime.
