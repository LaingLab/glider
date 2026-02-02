import pytest

from glider.core.flow_engine import FlowEngine, FlowState


def test_flow_engine_init():
    """Test that FlowEngine initializes correctly."""
    engine = FlowEngine()
    assert engine.state == FlowState.STOPPED
    assert not engine.is_running
    assert len(engine.nodes) == 0


def test_node_registration():
    """Test that nodes can be registered."""

    class MockNode:
        pass

    FlowEngine.register_node("MockNode", MockNode)
    assert "MockNode" in FlowEngine.get_available_nodes()
    assert FlowEngine.get_node_class("MockNode") == MockNode


@pytest.mark.asyncio
async def test_flow_engine_start_stop():
    """Test starting and stopping the engine."""
    engine = FlowEngine()
    await engine.start()
    assert engine.state == FlowState.RUNNING
    assert engine.is_running

    await engine.stop()
    assert engine.state == FlowState.STOPPED
    assert not engine.is_running
