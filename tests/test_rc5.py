"""Tests for the RC-5 command builder."""

from unittest.mock import MagicMock, patch


def test_make_rc5_command_passes_args():
    """make_rc5_command forwards address, command, and toggle to RC5Command."""
    mock_cmd = MagicMock()
    mock_rc5 = MagicMock(return_value=mock_cmd)

    with patch(
        "custom_components.cambridge_audio_infrared.rc5.RC5Command", mock_rc5
    ):
        from custom_components.cambridge_audio_infrared.rc5 import make_rc5_command

        result = make_rc5_command(address=16, command=14, toggle=True)

    mock_rc5.assert_called_once_with(address=16, command=14, toggle=True)
    assert result is mock_cmd


def test_make_rc5_command_toggle_defaults_false():
    """toggle defaults to False when not supplied."""
    mock_rc5 = MagicMock()

    with patch(
        "custom_components.cambridge_audio_infrared.rc5.RC5Command", mock_rc5
    ):
        from custom_components.cambridge_audio_infrared.rc5 import make_rc5_command

        make_rc5_command(address=16, command=12)

    _, kwargs = mock_rc5.call_args
    assert kwargs["toggle"] is False
