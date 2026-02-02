"""
Experiment Tools

Tools for creating and modifying experiment flow graphs.
"""

import logging
from typing import TYPE_CHECKING, Any

from glider.agent.actions import ActionType, AgentAction
from glider.agent.llm_backend import ToolDefinition

if TYPE_CHECKING:
    from glider.core.glider_core import GliderCore

logger = logging.getLogger(__name__)


# Tool Definitions
EXPERIMENT_TOOLS: list[ToolDefinition] = [
    ToolDefinition(
        name="create_node",
        description="Create a new node in the experiment flow graph",
        parameters={
            "type": "object",
            "properties": {
                "node_type": {
                    "type": "string",
                    "description": "Type of node to create",
                    "enum": [
                        "StartExperiment",
                        "EndExperiment",
                        "Delay",
                        "Loop",
                        "WaitForInput",
                        "DigitalWrite",
                        "DigitalRead",
                        "AnalogRead",
                        "PWMWrite",
                        "ServoWrite",
                        "Branch",
                        "Compare",
                        "MathOp",
                    ],
                },
                "name": {"type": "string", "description": "Display name for the node (optional)"},
                "x": {
                    "type": "number",
                    "description": "X position on canvas (default: auto-layout)",
                },
                "y": {
                    "type": "number",
                    "description": "Y position on canvas (default: auto-layout)",
                },
                "properties": {
                    "type": "object",
                    "description": "Node-specific properties (e.g., delay_ms, device_id)",
                    "additionalProperties": True,
                },
            },
            "required": ["node_type"],
        },
    ),
    ToolDefinition(
        name="delete_node",
        description="Delete a node from the flow graph",
        parameters={
            "type": "object",
            "properties": {
                "node_id": {"type": "string", "description": "ID of the node to delete"}
            },
            "required": ["node_id"],
        },
    ),
    ToolDefinition(
        name="connect_nodes",
        description="Create a connection between two node ports",
        parameters={
            "type": "object",
            "properties": {
                "from_node": {"type": "string", "description": "ID or name of the source node"},
                "from_port": {
                    "type": "string",
                    "description": "Name of the output port (e.g., 'exec', 'value', 'next')",
                },
                "to_node": {"type": "string", "description": "ID or name of the target node"},
                "to_port": {
                    "type": "string",
                    "description": "Name of the input port (e.g., 'exec', 'value', 'body')",
                },
            },
            "required": ["from_node", "from_port", "to_node", "to_port"],
        },
    ),
    ToolDefinition(
        name="disconnect_nodes",
        description="Remove a connection between nodes",
        parameters={
            "type": "object",
            "properties": {
                "from_node": {"type": "string", "description": "ID or name of the source node"},
                "from_port": {"type": "string", "description": "Name of the output port"},
                "to_node": {"type": "string", "description": "ID or name of the target node"},
                "to_port": {"type": "string", "description": "Name of the input port"},
            },
            "required": ["from_node", "from_port", "to_node", "to_port"],
        },
    ),
    ToolDefinition(
        name="set_node_property",
        description="Set a property on a node",
        parameters={
            "type": "object",
            "properties": {
                "node_id": {"type": "string", "description": "ID or name of the node"},
                "property_name": {"type": "string", "description": "Name of the property to set"},
                "value": {"description": "Value to set (type depends on property)"},
            },
            "required": ["node_id", "property_name", "value"],
        },
    ),
    ToolDefinition(
        name="get_flow_state",
        description="Get the current state of the flow graph (nodes and connections)",
        parameters={
            "type": "object",
            "properties": {},
        },
    ),
    ToolDefinition(
        name="validate_flow",
        description="Validate the flow graph for errors",
        parameters={
            "type": "object",
            "properties": {},
        },
    ),
    ToolDefinition(
        name="clear_flow",
        description="Remove all nodes and connections from the flow graph (DESTRUCTIVE)",
        parameters={
            "type": "object",
            "properties": {
                "confirm": {
                    "type": "boolean",
                    "description": "Must be true to confirm this destructive action",
                }
            },
            "required": ["confirm"],
        },
    ),
]


