"""
Knowledge Tools

Tools for explaining concepts and providing suggestions.
"""

import logging
from typing import TYPE_CHECKING, Any

from glider.agent.actions import ActionType, AgentAction
from glider.agent.llm_backend import ToolDefinition

if TYPE_CHECKING:
    from glider.core.glider_core import GliderCore

logger = logging.getLogger(__name__)


# Tool Definitions
KNOWLEDGE_TOOLS: list[ToolDefinition] = [
    ToolDefinition(
        name="explain_node",
        description="Get detailed explanation of a node type",
        parameters={
            "type": "object",
            "properties": {
                "node_type": {"type": "string", "description": "Type of node to explain"}
            },
            "required": ["node_type"],
        },
    ),
    ToolDefinition(
        name="explain_concept",
        description="Explain a GLIDER concept",
        parameters={
            "type": "object",
            "properties": {
                "concept": {
                    "type": "string",
                    "description": "Concept to explain (e.g., 'execution flow', 'data flow', 'devices')",
                }
            },
            "required": ["concept"],
        },
    ),
    ToolDefinition(
        name="get_examples",
        description="Get example experiments",
        parameters={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Category of examples",
                    "enum": ["basic", "sensors", "motors", "advanced", "all"],
                }
            },
        },
    ),
    ToolDefinition(
        name="suggest_flow",
        description="Suggest a flow design for a task",
        parameters={
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Description of what the experiment should do",
                }
            },
            "required": ["task"],
        },
    ),
    ToolDefinition(
        name="troubleshoot",
        description="Help diagnose and fix issues",
        parameters={
            "type": "object",
            "properties": {
                "issue": {"type": "string", "description": "Description of the problem"},
                "error_message": {"type": "string", "description": "Any error message received"},
            },
            "required": ["issue"],
        },
    ),
]


