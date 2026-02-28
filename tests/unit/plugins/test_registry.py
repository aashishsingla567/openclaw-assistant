from __future__ import annotations

import pytest

from openclaw_assistant.plugins.registry import PluginRegistry


class _BrokenWake:
    pass


def test_registry_validation_rejects_invalid_plugin() -> None:
    registry = PluginRegistry(wakeword_listener=_BrokenWake())
    with pytest.raises(TypeError):
        registry.validate()
