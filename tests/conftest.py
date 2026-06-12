"""Shared fixtures for Cambridge Audio Infrared tests."""

from unittest.mock import MagicMock, patch

import pytest

from custom_components.cambridge_audio_infrared.const import (
    CONF_INFRARED_ENTITY_ID,
    CONF_MODEL,
    DOMAIN,
    MODEL_CXA60,
    MODEL_CXA80,
)


@pytest.fixture
def mock_emitter():
    """A fake IR emitter entity returned by infrared.async_get_emitters."""
    emitter = MagicMock()
    emitter.entity_id = "remote.ir_blaster"
    emitter.name = "IR Blaster"
    return emitter


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
