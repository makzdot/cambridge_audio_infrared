"""Media player platform for Cambridge Audio Infrared."""

from __future__ import annotations

import logging

from homeassistant.components import infrared
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_INFRARED_ENTITY_ID,
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

# Features supported by the CXA60 via IR
_SUPPORTED_FEATURES = (
    MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.SELECT_SOURCE
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cambridge Audio media player from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    model = data[CONF_MODEL]
    ir_entity_id = data[CONF_INFRARED_ENTITY_ID]

    if model == MODEL_CXA60:
        async_add_entities(
            [CambridgeAudioCXA60MediaPlayer(hass, entry, ir_entity_id)],
            update_before_add=True,
        )
    elif model == MODEL_CXA80:
        async_add_entities(
            [CambridgeAudioCXA80MediaPlayer(hass, entry, ir_entity_id)],
            update_before_add=True,
        )


class CambridgeAudioCXA60MediaPlayer(MediaPlayerEntity):
    """Representation of a Cambridge Audio CXA60 amplifier via IR."""

    _attr_has_entity_name = True
    _attr_name = None  # use device name
    _attr_supported_features = _SUPPORTED_FEATURES
    _attr_source_list = list(CXA60_SOURCES.keys())

    # Assumed state – IR is one-way, we track locally
    _attr_assumed_state = True
    _attr_state = MediaPlayerState.OFF

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        ir_entity_id: str,
    ) -> None:
        """Initialise the media player."""
        self._hass = hass
        self._entry = entry
        self._ir_entity_id = ir_entity_id
        self._attr_unique_id = f"{entry.entry_id}_media_player"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Cambridge Audio {entry.data[CONF_MODEL]}",
            "manufacturer": "Cambridge Audio",
            "model": entry.data[CONF_MODEL],
        }
        self._source: str | None = None
        self._muted: bool = False

    # ── Properties ──────────────────────────────────────────────────────────

    @property
    def state(self) -> MediaPlayerState:
        """Return the current state (assumed)."""
        return self._attr_state  # type: ignore[return-value]

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
        code = CXA60_CODES.get(command_key)
        if code is None:
            _LOGGER.error("Unknown command key: %s", command_key)
            return

        command = make_rc5_command(
            address=RC5_SYSTEM_CODE,
            command=code,
        )
        await infrared.async_send_command(
            self._hass,
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
        if mute:
            await self._send("mute_on")
        else:
            await self._send("mute_off")
        self._muted = mute
        self.async_write_ha_state()

    async def async_select_source(self, source: str) -> None:
        """Select an input source."""
        command_key = CXA60_SOURCES.get(source)
        if command_key is None:
            _LOGGER.error("Unknown source: %s", source)
            return
        await self._send(command_key)
        self._source = source
        self.async_write_ha_state()


class CambridgeAudioCXA80MediaPlayer(CambridgeAudioCXA60MediaPlayer):
    """Cambridge Audio CXA80 — extends CXA60 with Balanced A1 and Bluetooth."""

    _attr_source_list = list(CXA80_SOURCES.keys())

    def __init__(self, hass, entry, ir_entity_id) -> None:
        """Initialise the CXA80 media player."""
        super().__init__(hass, entry, ir_entity_id)

    async def _send(self, command_key: str) -> None:
        """Send an RC-5 command using the CXA80 code table."""
        code = CXA80_CODES.get(command_key)
        if code is None:
            _LOGGER.error("Unknown command key: %s", command_key)
            return
        command = make_rc5_command(address=RC5_SYSTEM_CODE, command=code)
        await infrared.async_send_command(
            self._hass,
            self._ir_entity_id,
            command,
            context=self._context,
        )

    async def async_select_source(self, source: str) -> None:
        """Select an input source."""
        command_key = CXA80_SOURCES.get(source)
        if command_key is None:
            _LOGGER.error("Unknown source: %s", source)
            return
        await self._send(command_key)
        self._source = source
        self.async_write_ha_state()
