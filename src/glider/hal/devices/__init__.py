"""
Device implementations for the GLIDER HAL.

Devices are higher-level abstractions that wrap board operations
into semantic actions.
"""

from glider.hal.base_device import (
    DEVICE_REGISTRY,
    AnalogInputDevice,
    BaseDevice,
    DeviceConfig,
    DigitalInputDevice,
    DigitalOutputDevice,
    MotorGovernorDevice,
    PWMOutputDevice,
    ServoDevice,
    create_device_from_dict,
)

__all__ = [
    "BaseDevice",
    "DeviceConfig",
    "DigitalOutputDevice",
    "DigitalInputDevice",
    "AnalogInputDevice",
    "PWMOutputDevice",
    "ServoDevice",
    "MotorGovernorDevice",
    "DEVICE_REGISTRY",
    "create_device_from_dict",
]
