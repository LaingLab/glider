"""
Math Nodes - Mathematical operations.
"""

from glider.nodes.base_node import (
    LogicNode,
    NodeCategory,
    NodeDefinition,
    PortDefinition,
)


class AddNode(LogicNode):
    """Add two numbers."""

    definition = NodeDefinition(
        name="Add",
        category=NodeCategory.LOGIC,
        description="Add two numbers: A + B",
        inputs=[
            PortDefinition(name="A", data_type=float, default_value=0.0),
            PortDefinition(name="B", data_type=float, default_value=0.0),
        ],
        outputs=[
            PortDefinition(name="Result", data_type=float),
        ],
        color="#2d4a5a",
    )

    def process(self) -> None:
        a = float(self.get_input(0) or 0)
        b = float(self.get_input(1) or 0)
        self.set_output(0, a + b)


class SubtractNode(LogicNode):
    """Subtract two numbers."""

    definition = NodeDefinition(
        name="Subtract",
        category=NodeCategory.LOGIC,
        description="Subtract two numbers: A - B",
        inputs=[
            PortDefinition(name="A", data_type=float, default_value=0.0),
            PortDefinition(name="B", data_type=float, default_value=0.0),
        ],
        outputs=[
            PortDefinition(name="Result", data_type=float),
        ],
        color="#2d4a5a",
    )

    def process(self) -> None:
        a = float(self.get_input(0) or 0)
        b = float(self.get_input(1) or 0)
        self.set_output(0, a - b)


class MultiplyNode(LogicNode):
    """Multiply two numbers."""

    definition = NodeDefinition(
        name="Multiply",
        category=NodeCategory.LOGIC,
        description="Multiply two numbers: A * B",
        inputs=[
            PortDefinition(name="A", data_type=float, default_value=0.0),
            PortDefinition(name="B", data_type=float, default_value=1.0),
        ],
        outputs=[
            PortDefinition(name="Result", data_type=float),
        ],
        color="#2d4a5a",
    )

    def process(self) -> None:
        a = float(self.get_input(0) or 0)
        b = float(self.get_input(1) or 1)
        self.set_output(0, a * b)


class DivideNode(LogicNode):
    """Divide two numbers."""

    definition = NodeDefinition(
        name="Divide",
        category=NodeCategory.LOGIC,
        description="Divide two numbers: A / B",
        inputs=[
            PortDefinition(name="A", data_type=float, default_value=0.0),
            PortDefinition(name="B", data_type=float, default_value=1.0),
        ],
        outputs=[
            PortDefinition(name="Result", data_type=float),
        ],
        color="#2d4a5a",
    )

    def process(self) -> None:
        a = float(self.get_input(0) or 0)
        b = float(self.get_input(1) or 1)
        if b == 0:
            self.set_error("Division by zero")
            self.set_output(0, 0.0)
        else:
            self.set_output(0, a / b)


class MapRangeNode(LogicNode):
    """Map a value from one range to another."""

    definition = NodeDefinition(
        name="Map Range",
        category=NodeCategory.LOGIC,
        description="Map value from input range to output range",
        inputs=[
            PortDefinition(name="Value", data_type=float, default_value=0.0),
            PortDefinition(name="In Min", data_type=float, default_value=0.0),
            PortDefinition(name="In Max", data_type=float, default_value=1023.0),
            PortDefinition(name="Out Min", data_type=float, default_value=0.0),
            PortDefinition(name="Out Max", data_type=float, default_value=255.0),
        ],
        outputs=[
            PortDefinition(name="Result", data_type=float),
        ],
        color="#2d4a5a",
    )

    def process(self) -> None:
        value = float(self.get_input(0) or 0)
        in_min = float(self.get_input(1) or 0)
        in_max = float(self.get_input(2) or 1)
        out_min = float(self.get_input(3) or 0)
        out_max = float(self.get_input(4) or 1)

        if in_max == in_min:
            self.set_output(0, out_min)
        else:
            result = (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
            self.set_output(0, result)


class ClampNode(LogicNode):
    """Clamp a value to a range."""

    definition = NodeDefinition(
        name="Clamp",
        category=NodeCategory.LOGIC,
        description="Clamp value between min and max",
        inputs=[
            PortDefinition(name="Value", data_type=float, default_value=0.0),
            PortDefinition(name="Min", data_type=float, default_value=0.0),
            PortDefinition(name="Max", data_type=float, default_value=100.0),
        ],
        outputs=[
            PortDefinition(name="Result", data_type=float),
        ],
        color="#2d4a5a",
    )

    def process(self) -> None:
        value = float(self.get_input(0) or 0)
        min_val = float(self.get_input(1) or 0)
        max_val = float(self.get_input(2) or 100)
        self.set_output(0, max(min_val, min(max_val, value)))
