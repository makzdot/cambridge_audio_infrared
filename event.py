"""Event platform for Cambridge Audio Infrared – remote presses via IR receiver."""

from __future__ import annotations

import logging

from homeassistant.components import infrared
from homeassistant.components.event import EventDeviceClass, EventEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_INFRARED_RECEIVER_ENTITY_ID,
    CONF_MODEL,
    CXA60_CODES,
    CXA80_CODES,
    DOMAIN,
    MODEL_CXA80,
    RC5_SYSTEM_CODE,
)
from .rc5 import decode_rc5

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the remote event entity if an IR receiver was configured."""
    data = hass.data[DOMAIN][entry.entry_id]
    receiver_entity_id = data.get(CONF_INFRARED_RECEIVER_ENTITY_ID)
    if not receiver_entity_id:
        return

    model = data[CONF_MODEL]
    codes = CXA80_CODES if model == MODEL_CXA80 else CXA60_CODES
    async_add_entities(
        [CambridgeAudioRemoteEvent(entry, receiver_entity_id, codes)]
    )


class CambridgeAudioRemoteEvent(
    infrared.InfraredReceiverConsumerEntity, EventEntity
):
    """Fires an event when a Cambridge Audio remote press is received via IR."""

    _attr_has_entity_name = True
    _attr_name = "Remote"
    _attr_device_class = EventDeviceClass.BUTTON

    def __init__(
        self,
        entry: ConfigEntry,
        receiver_entity_id: str,
        codes: dict[str, int],
    ) -> None:
        """Initialise the remote event entity."""
        self._infrared_receiver_entity_id = receiver_entity_id
        self._code_to_key = {code: key for key, code in codes.items()}
        self._attr_event_types = list(codes)
        self._attr_unique_id = f"{entry.entry_id}_remote"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Cambridge Audio {entry.data[CONF_MODEL]}",
            manufacturer="Cambridge Audio",
            model=entry.data[CONF_MODEL],
        )

    @callback
    def _handle_signal(self, signal: infrared.InfraredReceivedSignal) -> None:
        """Decode a received IR signal and fire the matching event."""
        decoded = decode_rc5(signal.timings)
        if decoded is None:
            return
        address, command, toggle = decoded
        if address != RC5_SYSTEM_CODE:
            return
        command_key = self._code_to_key.get(command)
        if command_key is None:
            _LOGGER.debug("Received unmapped RC-5 command %d", command)
            return
        self._trigger_event(command_key, {"toggle": toggle})
        self.async_write_ha_state()
