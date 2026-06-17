"""Button platform for Cambridge Audio Infrared – one button per remote function."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components import infrared
from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CambridgeAudioConfigEntry
from .const import (
    CONF_MODEL,
    DOMAIN,
    MODEL_CXA60,
    MODEL_CXA80,
    MODEL_CXN100,
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

CXA80_EXTRA_BUTTONS: tuple[CXAButtonEntityDescription, ...] = (
    CXAButtonEntityDescription(key="input_a1_balanced", name="Input A1 Balanced", command_key="input_a1_balanced"),
    CXAButtonEntityDescription(key="input_bluetooth",   name="Input Bluetooth",   command_key="input_bluetooth"),
)

CXA80_BUTTONS = CXA60_BUTTONS + CXA80_EXTRA_BUTTONS

# CXN100 — a virtual remote for the network player. Codes span several RC-5
# system codes; see CXN_CODES in const.py.
CXN_BUTTONS: tuple[CXAButtonEntityDescription, ...] = (
    # Power
    CXAButtonEntityDescription(key="power_toggle", name="Power Toggle", command_key="power_toggle"),
    CXAButtonEntityDescription(key="power_on",     name="Power On",     command_key="power_on"),
    CXAButtonEntityDescription(key="power_off",    name="Power Off",    command_key="power_off"),
    # Transport
    CXAButtonEntityDescription(key="play_pause",   name="Play/Pause",   command_key="play_pause"),
    CXAButtonEntityDescription(key="stop",         name="Stop",         command_key="stop"),
    CXAButtonEntityDescription(key="skip_left",    name="Skip Previous", command_key="skip_left"),
    CXAButtonEntityDescription(key="skip_right",   name="Skip Next",    command_key="skip_right"),
    CXAButtonEntityDescription(key="random",       name="Random",       command_key="random"),
    CXAButtonEntityDescription(key="repeat",       name="Repeat",       command_key="repeat"),
    # Navigation
    CXAButtonEntityDescription(key="home",         name="Home",         command_key="home"),
    CXAButtonEntityDescription(key="up",           name="Up",           command_key="up"),
    CXAButtonEntityDescription(key="down",         name="Down",         command_key="down"),
    CXAButtonEntityDescription(key="left",         name="Left",         command_key="left"),
    CXAButtonEntityDescription(key="right",        name="Right",        command_key="right"),
    CXAButtonEntityDescription(key="select",       name="Select",       command_key="select"),
    CXAButtonEntityDescription(key="return",       name="Return",       command_key="return"),
    CXAButtonEntityDescription(key="info",         name="Info",         command_key="info"),
    CXAButtonEntityDescription(key="more",         name="More",         command_key="more"),
    CXAButtonEntityDescription(key="digital_input_menu", name="Digital Input Menu", command_key="digital_input_menu"),
    # Inputs
    CXAButtonEntityDescription(key="bluetooth",    name="Bluetooth",    command_key="bluetooth"),
    CXAButtonEntityDescription(key="usb_audio",    name="USB Audio",    command_key="usb_audio"),
    CXAButtonEntityDescription(key="d1",           name="D1",           command_key="d1"),
    CXAButtonEntityDescription(key="d2",           name="D2",           command_key="d2"),
    # Presets
    CXAButtonEntityDescription(key="preset_1",     name="Preset 1",     command_key="preset_1"),
    CXAButtonEntityDescription(key="preset_2",     name="Preset 2",     command_key="preset_2"),
    CXAButtonEntityDescription(key="preset_3",     name="Preset 3",     command_key="preset_3"),
    CXAButtonEntityDescription(key="preset_4",     name="Preset 4",     command_key="preset_4"),
    CXAButtonEntityDescription(key="preset_5",     name="Preset 5",     command_key="preset_5"),
    CXAButtonEntityDescription(key="preset_6",     name="Preset 6",     command_key="preset_6"),
    CXAButtonEntityDescription(key="preset_7",     name="Preset 7",     command_key="preset_7"),
    CXAButtonEntityDescription(key="preset_8",     name="Preset 8",     command_key="preset_8"),
    # Volume / Mute (only active in Digital Pre-amp mode)
    CXAButtonEntityDescription(key="volume_up",    name="Volume Up",    command_key="volume_up"),
    CXAButtonEntityDescription(key="volume_down",  name="Volume Down",  command_key="volume_down"),
    CXAButtonEntityDescription(key="mute_toggle",  name="Mute Toggle",  command_key="mute_toggle"),
    # Display
    CXAButtonEntityDescription(key="brightness_toggle", name="Brightness Toggle", command_key="brightness_toggle"),
    CXAButtonEntityDescription(key="lcd_bright",   name="LCD Bright",   command_key="lcd_bright"),
    CXAButtonEntityDescription(key="lcd_dim",      name="LCD Dim",      command_key="lcd_dim"),
    CXAButtonEntityDescription(key="lcd_off",      name="LCD Off",      command_key="lcd_off"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CambridgeAudioConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cambridge Audio button entities."""
    model = entry.runtime_data.model
    if model == MODEL_CXA60:
        buttons = CXA60_BUTTONS
    elif model == MODEL_CXA80:
        buttons = CXA80_BUTTONS
    elif model == MODEL_CXN100:
        buttons = CXN_BUTTONS
    else:
        return

    ir_entity_id = entry.runtime_data.emitter_entity_id
    codes = entry.runtime_data.codes
    async_add_entities(
        [
            CambridgeAudioIRButton(entry, ir_entity_id, description, codes)
            for description in buttons
        ]
    )


class CambridgeAudioIRButton(ButtonEntity):
    """A single Cambridge Audio remote button."""

    entity_description: CXAButtonEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        entry: CambridgeAudioConfigEntry,
        ir_entity_id: str,
        description: CXAButtonEntityDescription,
        codes: dict[str, tuple[int, int]],
    ) -> None:
        """Initialise the button."""
        self._ir_entity_id = ir_entity_id
        self._codes = codes
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_button_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Cambridge Audio {entry.data[CONF_MODEL]}",
            manufacturer="Cambridge Audio",
            model=entry.data[CONF_MODEL],
        )

    async def async_press(self) -> None:
        """Send the IR command when the button is pressed."""
        entry = self._codes.get(self.entity_description.command_key)
        if entry is None:
            _LOGGER.error(
                "No IR code for command key '%s'",
                self.entity_description.command_key,
            )
            return

        system_code, code = entry
        command = make_rc5_command(address=system_code, command=code)

        await infrared.async_send_command(
            self.hass,
            self._ir_entity_id,
            command,
            context=self._context,
        )
