"""
Board implementations for the GLIDER HAL.
"""

from glider.hal.boards.pi_gpio_board import PiGPIOBoard
from glider.hal.boards.telemetrix_board import TelemetrixBoard

__all__ = ["TelemetrixBoard", "PiGPIOBoard"]
