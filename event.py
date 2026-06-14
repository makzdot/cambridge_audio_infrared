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
    CONF_CXN_SYSTEM_CODE,
    CONF_INFRARED_RECEIVER_ENTITY_ID,
    CONF_MODEL,
    CXA60_CODES,
    CXA80_CODES,
    CXN_SYSTEM_CODE_DEFAULT,
    DOMAIN,
    MODEL_CXA60,
    MODEL_CXA80,
    MODEL_CXN100,
    RC5_SYSTEM_CODE,
    resolve_cxn_codes,
)
from .rc5 import decode_rc5

_LOGGER = logging.getLogger(__name__)


def _resolved_codes(data: dict) -> dict[str, tuple[int, int]] | None:
    """Return the {command_key: (system_code, command)} table for the model.

    Returns None for models that can't be decoded into events.
    """
    model = data[CONF_MODEL]
    if model == MODEL_CXA60:
        return {key: (RC5_SYSTEM_CODE, code) for key, code in CXA60_CODES.items()}
    if model == MODEL_CXA80:
        return {key: (RC5_SYSTEM_CODE, code) for key, code in CXA80_CODES.items()}
    if model == MODEL_CXN100:
        base = int(data.get(CONF_CXN_SYSTEM_CODE, CXN_SYSTEM_CODE_DEFAULT))
        return resolve_cxn_codes(base)
    return None


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

    codes = _resolved_codes(data)
    if codes is None:
        return
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
        codes: dict[str, tuple[int, int]],
    ) -> None:
        """Initialise the remote event entity."""
        self._infrared_receiver_entity_id = receiver_entity_id
        # Reverse map keyed by (system_code, command) so a single device only
        # reacts to its own RC-5 system code(s). The CXN's pre-amp volume/mute
        # share system code 16 with the CXA amplifiers, so those frames may
        # legitimately match both devices' event entities.
        self._signal_to_key = {
            (system, command): key for key, (system, command) in codes.items()
        }
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
            # Log the raw timings only on failure — that's when they're needed.
            _LOGGER.debug("Could not decode RC-5 from timings: %s", signal.timings)
            return
        address, command, toggle = decoded
        command_key = self._signal_to_key.get((address, command))
        if command_key is None:
            _LOGGER.debug(
                "No mapping for RC-5 system %d command %d", address, command
            )
            return
        _LOGGER.debug("Remote press: %s (toggle=%d)", command_key, toggle)
        self._trigger_event(command_key, {"toggle": toggle})
        self.async_write_ha_state()
