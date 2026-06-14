"""Tests for the Cambridge Audio remote event entity."""

from unittest.mock import MagicMock, patch

from homeassistant.config_entries import ConfigEntry

from custom_components.cambridge_audio_infrared.const import (
    CONF_MODEL,
    CXA60_CODES,
    MODEL_CXA60,
    MODEL_CXN100,
    RC5_SYSTEM_CODE,
    resolve_cxn_codes,
)
from custom_components.cambridge_audio_infrared.event import (
    CambridgeAudioRemoteEvent,
)
from custom_components.cambridge_audio_infrared.rc5 import make_rc5_command

# CXA codes all live on system code 16; wrap into the (system, command) shape.
_CXA60_TABLE = {key: (RC5_SYSTEM_CODE, code) for key, code in CXA60_CODES.items()}
_CXN_TABLE = resolve_cxn_codes(24)


def _make_entity(table=_CXA60_TABLE, model=MODEL_CXA60):
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test"
    entry.data = {CONF_MODEL: model}
    return CambridgeAudioRemoteEvent(entry, "remote.ir_receiver", table)


def _signal_for(command: int, address: int = RC5_SYSTEM_CODE):
    signal = MagicMock()
    signal.timings = make_rc5_command(
        address=address, command=command
    ).get_raw_timings()
    return signal


def test_known_command_fires_event():
    """A received volume_up frame triggers the volume_up event."""
    entity = _make_entity()
    with (
        patch.object(entity, "_trigger_event") as mock_trigger,
        patch.object(entity, "async_write_ha_state"),
    ):
        entity._handle_signal(_signal_for(CXA60_CODES["volume_up"]))

    mock_trigger.assert_called_once_with("volume_up", {"toggle": 0})


def test_foreign_address_ignored():
    """RC-5 frames for another device (different address) are ignored."""
    entity = _make_entity()
    with patch.object(entity, "_trigger_event") as mock_trigger:
        entity._handle_signal(_signal_for(CXA60_CODES["volume_up"], address=5))

    mock_trigger.assert_not_called()


def test_unmapped_command_ignored():
    """A valid RC-5 frame with an unknown command code fires nothing."""
    entity = _make_entity()
    with patch.object(entity, "_trigger_event") as mock_trigger:
        entity._handle_signal(_signal_for(63))  # not in CXA60_CODES

    mock_trigger.assert_not_called()


def test_undecodable_signal_ignored():
    """Non-RC-5 timings fire nothing."""
    entity = _make_entity()
    signal = MagicMock()
    signal.timings = [9000, -4500, 560]
    with patch.object(entity, "_trigger_event") as mock_trigger:
        entity._handle_signal(signal)

    mock_trigger.assert_not_called()


def test_event_types_match_code_table():
    """The entity advertises every command key as a possible event type."""
    entity = _make_entity()
    assert set(entity._attr_event_types) == set(CXA60_CODES)


# ── CXN (multi system-code) ──────────────────────────────────────────────────

def test_cxn_play_pause_fires_event():
    """A CXN Play/Pause frame (system 24) fires on a CXN event entity."""
    entity = _make_entity(table=_CXN_TABLE, model=MODEL_CXN100)
    with (
        patch.object(entity, "_trigger_event") as mock_trigger,
        patch.object(entity, "async_write_ha_state"),
    ):
        entity._handle_signal(_signal_for(24, address=24))  # play_pause

    mock_trigger.assert_called_once_with("play_pause", {"toggle": 0})


def test_cxn_entity_ignores_amp_navigation_frame():
    """A CXA-only frame (system 16, source_up=99) means nothing to the CXN."""
    entity = _make_entity(table=_CXN_TABLE, model=MODEL_CXN100)
    with patch.object(entity, "_trigger_event") as mock_trigger:
        entity._handle_signal(_signal_for(99, address=RC5_SYSTEM_CODE))

    mock_trigger.assert_not_called()


def test_cxa_entity_ignores_cxn_network_frame():
    """A CXN network frame (system 24) means nothing to a CXA event entity."""
    entity = _make_entity()  # CXA60
    with patch.object(entity, "_trigger_event") as mock_trigger:
        entity._handle_signal(_signal_for(12, address=24))  # CXN 'home'

    mock_trigger.assert_not_called()
