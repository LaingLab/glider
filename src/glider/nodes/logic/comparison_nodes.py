"""
Comparison Nodes - Threshold checks.
"""

from glider.nodes.base_node import (
    LogicNode,
    NodeCategory,
    NodeDefinition,
    PortDefinition,
)


class ThresholdNode(LogicNode):
    """Check if value exceeds threshold with hysteresis."""

    definition = NodeDefinition(
        name="Threshold",
        category=NodeCategory.LOGIC,
        description="Check if value exceeds threshold with optional hysteresis",
        inputs=[
            PortDefinition(name="Value", data_type=float, default_value=0.0),
            PortDefinition(name="Threshold", data_type=float, default_value=50.0),
            PortDefinition(name="Hysteresis", data_type=float, default_value=0.0),
        ],
        outputs=[
            PortDefinition(name="Above", data_type=bool),
            PortDefinition(name="Below", data_type=bool),
        ],
        color="#2d4a5a",
    )

    def __init__(self):
        super().__init__()
        self._last_state = False

    def process(self) -> None:
        value = float(self.get_input(0) or 0)
        threshold = float(self.get_input(1) or 50)
        hysteresis = float(self.get_input(2) or 0)

        if self._last_state:
            # Was above, check if now below (threshold - hysteresis)
            is_above = value > (threshold - hysteresis)
        else:
            # Was below, check if now above (threshold + hysteresis)
            is_above = value > (threshold + hysteresis)

        self._last_state = is_above
        self.set_output(0, is_above)
        self.set_output(1, not is_above)


class InRangeNode(LogicNode):
    """Check if value is within a range."""

    definition = NodeDefinition(
        name="In Range",
        category=NodeCategory.LOGIC,
        description="Check if value is within min/max range",
        inputs=[
            PortDefinition(name="Value", data_type=float, default_value=0.0),
            PortDefinition(name="Min", data_type=float, default_value=0.0),
            PortDefinition(name="Max", data_type=float, default_value=100.0),
        ],
        outputs=[
            PortDefinition(name="In Range", data_type=bool),
            PortDefinition(name="Out of Range", data_type=bool),
        ],
        color="#2d4a5a",
    )

    def process(self) -> None:
        value = float(self.get_input(0) or 0)
        min_val = float(self.get_input(1) or 0)
        max_val = float(self.get_input(2) or 100)

        in_range = min_val <= value <= max_val
        self.set_output(0, in_range)
        self.set_output(1, not in_range)
