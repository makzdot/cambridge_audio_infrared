"""Constants for the Cambridge Audio Infrared integration."""

from __future__ import annotations

DOMAIN = "cambridge_audio_infrared"

# Both CXA60 and CXA80 use RC-5 protocol, system code 16
RC5_SYSTEM_CODE = 16

CONF_INFRARED_ENTITY_ID = "infrared_entity_id"
CONF_INFRARED_RECEIVER_ENTITY_ID = "infrared_receiver_entity_id"
CONF_MODEL = "model"
CONF_CXN_SYSTEM_CODE = "cxn_system_code"

MODEL_CXA60 = "CXA60"
MODEL_CXA80 = "CXA80"
MODEL_CXN100 = "CXN100"

SUPPORTED_MODELS = [MODEL_CXA60, MODEL_CXA80, MODEL_CXN100]

# ─── CXA60 IR command codes (RC-5, decimal) ────────────────────────────────

CXA60_CODES: dict[str, int] = {
    # Power
    "power_toggle": 12,
    "power_on": 14,
    "power_off": 15,
    # Volume / Mute
    "mute_toggle": 13,
    "mute_on": 50,
    "mute_off": 51,
    "volume_up": 16,
    "volume_down": 17,
    # Display
    "lcd_bright": 18,
    "brightness_toggle": 72,
    "lcd_dim": 19,
    "lcd_off": 71,
    # Speaker output
    "speaker_select": 20,
    "speaker_ab": 30,
    "speaker_a": 35,
    "speaker_b": 39,
    # Analogue direct
    "analogue_stereo_direct": 78,
    # Trigger outputs
    "trigger_a": 82,
    "trigger_b": 83,
    "trigger_c": 84,
    # Source selection (cycle)
    "source_up": 99,
    "source_down": 126,
    # Named inputs
    "input_a1": 100,
    "input_a2": 101,
    "input_a3": 102,
    "input_a4": 103,
    "input_d1": 105,
    "input_d2": 106,
    "input_d3": 107,
    "input_mp3": 108,
    "input_usb_audio": 114,
}

# Map source name → command key (used by media_player select_source)
CXA60_SOURCES: dict[str, str] = {
    "A1": "input_a1",
    "A2": "input_a2",
    "A3": "input_a3",
    "A4": "input_a4",
    "D1": "input_d1",
    "D2": "input_d2",
    "D3": "input_d3",
    "MP3": "input_mp3",
    "USB Audio": "input_usb_audio",
}

# ─── CXA80 IR command codes (RC-5, decimal) ────────────────────────────────
# The CXA80 shares all CXA60 codes and adds Balanced A1 and Bluetooth.

CXA80_CODES: dict[str, int] = {
    **CXA60_CODES,
    "input_a1_balanced": 104,  # CXA80 only
    "input_bluetooth": 115,    # CXA80 only
}

# Map source name → command key (used by media_player select_source)
CXA80_SOURCES: dict[str, str] = {
    **CXA60_SOURCES,
    "A1 Balanced": "input_a1_balanced",
    "Bluetooth": "input_bluetooth",
}

# ─── CXN100 IR command codes (RC-5, decimal) ───────────────────────────────
# Unlike the amplifiers, the CXN uses several RC-5 system codes. Source:
# https://www.cambridgeaudio.com/sites/default/files/compliance/doc/CXN%20IR%20Remote%20Control%20Codes.pdf

# The navigation/transport/input commands live on a base system code that the
# CXN exposes as switchable between 24 and 28 in its settings menu.
CXN_SYSTEM_CODES = [24, 28]
CXN_SYSTEM_CODE_DEFAULT = 24

# Power and display commands share system code 25 with other CX devices
# (e.g. a CXA amplifier will also react to these).
CXN_SHARED_SYSTEM_CODE = 25
# A CXN-only power toggle that will not also toggle a CXA amplifier.
CXN_POWER_TOGGLE_SYSTEM_CODE = 24
# Volume/mute only respond when the CXN is in Digital Pre-amp mode.
CXN_PREAMP_SYSTEM_CODE = 16

# Each entry is (system_code, command). A system_code of None means "use the
# configured base system code" (24 or 28), resolved at entity setup.
CXN_CODES: dict[str, tuple[int | None, int]] = {
    # Navigation
    "home": (None, 12),
    "up": (None, 13),
    "down": (None, 19),
    "left": (None, 16),
    "right": (None, 18),
    "select": (None, 17),
    "return": (None, 22),
    "info": (None, 28),
    "more": (None, 9),
    "digital_input_menu": (None, 120),
    # Transport
    "play_pause": (None, 24),
    "stop": (None, 27),
    "skip_left": (None, 23),
    "skip_right": (None, 25),
    "random": (None, 20),
    "repeat": (None, 21),
    # Inputs
    "bluetooth": (None, 31),
    "usb_audio": (None, 32),
    "d1": (None, 35),
    "d2": (None, 36),
    # Presets 1-8
    "preset_1": (None, 57),
    "preset_2": (None, 58),
    "preset_3": (None, 59),
    "preset_4": (None, 60),
    "preset_5": (None, 61),
    "preset_6": (None, 62),
    "preset_7": (None, 63),
    "preset_8": (None, 64),
    # Power (system code 25 — shared with other CX devices)
    "power_on": (CXN_SHARED_SYSTEM_CODE, 14),
    "power_off": (CXN_SHARED_SYSTEM_CODE, 15),
    # CXN-only power toggle (won't also toggle a CXA amplifier)
    "power_toggle": (CXN_POWER_TOGGLE_SYSTEM_CODE, 2),
    # Display (system code 25)
    "lcd_bright": (CXN_SHARED_SYSTEM_CODE, 18),
    "lcd_dim": (CXN_SHARED_SYSTEM_CODE, 19),
    "lcd_off": (CXN_SHARED_SYSTEM_CODE, 71),
    "brightness_toggle": (CXN_SHARED_SYSTEM_CODE, 72),
    # Volume / mute (only active in Digital Pre-amp mode)
    "mute_toggle": (CXN_PREAMP_SYSTEM_CODE, 13),
    "volume_up": (CXN_PREAMP_SYSTEM_CODE, 16),
    "volume_down": (CXN_PREAMP_SYSTEM_CODE, 17),
}


def resolve_cxn_codes(base_system_code: int) -> dict[str, tuple[int, int]]:
    """Return CXN_CODES with the base system code (24/28) filled in."""
    return {
        key: (base_system_code if system is None else system, command)
        for key, (system, command) in CXN_CODES.items()
    }
