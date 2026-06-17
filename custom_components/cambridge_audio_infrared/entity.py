"""Base entity for the Cambridge Audio Infrared integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from . import CambridgeAudioConfigEntry
from .const import CONF_MODEL, DOMAIN


class CambridgeAudioEntity(Entity):
    """Base entity providing shared device info and unique id."""

    _attr_has_entity_name = True

    def __init__(
        self, entry: CambridgeAudioConfigEntry, unique_id_suffix: str
    ) -> None:
        """Initialise shared entity attributes."""
        model = entry.data[CONF_MODEL]
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Cambridge Audio {model}",
            manufacturer="Cambridge Audio",
            model=model,
        )
