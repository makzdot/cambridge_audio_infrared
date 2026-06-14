"""Shared fixtures for Cambridge Audio Infrared tests."""

import importlib.util

import pytest

from custom_components.cambridge_audio_infrared.const import (
    CONF_INFRARED_ENTITY_ID,
    CONF_MODEL,
    DOMAIN,
    MODEL_CXA60,
    MODEL_CXA80,
)


def _infrared_platform_available() -> bool:
    """Return True if this Home Assistant build ships the infrared platform."""
    try:
        return (
            importlib.util.find_spec("homeassistant.components.infrared") is not None
        )
    except ModuleNotFoundError:
        return False


# The media_player/button/event/config_flow modules import the infrared platform,
# which only exists in HA builds that ship it. When the installed HA predates it
# (e.g. the version pinned by pytest-homeassistant-custom-component), skip those
# test modules so the Home-Assistant-independent protocol tests still run.
collect_ignore: list[str] = []
if not _infrared_platform_available():
    collect_ignore = [
        "test_cxn.py",
        "test_event.py",
        "test_config_flow.py",
        "test_media_player.py",
    ]


@pytest.fixture
def mock_emitter():
    """A fake IR emitter entity_id as returned by infrared.async_get_emitters."""
    return "remote.ir_blaster"


@pytest.fixture
def cxa60_entry_data():
    return {
        CONF_MODEL: MODEL_CXA60,
        CONF_INFRARED_ENTITY_ID: "remote.ir_blaster",
    }


@pytest.fixture
def cxa80_entry_data():
    return {
        CONF_MODEL: MODEL_CXA80,
        CONF_INFRARED_ENTITY_ID: "remote.ir_blaster",
    }
