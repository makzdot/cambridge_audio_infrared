"""RC-5 command builder for Cambridge Audio devices."""

from __future__ import annotations

from infrared_protocols import RC5Command  # type: ignore[import]


def make_rc5_command(address: int, command: int, toggle: bool = False) -> RC5Command:
    """Return an RC5Command for the given address and command."""
    return RC5Command(address=address, command=command, toggle=toggle)
