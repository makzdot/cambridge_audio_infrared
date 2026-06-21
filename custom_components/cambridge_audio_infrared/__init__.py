"""Cambridge Audio Infrared integration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_CXN_SYSTEM_CODE,
    CONF_INFRARED_ENTITY_ID,
    CONF_INFRARED_RECEIVER_ENTITY_ID,
    CONF_MODEL,
    CXA60_CODES,
    CXA80_CODES,
    CXN_SYSTEM_CODE_DEFAULT,
    MODEL_CXA80,
    MODEL_CXN100,
    RC5_SYSTEM_CODE,
    resolve_cxn_codes,
)

PLATFORMS: list[Platform] = [
    Platform.MEDIA_PLAYER,
    Platform.BUTTON,
    Platform.EVENT,
]


@dataclass
class CambridgeAudioRuntimeData:
    """Runtime data for a configured Cambridge Audio device."""

    model: str
    emitter_entity_id: str
    receiver_entity_id: str | None
    # Resolved {command_key: (system_code, command)} for this device.
    codes: dict[str, tuple[int, int]]


type CambridgeAudioConfigEntry = ConfigEntry[CambridgeAudioRuntimeData]


def _build_codes(data: Mapping[str, Any]) -> dict[str, tuple[int, int]]:
    """Resolve the (system_code, command) table for the configured model."""
    model = data[CONF_MODEL]
    if model == MODEL_CXN100:
        base = int(data.get(CONF_CXN_SYSTEM_CODE, CXN_SYSTEM_CODE_DEFAULT))
        return resolve_cxn_codes(base)
    table = CXA80_CODES if model == MODEL_CXA80 else CXA60_CODES
    return {key: (RC5_SYSTEM_CODE, code) for key, code in table.items()}


async def async_setup_entry(
    hass: HomeAssistant, entry: CambridgeAudioConfigEntry
) -> bool:
    """Set up Cambridge Audio Infrared from a config entry."""
    entry.runtime_data = CambridgeAudioRuntimeData(
        model=entry.data[CONF_MODEL],
        emitter_entity_id=entry.data[CONF_INFRARED_ENTITY_ID],
        receiver_entity_id=entry.data.get(CONF_INFRARED_RECEIVER_ENTITY_ID),
        codes=_build_codes(entry.data),
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: CambridgeAudioConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
