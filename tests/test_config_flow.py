"""Tests for the Cambridge Audio Infrared config flow."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.cambridge_audio_infrared.const import (
    CONF_CXN_SYSTEM_CODE,
    CONF_INFRARED_ENTITY_ID,
    CONF_MODEL,
    DOMAIN,
    MODEL_CXA60,
    MODEL_CXA80,
    MODEL_CXN100,
)


@pytest.fixture(autouse=True)
def auto_mock_emitters(mock_emitter):
    """Patch the infrared emitter/receiver lookups for every test in this module."""
    with (
        patch(
            "custom_components.cambridge_audio_infrared.config_flow.infrared.async_get_emitters",
            return_value=[mock_emitter],
        ),
        patch(
            "custom_components.cambridge_audio_infrared.config_flow.infrared.async_get_receivers",
            return_value=[],
        ),
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
    init = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        init["flow_id"],
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


async def test_entry_with_receiver(hass):
    """When a receiver is available it can be stored in the entry data."""
    from custom_components.cambridge_audio_infrared.const import (
        CONF_INFRARED_RECEIVER_ENTITY_ID,
    )

    with patch(
        "custom_components.cambridge_audio_infrared.config_flow.infrared.async_get_receivers",
        return_value=["remote.ir_receiver"],
    ):
        init = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            init["flow_id"],
            user_input={
                CONF_MODEL: MODEL_CXA60,
                CONF_INFRARED_ENTITY_ID: "remote.ir_blaster",
                CONF_INFRARED_RECEIVER_ENTITY_ID: "remote.ir_receiver",
            },
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_INFRARED_RECEIVER_ENTITY_ID] == "remote.ir_receiver"


async def test_cxn100_two_step_flow(hass):
    """Selecting CXN100 adds a second step for the RC-5 system code."""
    init = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    step2 = await hass.config_entries.flow.async_configure(
        init["flow_id"],
        user_input={
            CONF_MODEL: MODEL_CXN100,
            CONF_INFRARED_ENTITY_ID: "remote.ir_blaster",
        },
    )
    # A CXN selection routes to the 'cxn' step rather than creating the entry.
    assert step2["type"] == FlowResultType.FORM
    assert step2["step_id"] == "cxn"

    result = await hass.config_entries.flow.async_configure(
        step2["flow_id"], user_input={CONF_CXN_SYSTEM_CODE: "28"}
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_MODEL] == MODEL_CXN100
    # Stored as an int, not the selector's string value.
    assert result["data"][CONF_CXN_SYSTEM_CODE] == 28


async def test_reconfigure_adds_receiver(hass):
    """Reconfigure can attach a receiver to an existing entry without re-adding."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from custom_components.cambridge_audio_infrared.const import (
        CONF_INFRARED_RECEIVER_ENTITY_ID,
    )

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODEL: MODEL_CXA60,
            CONF_INFRARED_ENTITY_ID: "remote.ir_blaster",
        },
        unique_id="CXA60_remote.ir_blaster",
    )
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.cambridge_audio_infrared.config_flow.infrared.async_get_receivers",
            return_value=["remote.ir_receiver"],
        ),
        patch(
            "custom_components.cambridge_audio_infrared.async_setup_entry",
            return_value=True,
        ),
    ):
        result = await entry.start_reconfigure_flow(hass)
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "reconfigure"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_INFRARED_ENTITY_ID: "remote.ir_blaster",
                CONF_INFRARED_RECEIVER_ENTITY_ID: "remote.ir_receiver",
            },
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_INFRARED_RECEIVER_ENTITY_ID] == "remote.ir_receiver"
