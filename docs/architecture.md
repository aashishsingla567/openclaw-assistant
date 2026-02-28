# Architecture

## Pipeline

Event order:
1. `WakeDetected`
2. `ListenStarted`
3. `AudioCaptured`
4. `TextTranscribed`
5. `ActionCompleted`
6. `ResponseSpoken`

The orchestrator (`core/pipeline.py`) knows only contracts and plugin stages.

## Separation of Concerns

- Core: no vendor imports.
- Adapters: all `pvporcupine`, `faster-whisper`, `kokoro-onnx`, `requests`, `sounddevice` coupling.
- Plugins: compose runtime behavior through stage methods.

## Runtime and Diagnostics Reuse

Both use:
- same settings loader
- same adapters
- same pluginized pipeline stages
