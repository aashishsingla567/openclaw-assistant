from __future__ import annotations

from typing import Any

import requests

from openclaw_assistant.config.settings import Settings


class OpenClawHttpExecutor:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @staticmethod
    def extract_response(payload: dict[str, Any], fallback_text: str = "") -> str:
        for key in ("response", "reply", "text", "message", "output"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return fallback_text.strip()

    def execute(self, prompt: str) -> str:
        response = requests.post(
            self.settings.openclaw_rest_url,
            json={"text": prompt},
            timeout=self.settings.openclaw_timeout_seconds,
        )
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type.lower():
            payload = response.json()
            if isinstance(payload, dict):
                return self.extract_response(payload)
        return response.text.strip()