# Node documentation
NODE_DOCS = {
    "StartExperiment": {
        "description": "Entry point for the experiment. Triggers when the experiment starts running.",
        "category": "Experiment",
        "inputs": [],
        "outputs": [
            {"name": "exec", "type": "execution", "description": "Triggers when experiment starts"}
        ],
        "properties": [],
        "tips": [
            "Every experiment needs exactly one StartExperiment node",
            "Connect the 'exec' output to the first action in your flow",
        ],
    },
    "EndExperiment": {
        "description": "Cleanly ends the experiment and stops all hardware.",
        "category": "Experiment",
        "inputs": [
            {
                "name": "exec",
                "type": "execution",
                "description": "Triggers the end of the experiment",
            }
        ],
        "outputs": [],
        "properties": [],
        "tips": [
            "Use this to ensure proper cleanup",
            "Optional - experiment also ends when flow completes",
        ],
    },
    "Delay": {
        "description": "Pauses execution for a specified duration.",
        "category": "Experiment",
        "inputs": [
            {"name": "exec", "type": "execution", "description": "Triggers the delay"},
            {
                "name": "duration",
                "type": "number",
                "description": "Duration in milliseconds (optional, overrides property)",
            },
        ],
        "outputs": [
            {"name": "exec", "type": "execution", "description": "Triggers after delay completes"}
        ],
        "properties": [
            {
                "name": "delay_ms",
                "type": "number",
                "default": 1000,
                "description": "Delay duration in milliseconds",
            }
        ],
        "tips": [
            "Use for timing between actions",
            "Can be connected to a data source for dynamic delays",
        ],
    },
    "Loop": {
        "description": "Repeats a section of the flow a specified number of times.",
        "category": "Experiment",
        "inputs": [
            {"name": "exec", "type": "execution", "description": "Triggers the loop to start"},
            {
                "name": "count",
                "type": "number",
                "description": "Number of iterations (optional, overrides property)",
            },
        ],
        "outputs": [
            {"name": "body", "type": "execution", "description": "Triggers for each iteration"},
            {
                "name": "complete",
                "type": "execution",
                "description": "Triggers when all iterations are done",
            },
            {"name": "index", "type": "number", "description": "Current iteration index (0-based)"},
        ],
        "properties": [
            {
                "name": "iterations",
                "type": "number",
                "default": 10,
                "description": "Number of times to repeat",
            }
        ],
        "tips": [
            "Connect 'body' to the nodes you want to repeat",
            "The last node in the loop should NOT connect back - it's automatic",
            "Use 'complete' to continue after all iterations",
        ],
    },
    "DigitalWrite": {
        "description": "Sets a digital output pin HIGH or LOW.",
        "category": "Hardware",
        "inputs": [
            {"name": "exec", "type": "execution", "description": "Triggers the write operation"},
            {
                "name": "value",
                "type": "boolean",
                "description": "Value to write (optional, overrides property)",
            },
        ],
        "outputs": [
            {"name": "exec", "type": "execution", "description": "Triggers after write completes"}
        ],
        "properties": [
            {"name": "device_id", "type": "string", "description": "ID of the device to control"},
            {
                "name": "value",
                "type": "boolean",
                "default": True,
                "description": "HIGH (true) or LOW (false)",
            },
        ],
        "tips": [
            "Use for LEDs, relays, buzzers",
            "Must have a DigitalOutput device configured first",
        ],
    },
    "DigitalRead": {
        "description": "Reads the current state of a digital input pin.",
        "category": "Hardware",
        "inputs": [
            {"name": "exec", "type": "execution", "description": "Triggers the read operation"}
        ],
        "outputs": [
            {"name": "exec", "type": "execution", "description": "Triggers after read completes"},
            {
                "name": "value",
                "type": "boolean",
                "description": "The read value (true = HIGH, false = LOW)",
            },
        ],
        "properties": [
            {"name": "device_id", "type": "string", "description": "ID of the device to read"}
        ],
        "tips": [
            "Use for buttons, switches, digital sensors",
            "Connect 'value' output to a Branch node for conditional logic",
        ],
    },
    "AnalogRead": {
        "description": "Reads an analog value from a pin (0-1023).",
        "category": "Hardware",
        "inputs": [
            {"name": "exec", "type": "execution", "description": "Triggers the read operation"}
        ],
        "outputs": [
            {"name": "exec", "type": "execution", "description": "Triggers after read completes"},
            {"name": "value", "type": "number", "description": "The analog value (0-1023)"},
        ],
        "properties": [
            {"name": "device_id", "type": "string", "description": "ID of the device to read"}
        ],
        "tips": [
            "Use for potentiometers, light sensors, temperature sensors",
            "Value range depends on ADC resolution (usually 0-1023 for 10-bit)",
        ],
    },
    "PWMWrite": {
        "description": "Writes a PWM value (0-255) for variable output control.",
        "category": "Hardware",
        "inputs": [
            {"name": "exec", "type": "execution", "description": "Triggers the write operation"},
            {"name": "value", "type": "number", "description": "PWM value 0-255 (optional)"},
        ],
        "outputs": [
            {"name": "exec", "type": "execution", "description": "Triggers after write completes"}
        ],
        "properties": [
            {"name": "device_id", "type": "string", "description": "ID of the device to control"},
            {
                "name": "value",
                "type": "number",
                "default": 128,
                "description": "PWM duty cycle (0-255)",
            },
        ],
        "tips": [
            "Use for motor speed control, LED dimming",
            "0 = fully off, 255 = fully on",
            "Only works on PWM-capable pins",
        ],
    },
    "Branch": {
        "description": "Conditional branching - executes different paths based on condition.",
        "category": "Control",
        "inputs": [
            {"name": "exec", "type": "execution", "description": "Triggers the branch evaluation"},
            {"name": "condition", "type": "boolean", "description": "Condition to evaluate"},
        ],
        "outputs": [
            {"name": "true", "type": "execution", "description": "Triggers if condition is true"},
            {"name": "false", "type": "execution", "description": "Triggers if condition is false"},
        ],
        "properties": [],
        "tips": [
            "Connect a comparison or sensor output to the 'condition' input",
            "Only one branch will execute",
        ],
    },
}


