"""RC-5 command builder for Cambridge Audio devices."""

from __future__ import annotations

from infrared_protocols.commands.rc5 import RC5Command


def make_rc5_command(address: int, command: int, toggle: int = 0) -> RC5Command:
    """Return an RC5Command for the given address and command."""
    return RC5Command(address=address, command=command, toggle=toggle)
