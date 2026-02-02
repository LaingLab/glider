"""
Tests for glider.hal.pin_manager module.

Tests pin allocation, conflict detection, and validation.
"""

from unittest.mock import MagicMock

import pytest

from glider.hal.pin_manager import (
    InvalidPinError,
    PinAllocation,
    PinConflictError,
    PinManager,
)


class TestPinAllocation:
    """Tests for PinAllocation dataclass."""

    def test_creation(self):
        """Test PinAllocation creation."""
        alloc = PinAllocation(
            pin=13, device_id="led_1", device_name="Status LED", pin_role="output"
        )

        assert alloc.pin == 13
        assert alloc.device_id == "led_1"
        assert alloc.device_name == "Status LED"
        assert alloc.pin_role == "output"


class TestPinConflictError:
    """Tests for PinConflictError exception."""

    def test_error_message(self):
        """Test PinConflictError message format."""
        error = PinConflictError(pin=13, existing_device="led_1", new_device="led_2")

        assert "13" in str(error)
        assert "led_1" in str(error)
        assert "led_2" in str(error)

    def test_error_attributes(self):
        """Test PinConflictError attributes."""
        error = PinConflictError(pin=13, existing_device="led_1", new_device="led_2")

        assert error.pin == 13
        assert error.existing_device == "led_1"
        assert error.new_device == "led_2"


class TestInvalidPinError:
    """Tests for InvalidPinError exception."""

    def test_error_message(self):
        """Test InvalidPinError message format."""
        error = InvalidPinError(pin=99, requested_type="PWM", supported_types={"DIGITAL"})

        assert "99" in str(error)
        assert "PWM" in str(error)

    def test_error_attributes(self):
        """Test InvalidPinError attributes."""
        error = InvalidPinError(pin=99, requested_type="PWM", supported_types={"DIGITAL", "ANALOG"})

        assert error.pin == 99
        assert error.requested_type == "PWM"
        assert "DIGITAL" in error.supported_types