# Concept explanations
CONCEPTS = {
    "execution flow": """
**Execution Flow** controls WHEN nodes run.

- Shown as white connections between nodes
- Flows from left to right
- Like following a recipe step by step
- Each node waits for its execution input before running

Example: StartExperiment → Delay → DigitalWrite → EndExperiment

The execution triggers in order: start, wait, write, end.
""",
    "data flow": """
**Data Flow** passes VALUES between nodes.

- Shown as colored connections (blue for numbers, green for booleans)
- Data is "pulled" when needed by the receiving node
- Can update reactively when source changes

Example: AnalogRead outputs a value → PWMWrite uses that value

The sensor reading directly controls the PWM output.
""",
    "devices": """
**Devices** are hardware I/O configured on a board.

Types:
- **DigitalOutput**: On/off control (LEDs, relays)
- **DigitalInput**: On/off sensing (buttons, switches)
- **AnalogInput**: Variable sensing (potentiometers, sensors)
- **PWMOutput**: Variable output (motor speed, LED brightness)
- **Servo**: Angle control (servo motors)

Each device is assigned to a specific pin on a board.
""",
    "boards": """
**Boards** are hardware platforms GLIDER connects to.

Supported:
- **Arduino** (Uno, Nano, Mega) - Uses Telemetrix firmware
- **Raspberry Pi** - Uses pigpio for GPIO control

Arduino requires uploading Telemetrix firmware first.
Raspberry Pi works directly with GPIO pins.
""",
    "nodes": """
**Nodes** are the building blocks of experiments.

Categories:
- **Experiment**: Flow control (Start, End, Delay, Loop)
- **Hardware**: Device interaction (Read, Write)
- **Control**: Logic (Branch, Compare)
- **Interface**: User interaction (coming soon)

Drag nodes from the library onto the canvas, then connect their ports.
""",
}


# Example experiments
EXAMPLES = {
    "basic": [
        {
            "name": "Blink LED",
            "description": "Blinks an LED on and off every second",
            "nodes": [
                "StartExperiment",
                "Loop",
                "DigitalWrite (HIGH)",
                "Delay (500)",
                "DigitalWrite (LOW)",
                "Delay (500)",
                "EndExperiment",
            ],
            "requirements": ["Arduino with LED on pin 13"],
        },
        {
            "name": "Button LED",
            "description": "Turns LED on when button is pressed",
            "nodes": [
                "StartExperiment",
                "Loop",
                "DigitalRead",
                "Branch",
                "DigitalWrite (HIGH)",
                "DigitalWrite (LOW)",
            ],
            "requirements": ["Arduino with LED and button"],
        },
    ],
    "sensors": [
        {
            "name": "Light Sensor",
            "description": "Reads light sensor and adjusts LED brightness",
            "nodes": ["StartExperiment", "Loop", "AnalogRead", "PWMWrite", "Delay"],
            "requirements": ["Arduino with LDR and LED"],
        },
    ],
    "motors": [
        {
            "name": "Motor Control",
            "description": "Controls motor speed with potentiometer",
            "nodes": ["StartExperiment", "Loop", "AnalogRead", "PWMWrite", "Delay"],
            "requirements": ["Arduino with potentiometer and motor driver"],
        },
    ],
}


