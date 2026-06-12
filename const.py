"""Constants for the Cambridge Audio Infrared integration."""

DOMAIN = "cambridge_audio_infrared"

# Both CXA60 and CXA80 use RC-5 protocol, system code 16
RC5_SYSTEM_CODE = 16

CONF_INFRARED_ENTITY_ID = "infrared_entity_id"
CONF_MODEL = "model"

MODEL_CXA60 = "CXA60"
MODEL_CXA80 = "CXA80"

SUPPORTED_MODELS = [MODEL_CXA60, MODEL_CXA80]

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
