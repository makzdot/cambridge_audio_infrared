"""RC-5 command builder and decoder for Cambridge Audio devices."""

from __future__ import annotations

from infrared_protocols.commands.rc5 import RC5_HALF_BIT_US, RC5Command

# Timings within ±30% of the nominal half-bit period are accepted.
_TOLERANCE = 0.30

# A 14-bit RC-5 frame is 28 Manchester half-bits.
_FRAME_HALF_BITS = 28


def make_rc5_command(address: int, command: int, toggle: int = 0) -> RC5Command:
    """Return an RC5Command for the given address and command."""
    return RC5Command(address=address, command=command, toggle=toggle)


def _half_bit_units(value: int) -> int | None | str:
    """Classify a timing as 1 or 2 half-bits, a gap (None), or noise ("bad")."""
    units = int(round(abs(value) / RC5_HALF_BIT_US))
    if units in (1, 2):
        nominal = units * RC5_HALF_BIT_US
        if abs(abs(value) - nominal) > nominal * _TOLERANCE:
            return "bad"
        return units
    if units >= 3:
        return None  # gap / frame boundary
    return "bad"  # shorter than half a bit


def decode_rc5(timings: list[int]) -> tuple[int, int, int] | None:
    """Decode raw IR timings into an RC-5 (address, command, toggle) tuple.

    Timings are signed microseconds as produced by the infrared platform.
    The mark/space polarity is detected automatically (an inverting receiver
    reports bursts as negative values), a single frame is isolated by
    splitting on the idle gap, and the implicit leading/trailing idle space is
    restored. Returns None if the timings do not form a valid RC-5 frame.
    """
    if not timings:
        return None

    quantized = [_half_bit_units(v) for v in timings]

    # Isolate one frame: skip leading gaps, then read until the next gap.
    start = next((i for i, q in enumerate(quantized) if q is not None), None)
    if start is None:
        return None
    frame: list[tuple[int, int]] = []
    for value, units in zip(timings[start:], quantized[start:]):
        if units is None:  # gap -> end of this frame
            break
        if not isinstance(units, int):  # "bad" -> not a valid half-bit
            return None
        frame.append((value, units))

    if not frame:
        return None

    # The first burst of any IR frame is a mark (carrier on); its sign reveals
    # the polarity and so handles inverting receivers transparently.
    mark_is_positive = frame[0][0] > 0

    halves: list[int] = []
    for value, units in frame:
        is_mark = (value > 0) == mark_is_positive
        halves.extend([1 if is_mark else 0] * units)

    # RC-5's first bit opens with an idle space that isn't captured; restore
    # it. A frame ending on a space bit loses that space into the idle gap, so
    # pad to a whole number of bits.
    halves.insert(0, 0)
    if len(halves) % 2:
        halves.append(0)
    if len(halves) != _FRAME_HALF_BITS:
        return None

    # Manchester decode: space→mark is '1', mark→space is '0'.
    bits: list[int] = []
    for i in range(0, _FRAME_HALF_BITS, 2):
        pair = (halves[i], halves[i + 1])
        if pair == (0, 1):
            bits.append(1)
        elif pair == (1, 0):
            bits.append(0)
        else:
            return None

    # Frame: S1, S2, T, A4..A0, C5..C0. S1 is always 1.
    if bits[0] != 1:
        return None

    toggle = bits[2]
    address = 0
    for bit in bits[3:8]:
        address = (address << 1) | bit
    command = 0
    for bit in bits[8:14]:
        command = (command << 1) | bit

    # Extended RC-5: S2 carries the inverted command MSB (bit 6).
    if bits[1] == 0:
        command |= 0x40

    return address, command, toggle
