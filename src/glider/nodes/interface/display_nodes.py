"""
Display Nodes - Read-only display widgets for the dashboard.
"""

from collections import deque
from typing import Any

from glider.nodes.base_node import (
    InterfaceNode,
    NodeCategory,
    NodeDefinition,
    PortDefinition,
)


class LabelNode(InterfaceNode):
    """Display a text label with a value."""

    definition = NodeDefinition(
        name="Label",
        category=NodeCategory.INTERFACE,
        description="Display a value as text",
        inputs=[
            PortDefinition(name="Value", data_type=object),
            PortDefinition(name="Format", data_type=str, default_value="{}"),
        ],
        outputs=[],
        color="#5a4a2d",
    )

    def __init__(self):
        super().__init__()
        self._label = "Value"
        self._display_text = ""

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        self._label = value

    @property
    def display_text(self) -> str:
        return self._display_text

    def update_event(self) -> None:
        value = self.get_input(0)
        format_str = self.get_input(1) or "{}"

        try:
            self._display_text = format_str.format(value)
        except Exception:
            self._display_text = str(value)

        self.notify_widget(self._display_text)

    def get_state(self) -> dict[str, Any]:
        state = super().get_state()
        state["label"] = self._label
        return state

    def set_state(self, state: dict[str, Any]) -> None:
        super().set_state(state)
        self._label = state.get("label", "Value")


class GaugeNode(InterfaceNode):
    """Display a gauge/meter widget."""

    definition = NodeDefinition(
        name="Gauge",
        category=NodeCategory.INTERFACE,
        description="Display value as a gauge/meter",
        inputs=[
            PortDefinition(name="Value", data_type=float, default_value=0.0),
            PortDefinition(name="Min", data_type=float, default_value=0.0),
            PortDefinition(name="Max", data_type=float, default_value=100.0),
        ],
        outputs=[],
        color="#5a4a2d",
    )

    def __init__(self):
        super().__init__()
        self._label = "Value"
        self._unit = ""
        self._warning_threshold = None
        self._danger_threshold = None

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        self._label = value

    @property
    def unit(self) -> str:
        return self._unit

    @unit.setter
    def unit(self, value: str) -> None:
        self._unit = value

    def update_event(self) -> None:
        value = float(self.get_input(0) or 0)
        min_val = float(self.get_input(1) or 0)
        max_val = float(self.get_input(2) or 100)

        # Calculate percentage
        if max_val > min_val:
            percent = (value - min_val) / (max_val - min_val) * 100
        else:
            percent = 0

        self.notify_widget(
            {
                "value": value,
                "percent": percent,
                "min": min_val,
                "max": max_val,
                "unit": self._unit,
                "label": self._label,
            }
        )

    def get_state(self) -> dict[str, Any]:
        state = super().get_state()
        state["label"] = self._label
        state["unit"] = self._unit
        state["warning_threshold"] = self._warning_threshold
        state["danger_threshold"] = self._danger_threshold
        return state

    def set_state(self, state: dict[str, Any]) -> None:
        super().set_state(state)
        self._label = state.get("label", "Value")
        self._unit = state.get("unit", "")
        self._warning_threshold = state.get("warning_threshold")
        self._danger_threshold = state.get("danger_threshold")


class ChartNode(InterfaceNode):
    """Display a real-time chart/graph."""

    definition = NodeDefinition(
        name="Chart",
        category=NodeCategory.INTERFACE,
        description="Display real-time chart of values",
        inputs=[
            PortDefinition(name="Value", data_type=float, default_value=0.0),
        ],
        outputs=[],
        color="#5a4a2d",
    )

    def __init__(self):
        super().__init__()
        self._label = "Chart"
        self._max_points = 100
        self._data: deque = deque(maxlen=100)
        self._y_min = None
        self._y_max = None

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        self._label = value

    @property
    def max_points(self) -> int:
        return self._max_points

    @max_points.setter
    def max_points(self, value: int) -> None:
        self._max_points = value
        self._data = deque(list(self._data), maxlen=value)

    @property
    def data(self) -> list[float]:
        return list(self._data)

    def clear_data(self) -> None:
        """Clear the chart data."""
        self._data.clear()

    def update_event(self) -> None:
        value = float(self.get_input(0) or 0)
        self._data.append(value)

        self.notify_widget(
            {
                "data": list(self._data),
                "label": self._label,
                "y_min": self._y_min,
                "y_max": self._y_max,
            }
        )

    def get_state(self) -> dict[str, Any]:
        state = super().get_state()
        state["label"] = self._label
        state["max_points"] = self._max_points
        state["y_min"] = self._y_min
        state["y_max"] = self._y_max
        return state

    def set_state(self, state: dict[str, Any]) -> None:
        super().set_state(state)
        self._label = state.get("label", "Chart")
        self._max_points = state.get("max_points", 100)
        self._y_min = state.get("y_min")
        self._y_max = state.get("y_max")


class LEDIndicatorNode(InterfaceNode):
    """Display an LED indicator."""

    definition = NodeDefinition(
        name="LED Indicator",
        category=NodeCategory.INTERFACE,
        description="Display an on/off LED indicator",
        inputs=[
            PortDefinition(name="State", data_type=bool, default_value=False),
        ],
        outputs=[],
        color="#5a4a2d",
    )

    def __init__(self):
        super().__init__()
        self._label = "LED"
        self._on_color = "#00ff00"  # Green
        self._off_color = "#333333"  # Dark gray

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        self._label = value

    @property
    def on_color(self) -> str:
        return self._on_color

    @on_color.setter
    def on_color(self, value: str) -> None:
        self._on_color = value

    @property
    def off_color(self) -> str:
        return self._off_color

    @off_color.setter
    def off_color(self, value: str) -> None:
        self._off_color = value

    def update_event(self) -> None:
        state = bool(self.get_input(0))
        color = self._on_color if state else self._off_color

        self.notify_widget(
            {
                "state": state,
                "color": color,
                "label": self._label,
            }
        )

    def get_state(self) -> dict[str, Any]:
        state = super().get_state()
        state["label"] = self._label
        state["on_color"] = self._on_color
        state["off_color"] = self._off_color
        return state

    def set_state(self, state: dict[str, Any]) -> None:
        super().set_state(state)
        self._label = state.get("label", "LED")
        self._on_color = state.get("on_color", "#00ff00")
        self._off_color = state.get("off_color", "#333333")
