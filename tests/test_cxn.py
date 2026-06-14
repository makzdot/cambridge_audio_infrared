"""Tests for CXN100 IR code resolution and button definitions."""

import pytest

from custom_components.cambridge_audio_infrared.button import CXN_BUTTONS
from custom_components.cambridge_audio_infrared.const import (
    CXN_CODES,
    CXN_SYSTEM_CODES,
    resolve_cxn_codes,
)
from custom_components.cambridge_audio_infrared.rc5 import (
    decode_rc5,
    make_rc5_command,
)


@pytest.mark.parametrize("base", CXN_SYSTEM_CODES)
def test_resolve_uses_base_for_navigation(base):
    """Commands with a None system code take the configured base (24/28)."""
    table = resolve_cxn_codes(base)
    assert table["play_pause"] == (base, 24)
    assert table["home"] == (base, 12)


def test_resolve_keeps_fixed_system_codes():
    """Power/display/volume commands keep their own fixed system codes."""
    table = resolve_cxn_codes(24)
    assert table["power_on"] == (25, 14)       # shared CX power code
    assert table["power_toggle"] == (24, 2)    # CXN-only power toggle
    assert table["volume_up"] == (16, 16)      # pre-amp mode
    assert table["lcd_bright"] == (25, 18)


@pytest.mark.parametrize("base", CXN_SYSTEM_CODES)
def test_every_cxn_command_encodes_and_decodes(base):
    """Each resolved command encodes to a frame that decodes back identically."""
    for system, command in resolve_cxn_codes(base).values():
        frame = make_rc5_command(address=system, command=command).get_raw_timings()
        assert decode_rc5(frame) == (system, command, 0)


def test_buttons_map_to_known_codes():
    """Every CXN button references a command key that exists in CXN_CODES."""
    for description in CXN_BUTTONS:
        assert description.command_key in CXN_CODES
