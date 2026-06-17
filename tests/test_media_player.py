"""Tests for the Cambridge Audio media player platform."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.media_player import MediaPlayerState

from custom_components.cambridge_audio_infrared.const import (
    CONF_MODEL,
    MODEL_CXA60,
    MODEL_CXA80,
    RC5_SYSTEM_CODE,
)


@pytest.fixture
def mock_send():
    """Patch infrared.async_send_command so no real IR is sent."""
    with patch(
        "custom_components.cambridge_audio_infrared.media_player.infrared.async_send_command",
        new_callable=AsyncMock,
    ) as mock:
        yield mock


@pytest.fixture
def mock_rc5():
    """Patch make_rc5_command to return a sentinel object."""
    sentinel = MagicMock(name="rc5_command")
    with patch(
        "custom_components.cambridge_audio_infrared.media_player.make_rc5_command",
        return_value=sentinel,
    ) as mock:
        mock.sentinel = sentinel
        yield mock


# ── CXA60 ─────────────────────────────────────────────────────────────────────

async def test_cxa60_turn_on(hass, mock_send, mock_rc5):
    """async_turn_on sends power_on and sets state to ON."""
    from custom_components.cambridge_audio_infrared.media_player import (
        CambridgeAudioCXA60MediaPlayer,
    )
    from homeassistant.config_entries import ConfigEntry

    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test"
    entry.data = {CONF_MODEL: MODEL_CXA60}

    player = CambridgeAudioCXA60MediaPlayer(entry, "remote.ir_blaster")
    player.hass = hass

    await player.async_turn_on()

    mock_rc5.assert_called_once_with(address=RC5_SYSTEM_CODE, command=14)
    mock_send.assert_awaited_once()
    assert player.state == MediaPlayerState.ON


async def test_cxa60_turn_off(hass, mock_send, mock_rc5):
    """async_turn_off sends power_off and sets state to OFF."""
    from custom_components.cambridge_audio_infrared.media_player import (
        CambridgeAudioCXA60MediaPlayer,
    )
    from homeassistant.config_entries import ConfigEntry

    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test"
    entry.data = {CONF_MODEL: MODEL_CXA60}

    player = CambridgeAudioCXA60MediaPlayer(entry, "remote.ir_blaster")
    player.hass = hass
    player._attr_state = MediaPlayerState.ON

    await player.async_turn_off()

    mock_rc5.assert_called_once_with(address=RC5_SYSTEM_CODE, command=15)
    assert player.state == MediaPlayerState.OFF


async def test_cxa60_mute_on(hass, mock_send, mock_rc5):
    """async_mute_volume(True) sends mute_on and tracks muted state."""
    from custom_components.cambridge_audio_infrared.media_player import (
        CambridgeAudioCXA60MediaPlayer,
    )
    from homeassistant.config_entries import ConfigEntry

    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test"
    entry.data = {CONF_MODEL: MODEL_CXA60}

    player = CambridgeAudioCXA60MediaPlayer(entry, "remote.ir_blaster")
    player.hass = hass

    await player.async_mute_volume(True)

    mock_rc5.assert_called_once_with(address=RC5_SYSTEM_CODE, command=50)
    assert player.is_volume_muted is True


async def test_cxa60_mute_off(hass, mock_send, mock_rc5):
    """async_mute_volume(False) sends mute_off."""
    from custom_components.cambridge_audio_infrared.media_player import (
        CambridgeAudioCXA60MediaPlayer,
    )
    from homeassistant.config_entries import ConfigEntry

    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test"
    entry.data = {CONF_MODEL: MODEL_CXA60}

    player = CambridgeAudioCXA60MediaPlayer(entry, "remote.ir_blaster")
    player.hass = hass
    player._muted = True

    await player.async_mute_volume(False)

    mock_rc5.assert_called_once_with(address=RC5_SYSTEM_CODE, command=51)
    assert player.is_volume_muted is False


async def test_cxa60_select_source(hass, mock_send, mock_rc5):
    """async_select_source sends the correct input code and tracks source."""
    from custom_components.cambridge_audio_infrared.media_player import (
        CambridgeAudioCXA60MediaPlayer,
    )
    from homeassistant.config_entries import ConfigEntry

    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test"
    entry.data = {CONF_MODEL: MODEL_CXA60}

    player = CambridgeAudioCXA60MediaPlayer(entry, "remote.ir_blaster")
    player.hass = hass

    await player.async_select_source("D1")

    mock_rc5.assert_called_once_with(address=RC5_SYSTEM_CODE, command=105)
    assert player.source == "D1"


async def test_cxa60_select_unknown_source_logs_error(hass, mock_send, mock_rc5, caplog):
    """Selecting an unknown source logs an error and sends nothing."""
    from custom_components.cambridge_audio_infrared.media_player import (
        CambridgeAudioCXA60MediaPlayer,
    )
    from homeassistant.config_entries import ConfigEntry

    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test"
    entry.data = {CONF_MODEL: MODEL_CXA60}

    player = CambridgeAudioCXA60MediaPlayer(entry, "remote.ir_blaster")
    player.hass = hass

    await player.async_select_source("HDMI1")

    mock_send.assert_not_awaited()
    assert "Unknown source" in caplog.text


# ── CXA80 ─────────────────────────────────────────────────────────────────────

async def test_cxa80_bluetooth_source(hass, mock_send, mock_rc5):
    """CXA80 can select Bluetooth (CXA80-only source, code 115)."""
    from custom_components.cambridge_audio_infrared.media_player import (
        CambridgeAudioCXA80MediaPlayer,
    )
    from homeassistant.config_entries import ConfigEntry

    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test"
    entry.data = {CONF_MODEL: MODEL_CXA80}

    player = CambridgeAudioCXA80MediaPlayer(entry, "remote.ir_blaster")
    player.hass = hass

    await player.async_select_source("Bluetooth")

    mock_rc5.assert_called_once_with(address=RC5_SYSTEM_CODE, command=115)
    assert player.source == "Bluetooth"


async def test_cxa80_has_bluetooth_in_source_list():
    """CXA80 source list includes Bluetooth and A1 Balanced."""
    from custom_components.cambridge_audio_infrared.media_player import (
        CambridgeAudioCXA80MediaPlayer,
    )

    assert "Bluetooth" in CambridgeAudioCXA80MediaPlayer._attr_source_list
    assert "A1 Balanced" in CambridgeAudioCXA80MediaPlayer._attr_source_list
