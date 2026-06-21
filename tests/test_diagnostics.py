"""Tests for the Cambridge Audio Infrared diagnostics."""

from unittest.mock import MagicMock

from custom_components.cambridge_audio_infrared.const import (
    CONF_INFRARED_ENTITY_ID,
    CONF_INFRARED_RECEIVER_ENTITY_ID,
    CONF_MODEL,
    MODEL_CXA60,
)
from custom_components.cambridge_audio_infrared.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_diagnostics_reports_config_and_emitter_state(hass):
    """Diagnostics include the model and the live emitter/receiver state."""
    hass.states.async_set("remote.ir_blaster", "idle")

    entry = MagicMock()
    entry.data = {
        CONF_MODEL: MODEL_CXA60,
        CONF_INFRARED_ENTITY_ID: "remote.ir_blaster",
    }

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["model"] == MODEL_CXA60
    assert result["emitter"] == {"entity_id": "remote.ir_blaster", "state": "idle"}
    # No receiver configured.
    assert result["receiver"] == {"entity_id": None, "state": None}


async def test_diagnostics_marks_missing_emitter(hass):
    """A configured emitter that isn't present shows up as not_found."""
    entry = MagicMock()
    entry.data = {
        CONF_MODEL: MODEL_CXA60,
        CONF_INFRARED_ENTITY_ID: "remote.gone",
        CONF_INFRARED_RECEIVER_ENTITY_ID: "remote.rx_gone",
    }

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["emitter"]["state"] == "not_found"
    assert result["receiver"]["state"] == "not_found"
