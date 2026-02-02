"""
Integration tests for experiment workflow.

Tests complete workflows from session creation through experiment execution.
"""

import json

from glider.core.experiment_session import (
    BoardConfig,
    DeviceConfig,
    ExperimentSession,
    SessionState,
)


class TestExperimentSessionWorkflow:
    """Integration tests for experiment session workflows."""

    def test_create_configure_save_load_workflow(self, temp_dir):
        """Test complete workflow: create, configure, save, load."""
        # 1. Create new session
        session = ExperimentSession()
        session.name = "Integration Test"

        # 2. Configure hardware
        session.add_board(BoardConfig(id="arduino_1", driver_type="arduino", port="/dev/ttyUSB0"))

        session.add_device(
            DeviceConfig(
                id="led_1",
                board_id="arduino_1",
                device_type="DigitalOutput",
                name="Status LED",
                pins={"signal": 13},
            )
        )

        session.add_device(
            DeviceConfig(
                id="sensor_1",
                board_id="arduino_1",
                device_type="AnalogInput",
                name="Temperature Sensor",
                pins={"analog": 0},
            )
        )

        # 3. Save session
        file_path = temp_dir / "test_session.json"
        data = session.to_dict()
        file_path.write_text(json.dumps(data, indent=2))

        assert file_path.exists()

        # 4. Load session
        loaded_data = json.loads(file_path.read_text())
        loaded_session = ExperimentSession.from_dict(loaded_data)

        # 5. Verify loaded session
        assert loaded_session.name == "Integration Test"
        assert len(loaded_session.hardware.boards) == 1
        assert len(loaded_session.hardware.devices) == 2

    def test_modify_and_track_dirty_state(self):
        """Test that modifications are tracked via dirty state."""
        session = ExperimentSession()

        # Mark clean to establish baseline
        session._mark_clean()
        assert session.is_dirty is False

        # Add board should mark dirty
        session.add_board(BoardConfig(id="b1", driver_type="arduino"))
        assert session.is_dirty is True

        # Mark clean
        session._mark_clean()
        assert session.is_dirty is False

        # Add device should mark dirty
        session.add_device(
            DeviceConfig(
                id="d1",
                board_id="b1",
                device_type="DigitalOutput",
                name="Device",
                pins={"signal": 13},
            )
        )
        assert session.is_dirty is True

        # Mark clean
        session._mark_clean()

        # Remove should mark dirty
        session.remove_device("d1")
        assert session.is_dirty is True

    def test_state_lifecycle(self):
        """Test session state lifecycle."""
        session = ExperimentSession()

        # Initial state
        assert session.state == SessionState.IDLE

        # Transition to running
        session.state = SessionState.RUNNING
        assert session.state == SessionState.RUNNING

        # Pause
        session.state = SessionState.PAUSED
        assert session.state == SessionState.PAUSED

        # Resume
        session.state = SessionState.RUNNING
        assert session.state == SessionState.RUNNING

        # Stop
        session.state = SessionState.STOPPING
        session.state = SessionState.IDLE
        assert session.state == SessionState.IDLE

    def test_clear_and_rebuild(self):
        """Test clearing and rebuilding a session."""
        session = ExperimentSession()
        session.name = "Clear Test"

        # Add some content
        session.add_board(BoardConfig(id="b1", driver_type="arduino"))
        session.add_device(
            DeviceConfig(
                id="d1",
                board_id="b1",
                device_type="DigitalOutput",
                name="Device",
                pins={"signal": 13},
            )
        )

        assert len(session.hardware.boards) == 1
        assert len(session.hardware.devices) == 1

        # Clear
        session.clear()

        assert len(session.hardware.boards) == 0
        assert len(session.hardware.devices) == 0

        # Rebuild
        session.add_board(BoardConfig(id="b2", driver_type="raspberry_pi"))
        session.add_device(
            DeviceConfig(
                id="d2", board_id="b2", device_type="PWMOutput", name="Motor", pins={"pwm": 12}
            )
        )

        assert len(session.hardware.boards) == 1
        assert len(session.hardware.devices) == 1


