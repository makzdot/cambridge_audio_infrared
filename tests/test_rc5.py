"""Tests for the RC-5 command builder and decoder."""

from unittest.mock import MagicMock, patch

import pytest

from custom_components.cambridge_audio_infrared.const import (
    CXA80_CODES,
    RC5_SYSTEM_CODE,
)
from custom_components.cambridge_audio_infrared.rc5 import (
    decode_rc5,
    make_rc5_command,
)


def test_make_rc5_command_passes_args():
    """make_rc5_command forwards address, command, and toggle to RC5Command."""
    mock_cmd = MagicMock()
    mock_rc5 = MagicMock(return_value=mock_cmd)

    with patch(
        "custom_components.cambridge_audio_infrared.rc5.RC5Command", mock_rc5
    ):
        from custom_components.cambridge_audio_infrared.rc5 import make_rc5_command

        result = make_rc5_command(address=16, command=14, toggle=1)

    mock_rc5.assert_called_once_with(address=16, command=14, toggle=1)
    assert result is mock_cmd


def test_make_rc5_command_toggle_defaults_false():
    """toggle defaults to 0 when not supplied."""
    mock_rc5 = MagicMock()

    with patch(
        "custom_components.cambridge_audio_infrared.rc5.RC5Command", mock_rc5
    ):
        from custom_components.cambridge_audio_infrared.rc5 import make_rc5_command

        make_rc5_command(address=16, command=12)

    _, kwargs = mock_rc5.call_args
    assert kwargs["toggle"] == 0


# ── Decoder ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("command_key,code", sorted(CXA80_CODES.items()))
@pytest.mark.parametrize("toggle", [0, 1])
def test_decode_round_trip(command_key, code, toggle):
    """Every Cambridge Audio code survives an encode→decode round trip."""
    cmd = make_rc5_command(address=RC5_SYSTEM_CODE, command=code, toggle=toggle)
    assert decode_rc5(cmd.get_raw_timings()) == (RC5_SYSTEM_CODE, code, toggle)


def test_decode_tolerates_timing_jitter():
    """Real-world timings off by ±15% still decode."""
    cmd = make_rc5_command(address=RC5_SYSTEM_CODE, command=16)
    jittered = [
        int(t * 1.15) if i % 2 else int(t * 0.85)
        for i, t in enumerate(cmd.get_raw_timings())
    ]
    assert decode_rc5(jittered) == (RC5_SYSTEM_CODE, 16, 0)


@pytest.mark.parametrize(
    "timings",
    [
        [],                       # empty
        [9000, -4500, 560],       # NEC-style leader
        [889, -889],              # too short
        [889] * 100,              # too long
        [500, -500, 400],         # not RC-5 half-bit periods
    ],
)
def test_decode_rejects_invalid_signals(timings):
    """Garbage or foreign-protocol timings return None."""
    assert decode_rc5(timings) is None
