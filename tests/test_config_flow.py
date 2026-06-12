"""Tests for the Cambridge Audio Infrared config flow."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.cambridge_audio_infrared.const import (
    CONF_INFRARED_ENTITY_ID,
    CONF_MODEL,
    DOMAIN,
    MODEL_CXA60,
    MODEL_CXA80,
)


@pytest.fixture(autouse=True)
def auto_mock_emitters(mock_emitter):
    """Patch infrared.async_get_emitters for every test in this module."""
    with patch(
        "custom_components.cambridge_audio_infrared.config_flow.infrared.async_get_emitters",
        return_value=[mock_emitter],
    ):
        yield


async def test_user_step_shows_form(hass):
    """The initial step renders the form when emitters are present."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert not result["errors"]


async def test_user_step_creates_entry_cxa60(hass):
    """Submitting valid CXA60 data creates a config entry."""
    await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_MODEL: MODEL_CXA60,
            CONF_INFRARED_ENTITY_ID: "remote.ir_blaster",
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Cambridge Audio CXA60"
    assert result["data"][CONF_MODEL] == MODEL_CXA60


async def test_user_step_creates_entry_cxa80(hass):
    """Submitting valid CXA80 data creates a config entry."""
    init = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        init["flow_id"],
        user_input={
            CONF_MODEL: MODEL_CXA80,
            CONF_INFRARED_ENTITY_ID: "remote.ir_blaster",
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_MODEL] == MODEL_CXA80


async def test_abort_when_no_emitters(hass):
    """Flow aborts with 'no_emitters' when no IR emitters are configured."""
    with patch(
        "custom_components.cambridge_audio_infrared.config_flow.infrared.async_get_emitters",
        return_value=[],
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "no_emitters"


async def test_abort_on_duplicate(hass):
    """A second flow for the same model+emitter is rejected as already configured."""
    user_input = {
        CONF_MODEL: MODEL_CXA60,
        CONF_INFRARED_ENTITY_ID: "remote.ir_blaster",
    }

    init = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    await hass.config_entries.flow.async_configure(init["flow_id"], user_input)

    # Second attempt for the same combination
    init2 = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(init2["flow_id"], user_input)

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"