class TestSchemaIntegration:
    """Integration tests for schema serialization."""

    def test_complex_experiment_roundtrip(self, temp_dir):
        """Test roundtrip with a complex experiment configuration."""
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
        )

        # Create complex schema
        schema = ExperimentSchema(
            schema_version=SCHEMA_VERSION,
            metadata=MetadataSchema(
                name="Complex Experiment",
                description="A complex experiment with multiple components",
                author="Integration Test",
            ),
            hardware=HardwareConfigSchema(
                boards=[
                    BoardConfigSchema(id="arduino_1", type="telemetrix", port="/dev/ttyUSB0"),
                    BoardConfigSchema(id="pi_1", type="pigpio"),
                ],
                devices=[
                    DeviceConfigSchema(
                        id="led_status",
                        type="digital_output",
                        board_id="arduino_1",
                        pin=13,
                        name="Status LED",
                    ),
                    DeviceConfigSchema(
                        id="led_error",
                        type="digital_output",
                        board_id="arduino_1",
                        pin=12,
                        name="Error LED",
                    ),
                    DeviceConfigSchema(
                        id="motor_1", type="pwm", board_id="arduino_1", pin=9, name="Motor"
                    ),
                    DeviceConfigSchema(
                        id="temp_sensor",
                        type="analog_input",
                        board_id="pi_1",
                        pin=0,
                        name="Temperature",
                    ),
                ],
            ),
            flow=FlowConfigSchema(
                nodes=[
                    NodeSchema(
                        id="start",
                        type="StartExperiment",
                        title="Start",
                        position={"x": 0, "y": 100},
                    ),
                    NodeSchema(
                        id="init_led",
                        type="Output",
                        title="Init LED",
                        position={"x": 150, "y": 100},
                        properties={"device_id": "led_status"},
                    ),
                    NodeSchema(
                        id="loop",
                        type="Loop",
                        title="Loop",
                        position={"x": 300, "y": 100},
                        properties={"iterations": 10},
                    ),
                    NodeSchema(
                        id="read_temp",
                        type="Input",
                        title="Read Temp",
                        position={"x": 450, "y": 100},
                        properties={"device_id": "temp_sensor"},
                    ),
                    NodeSchema(
                        id="delay",
                        type="Delay",
                        title="Delay",
                        position={"x": 600, "y": 100},
                        properties={"duration": 1.0},
                    ),
                    NodeSchema(
                        id="end", type="EndExperiment", title="End", position={"x": 750, "y": 100}
                    ),
                ],
                connections=[
                    ConnectionSchema(
                        id="c1", from_node="start", from_port=0, to_node="init_led", to_port=0
                    ),
                    ConnectionSchema(
                        id="c2", from_node="init_led", from_port=0, to_node="loop", to_port=0
                    ),
                    ConnectionSchema(
                        id="c3", from_node="loop", from_port=1, to_node="read_temp", to_port=0
                    ),
                    ConnectionSchema(
                        id="c4", from_node="read_temp", from_port=0, to_node="delay", to_port=0
                    ),
                    ConnectionSchema(
                        id="c5", from_node="delay", from_port=0, to_node="loop", to_port=1
                    ),
                    ConnectionSchema(
                        id="c6", from_node="loop", from_port=0, to_node="end", to_port=0
                    ),
                ],
            ),
            dashboard=DashboardConfigSchema(),
        )

        # Serialize
        data = schema.to_dict()
        file_path = temp_dir / "complex_experiment.json"
        file_path.write_text(json.dumps(data, indent=2))

        # Verify file content
        assert file_path.exists()
        loaded_json = json.loads(file_path.read_text())
        assert loaded_json["schema_version"] == SCHEMA_VERSION
        assert len(loaded_json["hardware"]["boards"]) == 2
        assert len(loaded_json["hardware"]["devices"]) == 4
        assert len(loaded_json["flow"]["nodes"]) == 6
        assert len(loaded_json["flow"]["connections"]) == 6

        # Deserialize
        restored = ExperimentSchema.from_dict(loaded_json)

        # Verify restoration
        assert restored.metadata.name == schema.metadata.name
        assert len(restored.hardware.boards) == 2
        assert len(restored.hardware.devices) == 4
        assert len(restored.flow.nodes) == 6
        assert len(restored.flow.connections) == 6

        # Verify specific values
        arduino_board = next(b for b in restored.hardware.boards if b.id == "arduino_1")
        assert arduino_board.port == "/dev/ttyUSB0"

        delay_node = next(n for n in restored.flow.nodes if n.id == "delay")
        assert delay_node.properties["duration"] == 1.0