class TestPinManager:
    """Tests for PinManager class."""

    @pytest.fixture
    def mock_board(self):
        """Provide a mock board for PinManager."""
        board = MagicMock()
        # Set up mock capabilities
        board.capabilities.pins = {
            0: MagicMock(supported_types={"DIGITAL", "ANALOG"}),
            1: MagicMock(supported_types={"DIGITAL", "ANALOG"}),
            2: MagicMock(supported_types={"DIGITAL", "PWM"}),
            13: MagicMock(supported_types={"DIGITAL"}),
        }
        return board

    @pytest.fixture
    def pin_manager(self, mock_board):
        """Provide a fresh PinManager instance."""
        return PinManager(mock_board)

    @pytest.fixture
    def mock_device(self):
        """Provide a mock device."""
        device = MagicMock()
        device.id = "led_1"
        device.name = "Status LED"
        device.pins = {"output": 13}
        return device

    def test_init(self, pin_manager, mock_board):
        """Test PinManager initialization."""
        assert len(pin_manager.allocated_pins) == 0
        assert pin_manager.board == mock_board

    def test_allocate_pin(self, pin_manager, mock_device):
        """Test allocating a pin."""
        alloc = pin_manager.allocate_pin(pin=13, device=mock_device, pin_role="output")

        assert 13 in pin_manager.allocated_pins
        assert alloc.device_id == "led_1"
        assert alloc.pin_role == "output"

    def test_allocate_multiple_pins(self, pin_manager):
        """Test allocating multiple pins."""
        device1 = MagicMock()
        device1.id = "led_1"
        device1.name = "LED 1"

        device2 = MagicMock()
        device2.id = "led_2"
        device2.name = "LED 2"

        pin_manager.allocate_pin(pin=13, device=device1, pin_role="output")
        pin_manager.allocate_pin(pin=2, device=device2, pin_role="output")

        assert len(pin_manager.allocated_pins) == 2
        assert 13 in pin_manager.allocated_pins
        assert 2 in pin_manager.allocated_pins

    def test_allocate_duplicate_raises_conflict(self, pin_manager, mock_device):
        """Test that allocating an already-allocated pin raises PinConflictError."""
        pin_manager.allocate_pin(pin=13, device=mock_device, pin_role="output")

        device2 = MagicMock()
        device2.id = "led_2"
        device2.name = "LED 2"

        with pytest.raises(PinConflictError) as exc_info:
            pin_manager.allocate_pin(pin=13, device=device2, pin_role="output")

        assert exc_info.value.pin == 13
        assert "Status LED" in exc_info.value.existing_device

    def test_release_pin(self, pin_manager, mock_device):
        """Test releasing a pin."""
        pin_manager.allocate_pin(pin=13, device=mock_device, pin_role="output")
        assert 13 in pin_manager.allocated_pins

        released = pin_manager.release_pin(pin=13)
        assert 13 not in pin_manager.allocated_pins
        assert released.device_id == "led_1"

    def test_release_nonexistent_pin(self, pin_manager):
        """Test releasing a pin that isn't allocated returns None."""
        result = pin_manager.release_pin(pin=99)
        assert result is None

    def test_is_pin_available(self, pin_manager, mock_device):
        """Test checking pin availability."""
        assert pin_manager.is_pin_available(13) is True

        pin_manager.allocate_pin(pin=13, device=mock_device, pin_role="output")
        assert pin_manager.is_pin_available(13) is False

        pin_manager.release_pin(13)
        assert pin_manager.is_pin_available(13) is True

    def test_get_allocation(self, pin_manager, mock_device):
        """Test getting the allocation info for a pin."""
        pin_manager.allocate_pin(pin=13, device=mock_device, pin_role="output")

        alloc = pin_manager.get_allocation(13)
        assert alloc is not None
        assert alloc.device_id == "led_1"

        assert pin_manager.get_allocation(12) is None

    def test_get_pins_for_device(self, pin_manager):
        """Test getting all pins allocated to a device."""
        stepper = MagicMock()
        stepper.id = "stepper_1"
        stepper.name = "Stepper Motor"

        led = MagicMock()
        led.id = "led_1"
        led.name = "LED"

        pin_manager.allocate_pin(pin=13, device=stepper, pin_role="step")
        pin_manager.allocate_pin(pin=2, device=stepper, pin_role="dir")
        pin_manager.allocate_pin(pin=0, device=led, pin_role="output")

        stepper_allocs = pin_manager.get_pins_for_device("stepper_1")
        assert len(stepper_allocs) == 2

        led_allocs = pin_manager.get_pins_for_device("led_1")
        assert len(led_allocs) == 1

    def test_release_device_pins(self, pin_manager):
        """Test releasing all pins for a device."""
        stepper = MagicMock()
        stepper.id = "stepper_1"
        stepper.name = "Stepper"

        led = MagicMock()
        led.id = "led_1"
        led.name = "LED"

        pin_manager.allocate_pin(pin=13, device=stepper, pin_role="step")
        pin_manager.allocate_pin(pin=2, device=stepper, pin_role="dir")
        pin_manager.allocate_pin(pin=0, device=led, pin_role="output")

        released = pin_manager.release_device_pins("stepper_1")

        assert len(released) == 2
        assert 13 not in pin_manager.allocated_pins
        assert 2 not in pin_manager.allocated_pins
        assert 0 in pin_manager.allocated_pins  # led should remain

    def test_clear_all(self, pin_manager, mock_device):
        """Test clearing all pin allocations."""
        pin_manager.allocate_pin(pin=13, device=mock_device, pin_role="output")
        pin_manager.allocate_pin(pin=2, device=mock_device, pin_role="pwm")

        pin_manager.clear_all()

        assert len(pin_manager.allocated_pins) == 0

    def test_available_pins(self, pin_manager, mock_device):
        """Test available_pins property."""
        initial_available = pin_manager.available_pins
        assert 13 in initial_available

        pin_manager.allocate_pin(pin=13, device=mock_device, pin_role="output")

        available = pin_manager.available_pins
        assert 13 not in available

    def test_to_dict(self, pin_manager, mock_device):
        """Test serializing allocations to dictionary."""
        pin_manager.allocate_pin(pin=13, device=mock_device, pin_role="output")

        data = pin_manager.to_dict()

        assert 13 in data
        assert data[13]["device_id"] == "led_1"
        assert data[13]["pin_role"] == "output"

    def test_get_allocation_summary_empty(self, pin_manager):
        """Test allocation summary when empty."""
        summary = pin_manager.get_allocation_summary()
        assert "No pins allocated" in summary

    def test_get_allocation_summary_with_pins(self, pin_manager, mock_device):
        """Test allocation summary with allocated pins."""
        pin_manager.allocate_pin(pin=13, device=mock_device, pin_role="output")

        summary = pin_manager.get_allocation_summary()
        assert "Pin 13" in summary
        assert "Status LED" in summary

    def test_allocate_device_pins(self, pin_manager):
        """Test allocating all pins for a device at once."""
        device = MagicMock()
        device.id = "stepper_1"
        device.name = "Stepper Motor"
        device.pins = {"step": 13, "dir": 2}

        allocs = pin_manager.allocate_device_pins(device)

        assert len(allocs) == 2
        assert 13 in pin_manager.allocated_pins
        assert 2 in pin_manager.allocated_pins

    def test_allocate_device_pins_conflict(self, pin_manager, mock_device):
        """Test that allocate_device_pins fails if any pin is already allocated."""
        pin_manager.allocate_pin(pin=13, device=mock_device, pin_role="output")

        stepper = MagicMock()
        stepper.id = "stepper_1"
        stepper.name = "Stepper"
        stepper.pins = {"step": 13, "dir": 2}

        with pytest.raises(PinConflictError):
            pin_manager.allocate_device_pins(stepper)

        # Verify partial allocation didn't happen
        assert 2 not in pin_manager.allocated_pins
