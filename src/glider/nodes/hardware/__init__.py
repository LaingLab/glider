"""
Hardware Nodes - Interface with physical devices.

These nodes are proxies for physical devices and hold references
to specific hardware driver instances.
"""

from glider.nodes.hardware.analog_nodes import (
    AnalogReadNode,
    PWMWriteNode,
)
from glider.nodes.hardware.device_nodes import (
    DeviceActionNode,
    DeviceReadNode,
)
from glider.nodes.hardware.digital_nodes import (
    DigitalReadNode,
    DigitalWriteNode,
)

__all__ = [
    "DigitalWriteNode",
    "DigitalReadNode",
    "AnalogReadNode",
    "PWMWriteNode",
    "DeviceActionNode",
    "DeviceReadNode",
]
