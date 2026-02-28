from __future__ import annotations

import argparse
import json
import threading


class _NoopActionStage:
    def execute(self, _prompt: str, _context: object) -> str:
        return ""


def _print_wakeword_settings(
    detector: object,
    label: str,
    keyword_path: object,
    sensitivity: float,
    input_device: object,
) -> None:
    if not hasattr(detector, "audio_params"):
        raise TypeError("Detector must implement audio_params()")
    sample_rate, frame_length = detector.audio_params()
    print("Wakeword settings:")
    print(f"  label={label}")
    print(f"  keyword_path={keyword_path}")
    print(f"  sensitivity={sensitivity}")
    print(f"  input_device={input_device}")
    print(f"  sample_rate={sample_rate}")
    print(f"  frame_length={frame_length}")


def diagnostics_command(args: argparse.Namespace) -> None:
    from openclaw_assistant.adapters.audio.input_stream import AudioInput
    from openclaw_assistant.adapters.gateway.openclaw_http import OpenClawHttpExecutor
    from openclaw_assistant.adapters.stt.faster_whisper import FasterWhisperTranscriber
    from openclaw_assistant.adapters.tts.kokoro import KokoroSpeaker
    from openclaw_assistant.adapters.wakeword.porcupine import PorcupineWakewordDetector
    from openclaw_assistant.app.runner import AppRunner
    from openclaw_assistant.config.loader import load_settings
    from openclaw_assistant.core.context import RuntimeContext
    from openclaw_assistant.core.events import ActionCompleted, TextTranscribed

    settings = load_settings()

    if args.diag_cmd == "devices":
        print(json.dumps(AudioInput.list_devices(), indent=2))
        return

    if args.diag_cmd == "tts":
        speaker = KokoroSpeaker(settings, reuse_output_stream=False)
        try:
            print("TTS settings:")
            print(f"  fade_ms={settings.tts_fade_ms}")
            print(f"  padding_ms={settings.tts_padding_ms}")
            print(f"  prewarm_ms={settings.tts_prewarm_ms}")
            print(f"  output_device={settings.audio_output_device}")
            speaker.speak(args.text)
        finally:
            speaker.close()
        return

    if args.diag_cmd == "stt":
        transcriber = FasterWhisperTranscriber(settings)
        print(f"Recording {args.seconds:.1f}s... speak now")
        audio = AudioInput.record_fixed_seconds(
            seconds=args.seconds,
            sample_rate=settings.command_sample_rate,
            device=settings.audio_input_device,
        )
        text = transcriber.transcribe(audio)
        print("Transcription:")
        print(text)
        return

    if args.diag_cmd == "openclaw":
        response = OpenClawHttpExecutor(settings).execute(args.text)
        print("OpenClaw response:")
        print(response)
        return

    if args.diag_cmd == "wakeword":
        settings.validate_runtime_assets(include_tts_assets=False)
        detector = PorcupineWakewordDetector(settings, stop_event=threading.Event())
        _print_wakeword_settings(
            detector,
            settings.wakeword_label,
            settings.porcupine_keyword_path,
            settings.porcupine_sensitivity,
            settings.audio_input_device,
        )
        print(
            f"Listening for wakeword for up to {args.timeout:.1f}s... "
            f"say '{settings.wakeword_label}'."
        )
        detected = detector.wait_for_wakeword(timeout_seconds=args.timeout)
        if detected:
            print("Wakeword detected.")
        else:
            print("Wakeword NOT detected before timeout.")
        return

    if args.diag_cmd == "pipeline":
        runner = AppRunner(settings)
        try:
            settings.validate_runtime_assets(include_tts_assets=True)
            _print_wakeword_settings(
                runner.context.wakeword,
                settings.wakeword_label,
                settings.porcupine_keyword_path,
                settings.porcupine_sensitivity,
                settings.audio_input_device,
            )
            print(
                f"Listening for wakeword for up to {args.timeout:.1f}s... "
                f"say '{settings.wakeword_label}'."
            )
            detected = runner.context.wakeword.wait_for_wakeword(timeout_seconds=args.timeout)
            if not detected:
                print("Wakeword NOT detected before timeout.")
                return

            print("Wakeword detected. Running assistant prompt/listen flow...")
            state: dict[str, str] = {"text": "", "response": ""}

            def _capture(event: object, _context: RuntimeContext) -> None:
                if isinstance(event, TextTranscribed):
                    state["text"] = event.text
                if isinstance(event, ActionCompleted):
                    state["response"] = event.response

            runner.registry.register_event_handler(_capture)
            if not args.openclaw:
                runner.registry.action_stage = _NoopActionStage()
            runner.pipeline.run_once_after_wake()

            print("Pipeline transcription:")
            print(state["text"] or "<empty>")
            if args.openclaw:
                print("Pipeline OpenClaw response:")
                print(state["response"] or "<empty>")
        finally:
            runner.stop()


def add_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("diagnostics", help="Run diagnostics")
    child = parser.add_subparsers(dest="diag_cmd", required=True)

    child.add_parser("devices", help="List audio devices")

    tts = child.add_parser("tts", help="Test TTS")
    tts.add_argument("--text", default="Testing text to speech.")

    stt = child.add_parser("stt", help="Test STT")
    stt.add_argument("--seconds", type=float, default=3.0)

    openclaw = child.add_parser("openclaw", help="Test OpenClaw REST")
    openclaw.add_argument("--text", default="Ping")

    wake = child.add_parser("wakeword", help="Test wakeword detection")
    wake.add_argument("--timeout", type=float, default=10.0)

    pipeline = child.add_parser("pipeline", help="Test full wakeword pipeline")
    pipeline.add_argument("--timeout", type=float, default=15.0)
    pipeline.add_argument("--openclaw", action="store_true")

    parser.set_defaults(handler=diagnostics_command)
