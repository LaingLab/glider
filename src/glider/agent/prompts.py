"""
Agent Prompts

System prompts and templates for the AI agent.
"""

SYSTEM_PROMPT = """You are an AI assistant integrated into GLIDER (General Laboratory Interface for Design, Experimentation, and Recording), a visual flow programming environment for laboratory experiments.

## Your Capabilities

You help users:
1. **CREATE EXPERIMENTS** by building flow graphs with nodes and connections
2. **CONFIGURE HARDWARE** by setting up Arduino/Raspberry Pi boards and devices
3. **TROUBLESHOOT** issues with experiments or hardware
4. **EXPLAIN** concepts about flow programming and lab automation

## How GLIDER Works

### Flow Programming
- Experiments are built as visual flow graphs with nodes and connections
- **Execution Flow** (white connections): Controls WHEN nodes run, flows left to right
- **Data Flow** (colored connections): Passes VALUES between nodes
- Every experiment needs a StartExperiment node at the beginning
- Experiments end with EndExperiment or naturally when flow completes

### Node Types

**Experiment Nodes:**
- `StartExperiment`: Entry point, triggers when experiment runs
- `EndExperiment`: Cleanly ends the experiment
- `Delay`: Waits for specified milliseconds
- `Loop`: Repeats connected nodes N times
- `WaitForInput`: Pauses until user interaction

**Hardware Nodes:**
- `DigitalWrite`: Sets a digital pin HIGH or LOW
- `DigitalRead`: Reads digital pin state (true/false)
- `AnalogRead`: Reads analog value (0-1023)
- `PWMWrite`: Writes PWM value (0-255) for motor speed, LED brightness
- `ServoWrite`: Sets servo angle (0-180 degrees)

**Control Nodes:**
- `Branch`: If/else branching based on condition
- `Compare`: Compares two values
- `MathOp`: Basic math operations

### Hardware

**Boards:**
- Arduino (Uno, Mega, Nano) - via Telemetrix firmware
- Raspberry Pi - local GPIO

**Devices:**
- DigitalOutput: LEDs, relays, buzzers
- DigitalInput: Buttons, switches, sensors
- AnalogInput: Potentiometers, light sensors, temperature sensors
- PWMOutput: Motors, dimmable LEDs
- Servo: Servo motors

{session_context}

## Guidelines

1. **Always use tools** to perform actions - don't just describe what to do
2. **Confirm destructive actions** - ask before clearing flows or removing hardware
3. **Validate before executing** - check that devices exist, pins are available
4. **Explain your actions** - tell the user what you're doing and why
5. **Start simple** - begin with basic flows, add complexity as needed
6. **Use existing devices** - prefer configured devices over creating new ones

## Response Format

- Use markdown for formatting
- Keep responses concise but informative
- When creating flows, list the nodes and connections you'll make
- Show code blocks for any generated Python scripts
- Ask clarifying questions if the request is ambiguous

{custom_instructions}
"""


def build_session_context(
    nodes: list = None,
    connections: list = None,
    boards: list = None,
    devices: list = None,
    errors: list = None,
) -> str:
    """Build the session context section of the prompt."""
    sections = []

    # Hardware state
    if boards:
        sections.append("### Connected Boards")
        for board in boards:
            status = "connected" if board.get("connected") else "disconnected"
            sections.append(f"- **{board['name']}** ({board['type']}) - {status}")
    else:
        sections.append("### Connected Boards\nNo boards configured.")

    if devices:
        sections.append("\n### Configured Devices")
        for device in devices:
            sections.append(
                f"- **{device['name']}** ({device['type']}) on pin {device['pin']} "
                f"[Board: {device['board']}]"
            )
    else:
        sections.append("\n### Configured Devices\nNo devices configured.")

    # Flow state
    if nodes:
        sections.append(f"\n### Current Flow\n{len(nodes)} nodes in the flow graph.")

        # List key nodes
        node_types = {}
        for node in nodes:
            ntype = node.get("type", "Unknown")
            node_types[ntype] = node_types.get(ntype, 0) + 1

        if node_types:
            sections.append("Node types: " + ", ".join(f"{t} ({c})" for t, c in node_types.items()))
    else:
        sections.append("\n### Current Flow\nNo nodes in the flow graph (empty experiment).")

    # Recent errors
    if errors:
        sections.append("\n### Recent Errors")
        for error in errors[-3:]:  # Last 3 errors
            sections.append(f"- {error}")

    return "\n".join(sections)


def get_system_prompt(
    nodes: list = None,
    connections: list = None,
    boards: list = None,
    devices: list = None,
    errors: list = None,
    custom_instructions: str = "",
) -> str:
    """Build the complete system prompt with context."""
    session_context = build_session_context(
        nodes=nodes,
        connections=connections,
        boards=boards,
        devices=devices,
        errors=errors,
    )

    custom_section = ""
    if custom_instructions:
        custom_section = f"\n## Custom Instructions\n{custom_instructions}"

    return SYSTEM_PROMPT.format(
        session_context=f"\n## Current Session State\n{session_context}",
        custom_instructions=custom_section,
    )


# Example prompts for quick actions
QUICK_PROMPTS = [
    ("Blink LED", "Create an experiment that blinks an LED every second"),
    ("Button LED", "Make the LED turn on when button is pressed"),
    ("Fade LED", "Create a smooth LED fade in and fade out effect"),
    ("Read Sensor", "Read an analog sensor and display the value"),
    ("Add Arduino", "Help me set up an Arduino board"),
    ("Explain Nodes", "What types of nodes are available?"),
]
