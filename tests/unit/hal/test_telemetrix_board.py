from unittest.mock import patch

import pytest

from glider.hal.boards.telemetrix_board import TelemetrixBoard


@pytest.fixture
def mock_telemetrix():
    with patch("telemetrix_aio.telemetrix_aio.TelemetrixAIO") as mock:
        yield mock


@pytest.mark.asyncio
async def test_telemetrix_board_init():
    """Test TelemetrixBoard initialization."""
    board = TelemetrixBoard(port="COM3", board_type="uno")
    assert board.name == "Arduino Uno"
    assert board.board_type == "telemetrix"
    assert not board.is_connected


@pytest.mark.asyncio
async def test_telemetrix_board_capabilities():
    """Test board capabilities."""
    board = TelemetrixBoard()
    caps = board.capabilities
    assert caps.supports_analog
    assert 14 in caps.pins  # A0
    assert caps.pins[14].description == "A0"
