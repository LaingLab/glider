"""
Tests for glider.serialization.schema module.

Tests the experiment schema dataclasses and validation.
"""

import pytest

from glider.serialization.schema import (
    SCHEMA_VERSION,
    BoardConfigSchema,
    ConnectionSchema,
    DashboardConfigSchema,
    DeviceConfigSchema,
    ExperimentSchema,
    FlowConfigSchema,
    HardwareConfigSchema,
    MetadataSchema,
    NodeSchema,
    SchemaValidationError,
)


class TestSchemaVersion:
    """Tests for schema version constant."""

    def test_version_exists(self):
        """Test that SCHEMA_VERSION is defined."""
        assert SCHEMA_VERSION is not None
        assert isinstance(SCHEMA_VERSION, str)

    def test_version_format(self):
        """Test that version follows semver format."""
        parts = SCHEMA_VERSION.split(".")
        assert len(parts) >= 2  # At least major.minor


class TestMetadataSchema:
    """Tests for MetadataSchema dataclass."""

    def test_creation(self):
        """Test MetadataSchema creation."""
        metadata = MetadataSchema(
            name="Test Experiment", description="A test experiment", author="Test Author"
        )

        assert metadata.name == "Test Experiment"
        assert metadata.description == "A test experiment"
        assert metadata.author == "Test Author"

    def test_default_values(self):
        """Test MetadataSchema default values."""
        metadata = MetadataSchema(name="Test")

        assert metadata.name == "Test"
        assert metadata.description == ""
        assert metadata.author == ""
        assert metadata.created != ""  # Auto-generated

    def test_to_dict(self):
        """Test MetadataSchema serialization."""
        metadata = MetadataSchema(name="Test", description="Description", author="Author")

        data = metadata.to_dict()

        assert data["name"] == "Test"
        assert data["description"] == "Description"
        assert "created" in data
        assert "modified" in data

    def test_from_dict(self):
        """Test MetadataSchema deserialization."""
        data = {
            "name": "Loaded",
            "description": "Loaded desc",
            "author": "Loaded author",
            "created": "2024-01-01T00:00:00Z",
            "modified": "2024-01-02T00:00:00Z",
        }

        metadata = MetadataSchema.from_dict(data)

        assert metadata.name == "Loaded"
        assert metadata.description == "Loaded desc"


class TestNodeSchema:
    """Tests for NodeSchema dataclass."""

    def test_creation(self):
        """Test NodeSchema creation."""
        node = NodeSchema(
            id="node_1",
            type="Delay",
            title="Delay Node",
            position={"x": 100, "y": 200},
            properties={"duration": 1.0},
        )

        assert node.id == "node_1"
        assert node.type == "Delay"
        assert node.title == "Delay Node"
        assert node.position == {"x": 100, "y": 200}
        assert node.properties["duration"] == 1.0

    def test_to_dict(self):
        """Test NodeSchema serialization."""
        node = NodeSchema(
            id="node_1",
            type="Output",
            title="Output Node",
            position={"x": 50, "y": 75},
            properties={"value": True},
        )

        data = node.to_dict()

        assert data["id"] == "node_1"
        assert data["type"] == "Output"
        assert data["position"] == {"x": 50, "y": 75}
        assert data["properties"]["value"] is True

    def test_from_dict(self):
        """Test NodeSchema deserialization."""
        data = {
            "id": "n1",
            "type": "Loop",
            "title": "Loop Node",
            "position": {"x": 200, "y": 300},
            "properties": {"iterations": 10},
        }

        node = NodeSchema.from_dict(data)

        assert node.id == "n1"
        assert node.type == "Loop"
        assert node.position == {"x": 200, "y": 300}
        assert node.properties["iterations"] == 10

    def test_validation_missing_id(self):
        """Test that validation fails for missing ID."""
        with pytest.raises(SchemaValidationError):
            NodeSchema.from_dict({"type": "Delay", "title": "Test", "position": {"x": 0, "y": 0}})

    def test_validation_missing_type(self):
        """Test that validation fails for missing type."""
        with pytest.raises(SchemaValidationError):
            NodeSchema.from_dict({"id": "n1", "title": "Test", "position": {"x": 0, "y": 0}})


