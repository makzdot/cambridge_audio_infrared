"""Event platform for Cambridge Audio Infrared – remote presses via IR receiver."""

from __future__ import annotations

import logging

from homeassistant.components.event import EventDeviceClass, EventEntity
from homeassistant.components.infrared import (
    InfraredReceivedSignal,
    InfraredReceiverConsumerEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import CambridgeAudioConfigEntry
from .entity import CambridgeAudioEntity
from .rc5 import decode_rc5

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CambridgeAudioConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the remote event entity if an IR receiver was configured."""
    receiver_entity_id = entry.runtime_data.receiver_entity_id
    if not receiver_entity_id:
        return

    async_add_entities(
        [
            CambridgeAudioRemoteEvent(
                entry, receiver_entity_id, entry.runtime_data.codes
            )
        ]
    )


class CambridgeAudioRemoteEvent(
    CambridgeAudioEntity, InfraredReceiverConsumerEntity, EventEntity
):
    """Fires an event when a Cambridge Audio remote press is received via IR."""

    _attr_name = "Remote"
    _attr_device_class = EventDeviceClass.BUTTON

    def __init__(
        self,
        entry: CambridgeAudioConfigEntry,
        receiver_entity_id: str,
        codes: dict[str, tuple[int, int]],
    ) -> None:
        """Initialise the remote event entity."""
        super().__init__(entry, unique_id_suffix="remote")
        self._infrared_receiver_entity_id = receiver_entity_id
        # Reverse map keyed by (system_code, command) so a single device only
        # reacts to its own RC-5 system code(s). The CXN's pre-amp volume/mute
        # share system code 16 with the CXA amplifiers, so those frames may
        # legitimately match both devices' event entities.
        self._signal_to_key = {
            (system, command): key for key, (system, command) in codes.items()
        }
        self._attr_event_types = list(codes)

    @callback
    def _handle_signal(self, signal: InfraredReceivedSignal) -> None:
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
