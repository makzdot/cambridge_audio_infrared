"""RC-5 command builder and decoder for Cambridge Audio devices."""

from __future__ import annotations

from infrared_protocols.commands.rc5 import RC5_HALF_BIT_US, RC5Command

# Timings within ±25% of the nominal half-bit period are accepted.
_TOLERANCE = 0.25

# A 14-bit RC-5 frame is 28 Manchester half-bits. The encoder strips the
# idle leading space (S1 is always space→mark) and a trailing space, so a
# received frame holds 26-28 half-bits worth of timings.
_FRAME_HALF_BITS = 28


def make_rc5_command(address: int, command: int, toggle: int = 0) -> RC5Command:
    """Return an RC5Command for the given address and command."""
    return RC5Command(address=address, command=command, toggle=toggle)


def decode_rc5(timings: list[int]) -> tuple[int, int, int] | None:
    """Decode raw IR timings into an RC-5 (address, command, toggle) tuple.

    Timings are signed microseconds: positive for pulse (mark), negative for
    space, as produced by the infrared platform. Returns None if the timings
    do not form a valid RC-5 frame.
    """
    if not timings:
        return None

    # Expand timings into a sequence of half-bit levels. The leading idle
    # space of the start bit is stripped on transmit, so restore it.
    halves: list[int] = [0]
    for value in timings:
        duration = abs(value)
        for units in (1, 2):
            nominal = units * RC5_HALF_BIT_US
            if abs(duration - nominal) <= nominal * _TOLERANCE:
                halves.extend([1 if value > 0 else 0] * units)
                break
        else:
            return None

    # A frame ending in a logical '0' bit has its trailing space stripped.
    if len(halves) == _FRAME_HALF_BITS - 1:
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
