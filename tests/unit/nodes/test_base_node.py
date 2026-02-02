"""
Tests for glider.nodes.base_node module.

Tests the base node classes and node system infrastructure.
"""

from unittest.mock import MagicMock

import pytest

from glider.nodes.base_node import (
    DataNode,
    ExecNode,
    GliderNode,
    HardwareNode,
    InterfaceNode,
    NodeCategory,
    NodeDefinition,
    PortDefinition,
    PortType,
)


class TestNodeCategory:
    """Tests for NodeCategory enum."""

    def test_category_values(self):
        """Test NodeCategory enum values."""
        assert NodeCategory.HARDWARE.value == "hardware"
        assert NodeCategory.LOGIC.value == "logic"
        assert NodeCategory.INTERFACE.value == "interface"

    def test_all_categories_exist(self):
        """Test that all expected categories exist."""
        categories = list(NodeCategory)
        assert len(categories) >= 3


class TestPortType:
    """Tests for PortType enum."""

    def test_port_type_values(self):
        """Test PortType enum values."""
        assert PortType.DATA is not None
        assert PortType.EXEC is not None


class TestPortDefinition:
    """Tests for PortDefinition dataclass."""

    def test_creation(self):
        """Test PortDefinition creation."""
        port = PortDefinition(
            name="input_1",
            port_type=PortType.DATA,
            data_type=float,
            default_value=0.0,
            description="An input port",
        )

        assert port.name == "input_1"
        assert port.port_type == PortType.DATA
        assert port.data_type is float
        assert port.default_value == 0.0
        assert port.description == "An input port"

    def test_default_values(self):
        """Test PortDefinition default values."""
        port = PortDefinition(name="port_1")

        assert port.port_type == PortType.DATA
        assert port.data_type is object
        assert port.default_value is None
        assert port.description == ""


class TestNodeDefinition:
    """Tests for NodeDefinition dataclass."""

    def test_creation(self):
        """Test NodeDefinition creation."""
        definition = NodeDefinition(
            name="TestNode",
            category=NodeCategory.LOGIC,
            description="A test node",
            inputs=[PortDefinition(name="in_1")],
            outputs=[PortDefinition(name="out_1")],
            color="#FF0000",
        )

        assert definition.name == "TestNode"
        assert definition.category == NodeCategory.LOGIC
        assert definition.description == "A test node"
        assert len(definition.inputs) == 1
        assert len(definition.outputs) == 1
        assert definition.color == "#FF0000"

    def test_default_values(self):
        """Test NodeDefinition default values."""
        definition = NodeDefinition(name="MinimalNode", category=NodeCategory.LOGIC)

        assert definition.description == ""
        assert definition.inputs == []
        assert definition.outputs == []
        assert definition.color == "#444444"


class ConcreteGliderNode(GliderNode):
    """Concrete implementation of GliderNode for testing."""

    definition = NodeDefinition(
        name="ConcreteNode",
        category=NodeCategory.LOGIC,
        inputs=[
            PortDefinition(name="input_a", default_value=0),
            PortDefinition(name="input_b", default_value=0),
        ],
        outputs=[
            PortDefinition(name="output"),
        ],
    )

    def update_event(self) -> None:
        """Process inputs."""
        a = self.get_input(0) or 0
        b = self.get_input(1) or 0
        self.set_output(0, a + b)


class TestGliderNode:
    """Tests for GliderNode base class."""

    def test_init(self):
        """Test GliderNode initialization."""
        node = ConcreteGliderNode()

        assert node.name == "ConcreteNode"
        assert node.category == NodeCategory.LOGIC
        assert len(node._inputs) == 2
        assert len(node._outputs) == 1

    def test_get_input(self):
        """Test getting input values."""
        node = ConcreteGliderNode()

        # Default values
        assert node.get_input(0) == 0
        assert node.get_input(1) == 0

        # Out of bounds returns None
        assert node.get_input(99) is None

    def test_set_input(self):
        """Test setting input values."""
        node = ConcreteGliderNode()

        node.set_input(0, 5)
        assert node.get_input(0) == 5

        node.set_input(1, 10)
        assert node.get_input(1) == 10

    def test_get_output(self):
        """Test getting output values."""
        node = ConcreteGliderNode()

        # Initial output is None
        assert node.get_output(0) is None

        # Out of bounds returns None
        assert node.get_output(99) is None

    def test_set_output(self):
        """Test setting output values."""
        node = ConcreteGliderNode()

        node.set_output(0, 42)
        assert node.get_output(0) == 42

    def test_update_event_processes_inputs(self):
        """Test that update_event processes inputs correctly."""
        node = ConcreteGliderNode()

        node._inputs[0] = 5
        node._inputs[1] = 7
        node.update_event()

        assert node.get_output(0) == 12

    def test_get_input_by_name(self):
        """Test getting input by name."""
        node = ConcreteGliderNode()
        node._inputs[0] = 100

        assert node.get_input_by_name("input_a") == 100
        assert node.get_input_by_name("nonexistent") is None

    def test_enable_disable(self):
        """Test enabling and disabling nodes."""
        node = ConcreteGliderNode()

        assert node.is_enabled is True

        node.disable()
        assert node.is_enabled is False

        node.enable()
        assert node.is_enabled is True

    def test_error_handling(self):
        """Test error state management."""
        node = ConcreteGliderNode()

        assert node.error is None

        node.set_error("Something went wrong")
        assert node.error == "Something went wrong"

        node.clear_error()
        assert node.error is None

    def test_device_binding(self):
        """Test binding and unbinding devices."""
        node = ConcreteGliderNode()
        mock_device = MagicMock()

        assert node.device is None

        node.bind_device(mock_device)
        assert node.device == mock_device

        node.unbind_device()
        assert node.device is None

    def test_visible_in_runner(self):
        """Test visible_in_runner property."""
        node = ConcreteGliderNode()

        assert node.visible_in_runner is False

        node.visible_in_runner = True
        assert node.visible_in_runner is True

    def test_state_management(self):
        """Test state get/set."""
        node = ConcreteGliderNode()

        node.set_state({"key": "value", "count": 42})
        state = node.get_state()

        assert state["key"] == "value"
        assert state["count"] == 42

    def test_output_callbacks(self):
        """Test output update callbacks."""
        node = ConcreteGliderNode()
        callback = MagicMock()

        node.on_output_update(callback)
        node.set_output(0, 100)

        callback.assert_called_once_with("output", 100)

    def test_to_dict(self):
        """Test node serialization."""
        node = ConcreteGliderNode()
        node._glider_id = "node_123"
        node._inputs[0] = 5
        node.set_state({"custom": "state"})

        data = node.to_dict()

        assert data["id"] == "node_123"
        assert data["node_type"] == "ConcreteNode"
        assert "state" in data