class KnowledgeToolExecutor:
    """Executes knowledge-related tools."""

    def __init__(self, core: "GliderCore"):
        self._core = core

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
        descriptions = {
            "explain_node": f"Explain {args.get('node_type', 'node')} node",
            "explain_concept": f"Explain {args.get('concept', 'concept')}",
            "get_examples": f"Get {args.get('category', 'all')} examples",
            "suggest_flow": "Suggest flow design",
            "troubleshoot": "Help troubleshoot issue",
        }

        return AgentAction(
            action_type=ActionType.EXPLAIN,
            tool_name=tool_name,
            parameters=args,
            description=descriptions.get(tool_name, tool_name),
        )

    async def _execute_explain_node(self, args: dict[str, Any]) -> dict[str, Any]:
        """Explain a node type."""
        node_type = args["node_type"]

        doc = NODE_DOCS.get(node_type)

        if doc is None:
            return {
                "found": False,
                "message": f"No documentation found for node type: {node_type}",
                "available_types": list(NODE_DOCS.keys()),
            }

        return {
            "found": True,
            "node_type": node_type,
            **doc,
        }

    async def _execute_explain_concept(self, args: dict[str, Any]) -> dict[str, Any]:
        """Explain a concept."""
        concept = args["concept"].lower()

        # Find matching concept
        explanation = None
        for key, value in CONCEPTS.items():
            if concept in key or key in concept:
                explanation = value
                break

        if explanation is None:
            return {
                "found": False,
                "message": f"No explanation found for: {concept}",
                "available_concepts": list(CONCEPTS.keys()),
            }

        return {
            "found": True,
            "concept": concept,
            "explanation": explanation,
        }

    async def _execute_get_examples(self, args: dict[str, Any]) -> dict[str, Any]:
        """Get example experiments."""
        category = args.get("category", "all")

        if category == "all":
            all_examples = []
            for cat, examples in EXAMPLES.items():
                for ex in examples:
                    all_examples.append({"category": cat, **ex})
            return {"examples": all_examples}

        examples = EXAMPLES.get(category, [])

        return {
            "category": category,
            "examples": examples,
            "count": len(examples),
        }

    async def _execute_suggest_flow(self, args: dict[str, Any]) -> dict[str, Any]:
        """Suggest a flow design for a task."""
        task = args["task"]

        # This would ideally use the LLM to generate suggestions,
        # but for now we'll return a template-based suggestion
        suggestion = {
            "task": task,
            "suggested_nodes": [
                {"type": "StartExperiment", "reason": "Every experiment needs a start"},
            ],
            "notes": "Based on your task description, here's a suggested approach.",
        }

        # Add nodes based on keywords in task
        task_lower = task.lower()

        if "blink" in task_lower or "flash" in task_lower:
            suggestion["suggested_nodes"].extend(
                [
                    {"type": "Loop", "reason": "Repeat the blinking action"},
                    {
                        "type": "DigitalWrite",
                        "properties": {"value": True},
                        "reason": "Turn LED on",
                    },
                    {
                        "type": "Delay",
                        "properties": {"delay_ms": 500},
                        "reason": "Wait with LED on",
                    },
                    {
                        "type": "DigitalWrite",
                        "properties": {"value": False},
                        "reason": "Turn LED off",
                    },
                    {
                        "type": "Delay",
                        "properties": {"delay_ms": 500},
                        "reason": "Wait with LED off",
                    },
                ]
            )

        if "button" in task_lower:
            suggestion["suggested_nodes"].extend(
                [
                    {"type": "Loop", "reason": "Continuously check button"},
                    {"type": "DigitalRead", "reason": "Read button state"},
                    {"type": "Branch", "reason": "Check if button is pressed"},
                ]
            )

        if "sensor" in task_lower or "read" in task_lower:
            suggestion["suggested_nodes"].extend(
                [
                    {"type": "Loop", "reason": "Continuously read sensor"},
                    {"type": "AnalogRead", "reason": "Read sensor value"},
                    {
                        "type": "Delay",
                        "properties": {"delay_ms": 100},
                        "reason": "Polling interval",
                    },
                ]
            )

        suggestion["suggested_nodes"].append(
            {"type": "EndExperiment", "reason": "Clean experiment end"}
        )

        return suggestion

    async def _execute_troubleshoot(self, args: dict[str, Any]) -> dict[str, Any]:
        """Help troubleshoot an issue."""
        issue = args["issue"]
        error_message = args.get("error_message", "")

        suggestions = []
        issue_lower = issue.lower()

        # Common issues and solutions
        if "not connected" in issue_lower or "connection" in issue_lower:
            suggestions.extend(
                [
                    "Check that the board is plugged in via USB",
                    "Verify the correct COM port is selected",
                    "Ensure Telemetrix firmware is uploaded to Arduino",
                    "Try disconnecting and reconnecting the board",
                ]
            )

        if "not working" in issue_lower or "nothing happens" in issue_lower:
            suggestions.extend(
                [
                    "Verify there's a StartExperiment node connected to your flow",
                    "Check that all nodes are properly connected via execution ports",
                    "Ensure devices are configured and assigned to the correct pins",
                    "Validate the flow using Flow → Validate",
                ]
            )

        if "led" in issue_lower:
            suggestions.extend(
                [
                    "Check LED polarity (long leg to positive)",
                    "Verify the pin number matches your device configuration",
                    "Ensure a current-limiting resistor is in the circuit",
                ]
            )

        if "loop" in issue_lower:
            suggestions.extend(
                [
                    "Connect the Loop's 'body' port to the first node in your loop",
                    "Connect the last node in your loop back or let it complete naturally",
                    "Use 'complete' port for actions after all iterations",
                ]
            )

        if not suggestions:
            suggestions = [
                "Check that all connections are properly made",
                "Verify hardware is connected and configured",
                "Run Flow → Validate to check for errors",
                "Check the log for error messages",
            ]

        return {
            "issue": issue,
            "error_message": error_message,
            "suggestions": suggestions,
        }
