"""Button platform for Cambridge Audio Infrared – one button per remote function."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import CambridgeAudioConfigEntry
from .const import (
    MODEL_CXA60,
    MODEL_CXA80,
    MODEL_CXN100,
)
from .entity import CambridgeAudioEntity
from .rc5 import make_rc5_command

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class CXAButtonEntityDescription(ButtonEntityDescription):
    """Describes a Cambridge Audio IR button entity."""

    command_key: str = ""


# ── Button definitions ───────────────────────────────────────────────────────
# Every entry maps to one button visible in the HA UI.

CXA60_BUTTONS: tuple[CXAButtonEntityDescription, ...] = (
    CXAButtonEntityDescription(key="power_toggle",    translation_key="power_toggle",        command_key="power_toggle"),
    CXAButtonEntityDescription(key="power_on",        translation_key="power_on",            command_key="power_on"),
    CXAButtonEntityDescription(key="power_off",       translation_key="power_off",           command_key="power_off"),
    # Volume / Mute
    CXAButtonEntityDescription(key="volume_up",       translation_key="volume_up",           command_key="volume_up"),
    CXAButtonEntityDescription(key="volume_down",     translation_key="volume_down",         command_key="volume_down"),
    CXAButtonEntityDescription(key="mute_toggle",     translation_key="mute_toggle",         command_key="mute_toggle"),
    CXAButtonEntityDescription(key="mute_on",         translation_key="mute_on",             command_key="mute_on"),
    CXAButtonEntityDescription(key="mute_off",        translation_key="mute_off",            command_key="mute_off"),
    # Display
    CXAButtonEntityDescription(key="brightness_toggle", translation_key="brightness_toggle", command_key="brightness_toggle"),
    CXAButtonEntityDescription(key="lcd_bright",      translation_key="lcd_bright",          command_key="lcd_bright"),
    CXAButtonEntityDescription(key="lcd_dim",         translation_key="lcd_dim",             command_key="lcd_dim"),
    CXAButtonEntityDescription(key="lcd_off",         translation_key="lcd_off",             command_key="lcd_off"),
    # Speaker output
    CXAButtonEntityDescription(key="speaker_ab",      translation_key="speaker_ab",         command_key="speaker_ab"),
    CXAButtonEntityDescription(key="speaker_a",       translation_key="speaker_a",           command_key="speaker_a"),
    CXAButtonEntityDescription(key="speaker_b",       translation_key="speaker_b",           command_key="speaker_b"),
    CXAButtonEntityDescription(key="speaker_select",  translation_key="speaker_select",      command_key="speaker_select"),
    # Direct mode
    CXAButtonEntityDescription(key="analogue_stereo_direct", translation_key="analogue_stereo_direct", command_key="analogue_stereo_direct"),
    # Source cycling
    CXAButtonEntityDescription(key="source_up",       translation_key="source_up",           command_key="source_up"),
    CXAButtonEntityDescription(key="source_down",     translation_key="source_down",         command_key="source_down"),
    # Named inputs
    CXAButtonEntityDescription(key="input_a1",        translation_key="input_a1",            command_key="input_a1"),
    CXAButtonEntityDescription(key="input_a2",        translation_key="input_a2",            command_key="input_a2"),
    CXAButtonEntityDescription(key="input_a3",        translation_key="input_a3",            command_key="input_a3"),
    CXAButtonEntityDescription(key="input_a4",        translation_key="input_a4",            command_key="input_a4"),
    CXAButtonEntityDescription(key="input_d1",        translation_key="input_d1",            command_key="input_d1"),
    CXAButtonEntityDescription(key="input_d2",        translation_key="input_d2",            command_key="input_d2"),
    CXAButtonEntityDescription(key="input_d3",        translation_key="input_d3",            command_key="input_d3"),
    CXAButtonEntityDescription(key="input_mp3",       translation_key="input_mp3",           command_key="input_mp3"),
    CXAButtonEntityDescription(key="input_usb_audio", translation_key="input_usb_audio",     command_key="input_usb_audio"),
    # Trigger outputs
    CXAButtonEntityDescription(key="trigger_a",       translation_key="trigger_a",           command_key="trigger_a"),
    CXAButtonEntityDescription(key="trigger_b",       translation_key="trigger_b",           command_key="trigger_b"),
    CXAButtonEntityDescription(key="trigger_c",       translation_key="trigger_c",           command_key="trigger_c"),
)

CXA80_EXTRA_BUTTONS: tuple[CXAButtonEntityDescription, ...] = (
    CXAButtonEntityDescription(key="input_a1_balanced", translation_key="input_a1_balanced", command_key="input_a1_balanced"),
    CXAButtonEntityDescription(key="input_bluetooth",   translation_key="input_bluetooth",   command_key="input_bluetooth"),
)

CXA80_BUTTONS = CXA60_BUTTONS + CXA80_EXTRA_BUTTONS

# CXN100 — a virtual remote for the network player. Codes span several RC-5
# system codes; see CXN_CODES in const.py.
CXN_BUTTONS: tuple[CXAButtonEntityDescription, ...] = (
    # Power
    CXAButtonEntityDescription(key="power_toggle", translation_key="power_toggle", command_key="power_toggle"),
    CXAButtonEntityDescription(key="power_on",     translation_key="power_on",     command_key="power_on"),
    CXAButtonEntityDescription(key="power_off",    translation_key="power_off",    command_key="power_off"),
    # Transport
    CXAButtonEntityDescription(key="play_pause",   translation_key="play_pause",   command_key="play_pause"),
    CXAButtonEntityDescription(key="stop",         translation_key="stop",         command_key="stop"),
    CXAButtonEntityDescription(key="skip_left",    translation_key="skip_left", command_key="skip_left"),
    CXAButtonEntityDescription(key="skip_right",   translation_key="skip_right",    command_key="skip_right"),
    CXAButtonEntityDescription(key="random",       translation_key="random",       command_key="random"),
    CXAButtonEntityDescription(key="repeat",       translation_key="repeat",       command_key="repeat"),
    # Navigation
    CXAButtonEntityDescription(key="home",         translation_key="home",         command_key="home"),
    CXAButtonEntityDescription(key="up",           translation_key="up",           command_key="up"),
    CXAButtonEntityDescription(key="down",         translation_key="down",         command_key="down"),
    CXAButtonEntityDescription(key="left",         translation_key="left",         command_key="left"),
    CXAButtonEntityDescription(key="right",        translation_key="right",        command_key="right"),
    CXAButtonEntityDescription(key="select",       translation_key="select",       command_key="select"),
    CXAButtonEntityDescription(key="return",       translation_key="return",       command_key="return"),
    CXAButtonEntityDescription(key="info",         translation_key="info",         command_key="info"),
    CXAButtonEntityDescription(key="more",         translation_key="more",         command_key="more"),
    CXAButtonEntityDescription(key="digital_input_menu", translation_key="digital_input_menu", command_key="digital_input_menu"),
    # Inputs
    CXAButtonEntityDescription(key="bluetooth",    translation_key="bluetooth",    command_key="bluetooth"),
    CXAButtonEntityDescription(key="usb_audio",    translation_key="usb_audio",    command_key="usb_audio"),
    CXAButtonEntityDescription(key="d1",           translation_key="d1",           command_key="d1"),
    CXAButtonEntityDescription(key="d2",           translation_key="d2",           command_key="d2"),
    # Presets
    CXAButtonEntityDescription(key="preset_1",     translation_key="preset_1",     command_key="preset_1"),
    CXAButtonEntityDescription(key="preset_2",     translation_key="preset_2",     command_key="preset_2"),
    CXAButtonEntityDescription(key="preset_3",     translation_key="preset_3",     command_key="preset_3"),
    CXAButtonEntityDescription(key="preset_4",     translation_key="preset_4",     command_key="preset_4"),
    CXAButtonEntityDescription(key="preset_5",     translation_key="preset_5",     command_key="preset_5"),
    CXAButtonEntityDescription(key="preset_6",     translation_key="preset_6",     command_key="preset_6"),
    CXAButtonEntityDescription(key="preset_7",     translation_key="preset_7",     command_key="preset_7"),
    CXAButtonEntityDescription(key="preset_8",     translation_key="preset_8",     command_key="preset_8"),
    # Volume / Mute (only active in Digital Pre-amp mode)
    CXAButtonEntityDescription(key="volume_up",    translation_key="volume_up",    command_key="volume_up"),
    CXAButtonEntityDescription(key="volume_down",  translation_key="volume_down",  command_key="volume_down"),
    CXAButtonEntityDescription(key="mute_toggle",  translation_key="mute_toggle",  command_key="mute_toggle"),
    # Display
    CXAButtonEntityDescription(key="brightness_toggle", translation_key="brightness_toggle", command_key="brightness_toggle"),
    CXAButtonEntityDescription(key="lcd_bright",   translation_key="lcd_bright",   command_key="lcd_bright"),
    CXAButtonEntityDescription(key="lcd_dim",      translation_key="lcd_dim",      command_key="lcd_dim"),
    CXAButtonEntityDescription(key="lcd_off",      translation_key="lcd_off",      command_key="lcd_off"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CambridgeAudioConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
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


class CambridgeAudioIRButton(
    CambridgeAudioEntity, InfraredEmitterConsumerEntity, ButtonEntity
):
    """A single Cambridge Audio remote button."""

    entity_description: CXAButtonEntityDescription

    def __init__(
        self,
        entry: CambridgeAudioConfigEntry,
        ir_entity_id: str,
        description: CXAButtonEntityDescription,
        codes: dict[str, tuple[int, int]],
    ) -> None:
        """Initialise the button."""
        super().__init__(entry, unique_id_suffix=f"button_{description.key}")
        self._infrared_emitter_entity_id = ir_entity_id
        self._codes = codes
        self.entity_description = description

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
        await self._send_command(
            make_rc5_command(address=system_code, command=code)
        )