class ConcreteDataNode(DataNode):
    """Concrete DataNode for testing."""

    definition = NodeDefinition(
        name="AddNode",
        category=NodeCategory.LOGIC,
        inputs=[
            PortDefinition(name="a", default_value=0),
            PortDefinition(name="b", default_value=0),
        ],
        outputs=[
            PortDefinition(name="result"),
        ],
    )

    def process(self) -> None:
        """Add inputs."""
        a = self.get_input(0) or 0
        b = self.get_input(1) or 0
        self.set_output(0, a + b)


class TestDataNode:
    """Tests for DataNode class."""

    def test_update_event_calls_process(self):
        """Test that update_event calls process."""
        node = ConcreteDataNode()
        node._inputs[0] = 3
        node._inputs[1] = 4

        node.update_event()

        assert node.get_output(0) == 7

    def test_disabled_node_does_not_process(self):
        """Test that disabled nodes don't process."""
        node = ConcreteDataNode()
        node._inputs[0] = 3
        node._inputs[1] = 4
        node.disable()

        node.update_event()

        # Output should remain None (not processed)
        assert node.get_output(0) is None

    def test_error_handling_in_process(self):
        """Test that errors in process are caught."""
        node = ConcreteDataNode()

        # Create a node that will error
        def failing_process():
            raise ValueError("Test error")

        node.process = failing_process

        # Should not raise, but should set error
        node.update_event()
        assert node.error is not None


class ConcreteExecNode(ExecNode):
    """Concrete ExecNode for testing."""

    definition = NodeDefinition(
        name="DelayNode",
        category=NodeCategory.LOGIC,
    )

    async def execute(self) -> None:
        """Execute the node."""
        self.exec_output(0)


class TestExecNode:
    """Tests for ExecNode class."""

    def test_exec_callbacks(self):
        """Test execution output callbacks."""
        node = ConcreteExecNode()
        callback = MagicMock()

        node.on_exec(callback)
        node.exec_output(0)

        callback.assert_called_once_with(0)

    @pytest.mark.asyncio
    async def test_execute(self):
        """Test async execute method."""
        node = ConcreteExecNode()
        callback = MagicMock()
        node.on_exec(callback)

        await node.execute()

        callback.assert_called_once_with(0)


class TestInterfaceNode:
    """Tests for InterfaceNode class."""

    def test_default_visibility(self):
        """Test that interface nodes are visible by default."""

        class TestInterfaceNode(InterfaceNode):
            definition = NodeDefinition(
                name="TestInterface",
                category=NodeCategory.INTERFACE,
            )

            def update_event(self):
                pass

        node = TestInterfaceNode()
        assert node.visible_in_runner is True

    def test_widget_callbacks(self):
        """Test widget update callbacks."""

        class TestInterfaceNode(InterfaceNode):
            definition = NodeDefinition(
                name="TestInterface",
                category=NodeCategory.INTERFACE,
                inputs=[PortDefinition(name="value")],
            )

        node = TestInterfaceNode()
        callback = MagicMock()

        node.on_widget_update(callback)
        node.notify_widget(42)

        callback.assert_called_once_with(42)


class TestHardwareNode:
    """Tests for HardwareNode class."""

    @pytest.mark.asyncio
    async def test_execute_without_device_sets_error(self):
        """Test that executing without a bound device sets an error."""

        class TestHardwareNode(HardwareNode):
            async def hardware_operation(self):
                pass

        node = TestHardwareNode()
        await node.execute()

        assert node.error is not None
        assert "No device" in node.error

    @pytest.mark.asyncio
    async def test_execute_with_device(self):
        """Test executing with a bound device."""

        class TestHardwareNode(HardwareNode):
            async def hardware_operation(self):
                self.set_output(0, "success")

        node = TestHardwareNode()
        node.bind_device(MagicMock())

        await node.execute()

        assert node.error is None

    @pytest.mark.asyncio
    async def test_disabled_node_does_not_execute(self):
        """Test that disabled hardware nodes don't execute."""
        operation_called = False

        class TestHardwareNode(HardwareNode):
            async def hardware_operation(self):
                nonlocal operation_called
                operation_called = True

        node = TestHardwareNode()
        node.bind_device(MagicMock())
        node.disable()

        await node.execute()

        assert operation_called is False
