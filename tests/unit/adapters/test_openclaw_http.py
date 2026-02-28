from __future__ import annotations

from openclaw_assistant.adapters.gateway.openclaw_http import OpenClawHttpExecutor


def test_extract_response_priority() -> None:
    payload = {"message": "m", "response": "r", "text": "t"}
    assert OpenClawHttpExecutor.extract_response(payload) == "r"


def test_extract_response_fallback() -> None:
    payload = {"foo": "bar"}
    assert OpenClawHttpExecutor.extract_response(payload, fallback_text="x") == "x"