class TestZoneTrackingIntegration:
    """Integration tests for zone tracking system."""

    def test_zone_configuration_roundtrip(self, temp_dir):
        """Test zone configuration save/load roundtrip."""
        from glider.vision.zones import (
            Zone,
            ZoneConfiguration,
            ZoneShape,
        )

        # Create zone configuration
        config = ZoneConfiguration()

        # Add zones
        config.add_zone(
            Zone(
                id="start_zone",
                name="Start",
                shape=ZoneShape.RECTANGLE,
                vertices=[(0.0, 0.0), (0.3, 1.0)],
                color=(0, 255, 0),
            )
        )
        config.add_zone(
            Zone(
                id="middle_zone",
                name="Middle",
                shape=ZoneShape.RECTANGLE,
                vertices=[(0.35, 0.0), (0.65, 1.0)],
                color=(255, 255, 0),
            )
        )
        config.add_zone(
            Zone(
                id="end_zone",
                name="End",
                shape=ZoneShape.RECTANGLE,
                vertices=[(0.7, 0.0), (1.0, 1.0)],
                color=(255, 0, 0),
            )
        )
        config.config_width = 1920
        config.config_height = 1080

        # Save to file
        file_path = temp_dir / "zones.json"
        config.save(file_path)

        # Load from file
        loaded_config = ZoneConfiguration()
        loaded_config.load(file_path)

        # Verify
        assert len(loaded_config.zones) == 3
        assert loaded_config.zones[0].id == "start_zone"
        assert loaded_config.config_width == 1920

    def test_zone_tracker_basic(self):
        """Test basic zone tracker functionality."""
        from glider.vision.zones import (
            Zone,
            ZoneConfiguration,
            ZoneShape,
            ZoneTracker,
        )

        # Create configuration
        config = ZoneConfiguration()
        config.add_zone(
            Zone(
                id="zone_1",
                name="Zone 1",
                shape=ZoneShape.RECTANGLE,
                vertices=[(0.0, 0.0), (0.5, 0.5)],
                color=(0, 255, 0),
            )
        )
        config.add_zone(
            Zone(
                id="zone_2",
                name="Zone 2",
                shape=ZoneShape.RECTANGLE,
                vertices=[(0.5, 0.5), (1.0, 1.0)],
                color=(255, 0, 0),
            )
        )

        # Create tracker
        tracker = ZoneTracker()
        tracker.set_zone_configuration(config)

        # Update with no objects
        states = tracker.update([], frame_width=640, frame_height=480)

        assert len(states) == 2
        assert states["zone_1"].object_count == 0
        assert states["zone_2"].object_count == 0


class TestCalibrationIntegration:
    """Integration tests for camera calibration."""

    def test_calibration_save_load_workflow(self, temp_dir):
        """Test saving and loading calibration."""
        from glider.vision.calibration import CameraCalibration, LengthUnit

        # Create and configure calibration
        original = CameraCalibration()
        original.add_line(
            start=(0, 240),
            end=(640, 240),
            length=200.0,
            unit=LengthUnit.CENTIMETERS,
            resolution=(640, 480),
        )

        # Save
        file_path = temp_dir / "calibration.json"
        data = original.to_dict()
        file_path.write_text(json.dumps(data, indent=2))

        # Load
        loaded_data = json.loads(file_path.read_text())
        restored = CameraCalibration.from_dict(loaded_data)

        # Verify
        assert len(restored.lines) == 1
        assert restored.lines[0].length == 200.0
        assert restored.lines[0].unit == LengthUnit.CENTIMETERS
        assert restored.calibration_width == 640