class ExperimentToolExecutor:
    """Executes experiment-related tools."""

    def __init__(self, core: "GliderCore"):
        self._core = core
        self._auto_layout_x = 100
        self._auto_layout_y = 100

    def _get_next_position(self) -> tuple:
        """Get next auto-layout position."""
        pos = (self._auto_layout_x, self._auto_layout_y)
        self._auto_layout_x += 180
        if self._auto_layout_x > 800:
            self._auto_layout_x = 100
            self._auto_layout_y += 120
        return pos

    def reset_layout(self) -> None:
        """Reset auto-layout position."""
        self._auto_layout_x = 100
        self._auto_layout_y = 100

    async def execute(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool and return the result."""
        method = getattr(self, f"_execute_{tool_name}", None)
        if method is None:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        try:
            result = await method(args)
            return {"success": True, "result": result}
        except Exception as e:
            logger.exception(f"Tool execution failed: {tool_name}")
            return {"success": False, "error": str(e)}

    def create_action(self, tool_name: str, args: dict[str, Any]) -> AgentAction:
        """Create an action for a tool call."""
        action_types = {
            "create_node": ActionType.CREATE_NODE,
            "delete_node": ActionType.DELETE_NODE,
            "connect_nodes": ActionType.CONNECT_NODES,
            "disconnect_nodes": ActionType.DISCONNECT_NODES,
            "set_node_property": ActionType.SET_NODE_PROPERTY,
            "clear_flow": ActionType.CLEAR_FLOW,
            "validate_flow": ActionType.VALIDATE_FLOW,
            "get_flow_state": ActionType.GET_STATE,
        }

        descriptions = {
            "create_node": f"Create {args.get('node_type', 'node')} node",
            "delete_node": f"Delete node {args.get('node_id', '')}",
            "connect_nodes": f"Connect {args.get('from_node')}.{args.get('from_port')} → {args.get('to_node')}.{args.get('to_port')}",
            "disconnect_nodes": f"Disconnect {args.get('from_node')} from {args.get('to_node')}",
            "set_node_property": f"Set {args.get('property_name')} on {args.get('node_id')}",
            "clear_flow": "Clear all nodes and connections",
            "validate_flow": "Validate flow graph",
            "get_flow_state": "Get current flow state",
        }

        return AgentAction(
            action_type=action_types.get(tool_name, ActionType.GET_STATE),
            tool_name=tool_name,
            parameters=args,
            description=descriptions.get(tool_name, tool_name),
        )

    async def _execute_create_node(self, args: dict[str, Any]) -> dict[str, Any]:
        """Create a new node."""
        import uuid

        node_type = args["node_type"]
        name = args.get("name", node_type)

        # Get position
        x = args.get("x")
        y = args.get("y")
        if x is None or y is None:
            x, y = self._get_next_position()

        properties = args.get("properties", {})

        # Map friendly names to actual node class names
        node_type_map = {
            "StartExperiment": "StartExperimentNode",
            "EndExperiment": "EndExperimentNode",
            "Delay": "DelayNode",
            "Loop": "LoopNode",
            "WaitForInput": "WaitForInputNode",
            "DigitalWrite": "DigitalWriteNode",
            "DigitalRead": "DigitalReadNode",
            "AnalogRead": "AnalogReadNode",
            "PWMWrite": "PWMWriteNode",
            "ServoWrite": "ServoWriteNode",
            "Branch": "BranchNode",
            "Compare": "CompareNode",
            "MathOp": "MathOpNode",
        }

        actual_type = node_type_map.get(node_type, node_type)
        if not actual_type.endswith("Node"):
            actual_type = f"{actual_type}Node"

        # Generate unique node ID
        node_id = f"{node_type.lower()}_{uuid.uuid4().hex[:8]}"

        # Create the node through flow engine
        flow_engine = self._core.flow_engine

        # Get device_id if specified in properties
        device_id = properties.pop("device_id", None)

        flow_engine.create_node(
            node_id=node_id,
            node_type=actual_type,
            position=(x, y),
            state=properties if properties else None,
            device_id=device_id,
        )

        logger.info(f"Created node: {actual_type} ({node_id}) at ({x}, {y})")

        return {
            "node_id": node_id,
            "node_type": node_type,
            "name": name,
            "position": {"x": x, "y": y},
        }

    async def _execute_delete_node(self, args: dict[str, Any]) -> dict[str, Any]:
        """Delete a node."""
        node_id = args["node_id"]

        flow_engine = self._core.flow_engine
        success = flow_engine.delete_node(node_id)

        if success:
            logger.info(f"Deleted node: {node_id}")
            return {"deleted": node_id}
        else:
            raise ValueError(f"Node not found: {node_id}")

    async def _execute_connect_nodes(self, args: dict[str, Any]) -> dict[str, Any]:
        """Connect two nodes."""
        from_node = args["from_node"]
        from_port = args["from_port"]
        to_node = args["to_node"]
        to_port = args["to_port"]

        flow_engine = self._core.flow_engine
        connection_id = flow_engine.connect_nodes(from_node, from_port, to_node, to_port)

        logger.info(f"Connected: {from_node}.{from_port} → {to_node}.{to_port}")

        return {
            "connection_id": connection_id,
            "from": f"{from_node}.{from_port}",
            "to": f"{to_node}.{to_port}",
        }

    async def _execute_disconnect_nodes(self, args: dict[str, Any]) -> dict[str, Any]:
        """Disconnect nodes."""
        from_node = args["from_node"]
        from_port = args["from_port"]
        to_node = args["to_node"]
        to_port = args["to_port"]

        flow_engine = self._core.flow_engine
        success = flow_engine.disconnect_nodes(from_node, from_port, to_node, to_port)

        if success:
            logger.info(f"Disconnected: {from_node}.{from_port} → {to_node}.{to_port}")
            return {"disconnected": True}
        else:
            raise ValueError("Connection not found")

    async def _execute_set_node_property(self, args: dict[str, Any]) -> dict[str, Any]:
        """Set a node property."""
        node_id = args["node_id"]
        property_name = args["property_name"]
        value = args["value"]

        flow_engine = self._core.flow_engine
        success = flow_engine.set_node_property(node_id, property_name, value)

        if success:
            logger.info(f"Set {node_id}.{property_name} = {value}")
            return {"node_id": node_id, "property": property_name, "value": value}
        else:
            raise ValueError(f"Failed to set property on node: {node_id}")

    async def _execute_get_flow_state(self, args: dict[str, Any]) -> dict[str, Any]:
        """Get current flow state."""
        flow_engine = self._core.flow_engine

        nodes = flow_engine.get_nodes()
        connections = flow_engine.get_connections()

        return {
            "nodes": nodes,
            "connections": connections,
            "node_count": len(nodes),
            "connection_count": len(connections),
        }

    async def _execute_validate_flow(self, args: dict[str, Any]) -> dict[str, Any]:
        """Validate the flow graph."""
        flow_engine = self._core.flow_engine

        errors = flow_engine.validate()

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }

    async def _execute_clear_flow(self, args: dict[str, Any]) -> dict[str, Any]:
        """Clear all nodes and connections."""
        if not args.get("confirm", False):
            raise ValueError("Must confirm with confirm=true to clear flow")

        flow_engine = self._core.flow_engine
        flow_engine.clear()

        self.reset_layout()

        logger.info("Cleared flow graph")

        return {"cleared": True}
