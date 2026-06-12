"""RC-5 protocol encoder for Cambridge Audio devices.

The Philips RC-5 protocol encodes a 14-bit frame using Manchester (biphase)
encoding on a 36 kHz carrier:

  Bit layout (MSB first):
    bit 13  – start bit (always 1)
    bit 12  – field bit (1 for commands 0-63, 0 for extended commands 64-127)
    bit 11  – toggle bit (alternates on each key press)
    bits 10-6 – system address (5 bits)
    bits 5-0  – command (6 bits, or 7 bits using the inverted field bit)

Each bit cell is 1778 µs.  A logical '1' is space→mark; a logical '0' is
mark→space (biphase Mark encoding).

The infrared-protocols library from Home Assistant exposes an RC5Command class.
If it is available we use it; otherwise we fall back to a pure-Python encoder
that produces an equivalent list of (high_us, low_us) Timing pairs which can
be passed to a RAWInfraredCommand.
"""

from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)

# RC-5 timing constants (µs)
_T = 889   # half-bit period

try:
    # HA 2026.4+ infrared-protocols library
    from infrared_protocols import RC5Command  # type: ignore[import]
    _HAS_RC5_COMMAND = True
except ImportError:
    _HAS_RC5_COMMAND = False
    _LOGGER.debug(
        "infrared_protocols.RC5Command not available – using raw timing encoder"
    )


def make_rc5_command(address: int, command: int, toggle: bool = False):
    """Return an IR command object for the given RC-5 address and command.

    Uses RC5Command from the infrared-protocols library when available,
    otherwise falls back to a RAWInfraredCommand with manually encoded timings.
    """
    if _HAS_RC5_COMMAND:
        return RC5Command(address=address, command=command, toggle=toggle)

    # ── Fallback: encode RC-5 frame to raw timings ──────────────────────────
    from infrared_protocols import RAWInfraredCommand, Timing  # type: ignore[import]

    timings = _encode_rc5_raw(address, command, toggle)
    return RAWInfraredCommand(timings=timings, modulation=36000)


def _encode_rc5_raw(address: int, command: int, toggle: bool) -> list:
    """Encode an RC-5 frame as a list of Timing(high_us, low_us) pairs."""
    try:
        from infrared_protocols import Timing  # type: ignore[import]
    except ImportError:
        # Minimal fallback dataclass
        from dataclasses import dataclass

        @dataclass
        class Timing:  # type: ignore[no-redef]
            high_us: int
            low_us: int

    # Build 14-bit frame
    field_bit = 0 if command >= 64 else 1
    cmd6 = command & 0x3F  # lower 6 bits
    toggle_bit = 1 if toggle else 0

    bits: list[int] = []
    bits.append(1)           # start bit
    bits.append(field_bit)   # field / extended command bit
    bits.append(toggle_bit)  # toggle

    for i in range(4, -1, -1):
        bits.append((address >> i) & 1)

    for i in range(5, -1, -1):
        bits.append((cmd6 >> i) & 1)

    # Manchester encode: '1' → space then mark; '0' → mark then space
    # We build a list of pulse lengths (alternating mark/space starting with mark).
    pulses: list[int] = []
    level = 1  # start high

    # Pre-compute mark/space sequence from bit list
    # For biphase: each bit = two half-periods
    half_pulses: list[int] = []
    for bit in bits:
        if bit == 1:
            half_pulses += [0, 1]   # space then mark
        else:
            half_pulses += [1, 0]   # mark then space

    # Merge consecutive same-level half-periods
    merged: list[tuple[int, int]] = []  # (level, count_of_T)
    for hp in half_pulses:
        if merged and merged[-1][0] == hp:
            merged[-1] = (hp, merged[-1][1] + 1)
        else:
            merged.append((hp, 1))

    # Convert to Timing pairs: we pair consecutive mark+space
    timings: list = []
    i = 0
    while i < len(merged):
        if merged[i][0] == 1:  # mark
            high = merged[i][1] * _T
            low = merged[i + 1][1] * _T if i + 1 < len(merged) else _T
            timings.append(Timing(high_us=high, low_us=low))
            i += 2
        else:
            # Leading space – skip (shouldn't happen with RC-5)
            i += 1

    return timings