class TestConnectionSchema:
    """Tests for ConnectionSchema dataclass."""

    def test_creation(self):
        """Test ConnectionSchema creation."""
        connection = ConnectionSchema(
            id="conn_1", from_node="node_1", from_port=0, to_node="node_2", to_port=0
        )

        assert connection.id == "conn_1"
        assert connection.from_node == "node_1"
        assert connection.from_port == 0
        assert connection.to_node == "node_2"
        assert connection.to_port == 0

    def test_to_dict(self):
        """Test ConnectionSchema serialization."""
        connection = ConnectionSchema(id="c1", from_node="n1", from_port=0, to_node="n2", to_port=1)

        data = connection.to_dict()

        assert data["id"] == "c1"
        assert data["from_node"] == "n1"
        assert data["from_port"] == 0
        assert data["to_node"] == "n2"
        assert data["to_port"] == 1

    def test_from_dict(self):
        """Test ConnectionSchema deserialization."""
        data = {"id": "c1", "from_node": "a", "from_port": 0, "to_node": "b", "to_port": 1}

        connection = ConnectionSchema.from_dict(data)

        assert connection.from_node == "a"
        assert connection.to_node == "b"


class TestBoardConfigSchema:
    """Tests for BoardConfigSchema dataclass."""

    def test_creation(self):
        """Test BoardConfigSchema creation."""
        board = BoardConfigSchema(id="board_1", type="telemetrix", port="/dev/ttyUSB0")

        assert board.id == "board_1"
        assert board.type == "telemetrix"
        assert board.port == "/dev/ttyUSB0"

    def test_to_dict(self):
        """Test BoardConfigSchema serialization."""
        board = BoardConfigSchema(id="b1", type="pigpio", settings={"gpio_mode": "BCM"})

        data = board.to_dict()

        assert data["id"] == "b1"
        assert data["type"] == "pigpio"
        assert data["settings"]["gpio_mode"] == "BCM"

    def test_from_dict(self):
        """Test BoardConfigSchema deserialization."""
        data = {"id": "b1", "type": "telemetrix", "port": "COM3", "settings": {}}

        board = BoardConfigSchema.from_dict(data)

        assert board.id == "b1"
        assert board.port == "COM3"


class TestDeviceConfigSchema:
    """Tests for DeviceConfigSchema dataclass."""

    def test_creation(self):
        """Test DeviceConfigSchema creation."""
        device = DeviceConfigSchema(
            id="led_1", type="digital_output", board_id="board_1", pin=13, name="Status LED"
        )

        assert device.id == "led_1"
        assert device.board_id == "board_1"
        assert device.type == "digital_output"
        assert device.pin == 13

    def test_to_dict(self):
        """Test DeviceConfigSchema serialization."""
        device = DeviceConfigSchema(
            id="d1",
            type="analog_input",
            board_id="b1",
            pin=0,
            name="Sensor",
            settings={"smoothing": True},
        )

        data = device.to_dict()

        assert data["id"] == "d1"
        assert data["pin"] == 0
        assert data["settings"]["smoothing"] is True

    def test_from_dict(self):
        """Test DeviceConfigSchema deserialization."""
        data = {
            "id": "d1",
            "type": "servo",
            "board_id": "b1",
            "pin": 9,
            "settings": {"frequency": 1000},
        }

        device = DeviceConfigSchema.from_dict(data)

        assert device.id == "d1"
        assert device.type == "servo"


class TestFlowConfigSchema:
    """Tests for FlowConfigSchema dataclass."""

    def test_creation(self):
        """Test FlowConfigSchema creation."""
        flow = FlowConfigSchema(
            nodes=[
                NodeSchema(id="n1", type="Start", title="Start", position={"x": 0, "y": 0}),
                NodeSchema(id="n2", type="End", title="End", position={"x": 100, "y": 0}),
            ],
            connections=[
                ConnectionSchema(id="c1", from_node="n1", from_port=0, to_node="n2", to_port=0)
            ],
        )

        assert len(flow.nodes) == 2
        assert len(flow.connections) == 1

    def test_to_dict(self):
        """Test FlowConfigSchema serialization."""
        flow = FlowConfigSchema(
            nodes=[NodeSchema(id="n1", type="Delay", title="Delay", position={"x": 0, "y": 0})],
            connections=[],
        )

        data = flow.to_dict()

        assert "nodes" in data
        assert "connections" in data
        assert len(data["nodes"]) == 1

    def test_from_dict(self):
        """Test FlowConfigSchema deserialization."""
        data = {
            "nodes": [
                {
                    "id": "n1",
                    "type": "Start",
                    "title": "Start",
                    "position": {"x": 0, "y": 0},
                    "properties": {},
                }
            ],
            "connections": [],
        }

        flow = FlowConfigSchema.from_dict(data)

        assert len(flow.nodes) == 1
        assert flow.nodes[0].type == "Start"


class TestHardwareConfigSchema:
    """Tests for HardwareConfigSchema dataclass."""

    def test_creation(self):
        """Test HardwareConfigSchema creation."""
        hardware = HardwareConfigSchema(
            boards=[BoardConfigSchema(id="b1", type="telemetrix")],
            devices=[DeviceConfigSchema(id="d1", type="digital_output", board_id="b1", pin=13)],
        )

        assert len(hardware.boards) == 1
        assert len(hardware.devices) == 1

    def test_to_dict(self):
        """Test HardwareConfigSchema serialization."""
        hardware = HardwareConfigSchema(boards=[], devices=[])

        data = hardware.to_dict()

        assert "boards" in data
        assert "devices" in data


