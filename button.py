"""Button platform for Cambridge Audio Infrared – one button per remote function."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components import infrared
from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_INFRARED_ENTITY_ID,
    CONF_MODEL,
    CXA60_CODES,
    DOMAIN,
    MODEL_CXA60,
    RC5_SYSTEM_CODE,
)
from .rc5 import make_rc5_command

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class CXAButtonEntityDescription(ButtonEntityDescription):
    """Describes a Cambridge Audio IR button entity."""

    command_key: str = ""


# ── Button definitions ───────────────────────────────────────────────────────
# Every entry maps to one button visible in the HA UI.

CXA60_BUTTONS: tuple[CXAButtonEntityDescription, ...] = (
    # Power
    CXAButtonEntityDescription(key="power_toggle",    name="Power Toggle",        command_key="power_toggle"),
    CXAButtonEntityDescription(key="power_on",        name="Power On",            command_key="power_on"),
    CXAButtonEntityDescription(key="power_off",       name="Power Off",           command_key="power_off"),
    # Volume / Mute
    CXAButtonEntityDescription(key="volume_up",       name="Volume Up",           command_key="volume_up"),
    CXAButtonEntityDescription(key="volume_down",     name="Volume Down",         command_key="volume_down"),
    CXAButtonEntityDescription(key="mute_toggle",     name="Mute Toggle",         command_key="mute_toggle"),
    CXAButtonEntityDescription(key="mute_on",         name="Mute On",             command_key="mute_on"),
    CXAButtonEntityDescription(key="mute_off",        name="Mute Off",            command_key="mute_off"),
    # Display
    CXAButtonEntityDescription(key="brightness_toggle", name="Brightness Toggle", command_key="brightness_toggle"),
    CXAButtonEntityDescription(key="lcd_bright",      name="LCD Bright",          command_key="lcd_bright"),
    CXAButtonEntityDescription(key="lcd_dim",         name="LCD Dim",             command_key="lcd_dim"),
    CXAButtonEntityDescription(key="lcd_off",         name="LCD Off",             command_key="lcd_off"),
    # Speaker output
    CXAButtonEntityDescription(key="speaker_ab",      name="Speaker A+B",         command_key="speaker_ab"),
    CXAButtonEntityDescription(key="speaker_a",       name="Speaker A",           command_key="speaker_a"),
    CXAButtonEntityDescription(key="speaker_b",       name="Speaker B",           command_key="speaker_b"),
    CXAButtonEntityDescription(key="speaker_select",  name="Speaker Select",      command_key="speaker_select"),
    # Direct mode
    CXAButtonEntityDescription(key="analogue_stereo_direct", name="Analogue Stereo Direct", command_key="analogue_stereo_direct"),
    # Source cycling
    CXAButtonEntityDescription(key="source_up",       name="Source Up",           command_key="source_up"),
    CXAButtonEntityDescription(key="source_down",     name="Source Down",         command_key="source_down"),
    # Named inputs
    CXAButtonEntityDescription(key="input_a1",        name="Input A1",            command_key="input_a1"),
    CXAButtonEntityDescription(key="input_a2",        name="Input A2",            command_key="input_a2"),
    CXAButtonEntityDescription(key="input_a3",        name="Input A3",            command_key="input_a3"),
    CXAButtonEntityDescription(key="input_a4",        name="Input A4",            command_key="input_a4"),
    CXAButtonEntityDescription(key="input_d1",        name="Input D1",            command_key="input_d1"),
    CXAButtonEntityDescription(key="input_d2",        name="Input D2",            command_key="input_d2"),
    CXAButtonEntityDescription(key="input_d3",        name="Input D3",            command_key="input_d3"),
    CXAButtonEntityDescription(key="input_mp3",       name="Input MP3",           command_key="input_mp3"),
    CXAButtonEntityDescription(key="input_usb_audio", name="Input USB Audio",     command_key="input_usb_audio"),
    # Trigger outputs
    CXAButtonEntityDescription(key="trigger_a",       name="Trigger A",           command_key="trigger_a"),
    CXAButtonEntityDescription(key="trigger_b",       name="Trigger B",           command_key="trigger_b"),
    CXAButtonEntityDescription(key="trigger_c",       name="Trigger C",           command_key="trigger_c"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cambridge Audio button entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    model = data[CONF_MODEL]
    ir_entity_id = data[CONF_INFRARED_ENTITY_ID]

    if model == MODEL_CXA60:
        async_add_entities(
            [
                CambridgeAudioIRButton(hass, entry, ir_entity_id, description)
                for description in CXA60_BUTTONS
            ]
        )


class CambridgeAudioIRButton(ButtonEntity):
    """A single Cambridge Audio remote button."""

    entity_description: CXAButtonEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        ir_entity_id: str,
        description: CXAButtonEntityDescription,
    ) -> None:
        """Initialise the button."""
        self._hass = hass
        self._ir_entity_id = ir_entity_id
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_button_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Cambridge Audio {entry.data[CONF_MODEL]}",
            "manufacturer": "Cambridge Audio",
            "model": entry.data[CONF_MODEL],
        }

    async def async_press(self) -> None:
        """Send the IR command when the button is pressed."""
        code = CXA60_CODES.get(self.entity_description.command_key)
        if code is None:
            _LOGGER.error(
                "No IR code for command key '%s'",
                self.entity_description.command_key,
            )
            return

        command = make_rc5_command(address=RC5_SYSTEM_CODE, command=code)

        await infrared.async_send_command(
            self._hass,
            self._ir_entity_id,
            command,
            context=self._context,
        )
