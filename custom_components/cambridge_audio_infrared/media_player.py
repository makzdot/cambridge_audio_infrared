"""Media player platform for Cambridge Audio Infrared."""

from __future__ import annotations

import logging

from homeassistant.components import infrared
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CambridgeAudioConfigEntry
from .const import (
    CONF_MODEL,
    CXA60_CODES,
    CXA60_SOURCES,
    CXA80_CODES,
    CXA80_SOURCES,
    DOMAIN,
    MODEL_CXA60,
    MODEL_CXA80,
    RC5_SYSTEM_CODE,
)
from .rc5 import make_rc5_command

_LOGGER = logging.getLogger(__name__)

_SUPPORTED_FEATURES = (
    MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.SELECT_SOURCE
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CambridgeAudioConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cambridge Audio media player from a config entry."""
    model = entry.runtime_data.model
    ir_entity_id = entry.runtime_data.emitter_entity_id

    if model == MODEL_CXA60:
        async_add_entities([CambridgeAudioCXA60MediaPlayer(entry, ir_entity_id)])
    elif model == MODEL_CXA80:
        async_add_entities([CambridgeAudioCXA80MediaPlayer(entry, ir_entity_id)])


class CambridgeAudioCXA60MediaPlayer(MediaPlayerEntity):
    """Representation of a Cambridge Audio CXA60 amplifier via IR."""

    _attr_has_entity_name = True
    _attr_name = None  # use device name
    _attr_supported_features = _SUPPORTED_FEATURES
    _attr_source_list = list(CXA60_SOURCES.keys())
    _attr_assumed_state = True
    _attr_state = MediaPlayerState.OFF

    _codes = CXA60_CODES
    _sources = CXA60_SOURCES

    def __init__(
        self,
        entry: CambridgeAudioConfigEntry,
        ir_entity_id: str,
    ) -> None:
        """Initialise the media player."""
        self._ir_entity_id = ir_entity_id
        self._attr_unique_id = f"{entry.entry_id}_media_player"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Cambridge Audio {entry.data[CONF_MODEL]}",
            manufacturer="Cambridge Audio",
            model=entry.data[CONF_MODEL],
        )
        self._source: str | None = None
        self._muted: bool = False

    # ── Properties ──────────────────────────────────────────────────────────

    @property
    def is_volume_muted(self) -> bool:
        """Return true if volume is muted (assumed)."""
        return self._muted

    @property
    def source(self) -> str | None:
        """Return the current source (assumed)."""
        return self._source

    # ── Commands ─────────────────────────────────────────────────────────────

    async def _send(self, command_key: str) -> None:
        """Send an RC-5 command to the amplifier."""
        code = self._codes.get(command_key)
        if code is None:
            _LOGGER.error("Unknown command key: %s", command_key)
            return

        command = make_rc5_command(address=RC5_SYSTEM_CODE, command=code)
        await infrared.async_send_command(
            self.hass,
            self._ir_entity_id,
            command,
            context=self._context,
        )

    async def async_turn_on(self) -> None:
        """Turn the amplifier on."""
        await self._send("power_on")
        self._attr_state = MediaPlayerState.ON
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Turn the amplifier off."""
        await self._send("power_off")
        self._attr_state = MediaPlayerState.OFF
        self.async_write_ha_state()

    async def async_volume_up(self) -> None:
        """Send volume up."""
        await self._send("volume_up")

    async def async_volume_down(self) -> None:
        """Send volume down."""
        await self._send("volume_down")

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute or unmute the amplifier."""
        await self._send("mute_on" if mute else "mute_off")
        self._muted = mute
        self.async_write_ha_state()

    async def async_select_source(self, source: str) -> None:
        """Select an input source."""
        command_key = self._sources.get(source)
        if command_key is None:
            _LOGGER.error("Unknown source: %s", source)
            return
        await self._send(command_key)
        self._source = source
        self.async_write_ha_state()


class CambridgeAudioCXA80MediaPlayer(CambridgeAudioCXA60MediaPlayer):
    """Cambridge Audio CXA80 — extends CXA60 with Balanced A1 and Bluetooth."""

    _attr_source_list = list(CXA80_SOURCES.keys())
    _codes = CXA80_CODES
    _sources = CXA80_SOURCES