class TestExperimentSchema:
    """Tests for ExperimentSchema dataclass."""

    def test_creation(self):
        """Test ExperimentSchema creation."""
        schema = ExperimentSchema(
            schema_version=SCHEMA_VERSION,
            metadata=MetadataSchema(name="Test"),
            hardware=HardwareConfigSchema(boards=[], devices=[]),
            flow=FlowConfigSchema(nodes=[], connections=[]),
            dashboard=DashboardConfigSchema(),
        )

        assert schema.schema_version == SCHEMA_VERSION
        assert schema.metadata.name == "Test"

    def test_default_values(self):
        """Test ExperimentSchema default values."""
        schema = ExperimentSchema()

        assert schema.schema_version == SCHEMA_VERSION
        assert schema.metadata.name == "Untitled"

    def test_to_dict(self):
        """Test ExperimentSchema serialization."""
        schema = ExperimentSchema(
            schema_version=SCHEMA_VERSION,
            metadata=MetadataSchema(name="Full Test"),
            hardware=HardwareConfigSchema(
                boards=[BoardConfigSchema(id="b1", type="telemetrix")], devices=[]
            ),
            flow=FlowConfigSchema(
                nodes=[NodeSchema(id="n1", type="Start", title="Start", position={"x": 0, "y": 0})],
                connections=[],
            ),
            dashboard=DashboardConfigSchema(),
        )

        data = schema.to_dict()

        assert data["schema_version"] == SCHEMA_VERSION
        assert data["metadata"]["name"] == "Full Test"
        assert len(data["hardware"]["boards"]) == 1
        assert len(data["flow"]["nodes"]) == 1

    def test_from_dict(self):
        """Test ExperimentSchema deserialization."""
        data = {
            "schema_version": SCHEMA_VERSION,
            "metadata": {"name": "Loaded Experiment", "description": "Test"},
            "hardware": {"boards": [], "devices": []},
            "flow": {"nodes": [], "connections": []},
            "dashboard": {"widgets": [], "layout_mode": "vertical"},
        }

        schema = ExperimentSchema.from_dict(data)

        assert schema.metadata.name == "Loaded Experiment"
        assert schema.schema_version == SCHEMA_VERSION

    def test_roundtrip(self):
        """Test serialization roundtrip."""
        original = ExperimentSchema(
            schema_version=SCHEMA_VERSION,
            metadata=MetadataSchema(
                name="Roundtrip Test", description="Testing roundtrip serialization"
            ),
            hardware=HardwareConfigSchema(
                boards=[BoardConfigSchema(id="arduino_1", type="telemetrix", port="/dev/ttyUSB0")],
                devices=[
                    DeviceConfigSchema(
                        id="led_1",
                        type="digital_output",
                        board_id="arduino_1",
                        pin=13,
                        name="Status LED",
                    )
                ],
            ),
            flow=FlowConfigSchema(
                nodes=[
                    NodeSchema(
                        id="start", type="StartExperiment", title="Start", position={"x": 0, "y": 0}
                    ),
                    NodeSchema(
                        id="delay",
                        type="Delay",
                        title="Delay",
                        position={"x": 100, "y": 0},
                        properties={"duration": 1.0},
                    ),
                    NodeSchema(
                        id="end", type="EndExperiment", title="End", position={"x": 200, "y": 0}
                    ),
                ],
                connections=[
                    ConnectionSchema(
                        id="c1", from_node="start", from_port=0, to_node="delay", to_port=0
                    ),
                    ConnectionSchema(
                        id="c2", from_node="delay", from_port=0, to_node="end", to_port=0
                    ),
                ],
            ),
            dashboard=DashboardConfigSchema(),
        )

        data = original.to_dict()
        restored = ExperimentSchema.from_dict(data)

        assert restored.metadata.name == original.metadata.name
        assert len(restored.hardware.boards) == len(original.hardware.boards)
        assert len(restored.hardware.devices) == len(original.hardware.devices)
        assert len(restored.flow.nodes) == len(original.flow.nodes)
        assert len(restored.flow.connections) == len(original.flow.connections)


class TestSchemaValidationError:
    """Tests for SchemaValidationError exception."""

    def test_error_message(self):
        """Test SchemaValidationError message."""
        error = SchemaValidationError("Invalid field: name")

        assert "Invalid field: name" in str(error)

    def test_error_with_path(self):
        """Test SchemaValidationError with path context."""
        error = SchemaValidationError("Missing required field", path="hardware.boards[0].type")

        assert "hardware.boards[0].type" in str(error)
