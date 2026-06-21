"""Diagnostics support for the Cambridge Audio Infrared integration."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import CambridgeAudioConfigEntry
from .const import (
    CONF_CXN_SYSTEM_CODE,
    CONF_INFRARED_ENTITY_ID,
    CONF_INFRARED_RECEIVER_ENTITY_ID,
    CONF_MODEL,
)


def _entity_state(hass: HomeAssistant, entity_id: str | None) -> str | None:
    """Return the current state of an entity, or a marker if it's absent."""
    if not entity_id:
        return None
    state = hass.states.get(entity_id)
    return state.state if state else "not_found"


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: CambridgeAudioConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    emitter = entry.data.get(CONF_INFRARED_ENTITY_ID)
    receiver = entry.data.get(CONF_INFRARED_RECEIVER_ENTITY_ID)
    return {
        "model": entry.data.get(CONF_MODEL),
        "cxn_system_code": entry.data.get(CONF_CXN_SYSTEM_CODE),
        "emitter": {
            "entity_id": emitter,
            "state": _entity_state(hass, emitter),
        },
        "receiver": {
            "entity_id": receiver,
            "state": _entity_state(hass, receiver),
        },
    }
