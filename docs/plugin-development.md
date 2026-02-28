# Plugin Development

Builtin stage slots:
- `wakeword_listener.wait_for_wakeword(context, timeout_seconds)`
- `listen_stage.capture_audio(context)`
- `transcribe_stage.transcribe(audio, context)`
- `action_stage.execute(prompt, context)`
- `speak_stage.speak(response, context)`

## First Plugin in 20 Minutes

1. Create plugin class in `src/openclaw_assistant/plugins/builtin/` or your own module.
2. Implement required method for that stage.
3. Assign it in `PluginRegistry` during app/bootstrap.
4. Add unit test for the stage behavior.
