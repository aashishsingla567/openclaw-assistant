# Silence-Aware Recording Upgrade

OpenClaw records voice commands in 100ms chunks and stops deterministically when both conditions are met:

1. Minimum capture time is reached (`OPENCLAW_RECORD_MIN_SECONDS`, default `1.0`).
2. Consecutive silence duration is reached (`OPENCLAW_SILENCE_SECONDS`, default `0.9`) based on RMS energy threshold (`OPENCLAW_SILENCE_THRESHOLD`, default `180.0` in int16 scale).

## Why this is reliable

- Bounded runtime: hard stop at `OPENCLAW_RECORD_MAX_SECONDS` (default `8.0`).
- No hidden VAD randomness: plain RMS threshold and fixed chunk size.
- Low overhead: only NumPy + `sounddevice`, no extra model in the hot path.

## Tuning sequence

1. Start with defaults.
2. If recordings cut off too early, lower `OPENCLAW_SILENCE_THRESHOLD` by 20 and/or increase `OPENCLAW_SILENCE_SECONDS` by 0.2.
3. If recordings run too long in noisy rooms, raise `OPENCLAW_SILENCE_THRESHOLD` by 20.
4. Keep `OPENCLAW_COMMAND_SAMPLE_RATE=16000` to match wake/STT path and avoid resampling variance.

## Validation command

Use the assistant logs while speaking short and long prompts:

```bash
tail -f /tmp/openclaw-assistant.log
```
