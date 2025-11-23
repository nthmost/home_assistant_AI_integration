# Squawkers McCaw Python Module

Clean Python module for controlling Squawkers McCaw animatronic parrot via Home Assistant IR commands.

## Quick Start

```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = Squawkers(client)

squawkers.dance()
squawkers.reset()
```

## Installation

Already installed as part of this project. Just import and use.

## Usage

### Simple Commands

```python
from squawkers import Squawkers

squawkers = Squawkers(client)
squawkers.dance()           # DANCE command
squawkers.reset()           # RESET command
squawkers.command("Gags A") # Any learned command
```

### Convenience Methods (All 32 Commands)

```python
from squawkers.squawkers_full import SquawkersFull

squawkers = SquawkersFull(client)
squawkers.dance()           # DANCE
squawkers.button_a()        # Button A
squawkers.gag_b()           # Gags B
squawkers.command_c()       # Command C
squawkers.record_response_a()  # Record Response A
```

## Discovery

Auto-discover all learned commands:

```bash
pipenv run python squawkers/scripts/discover_commands.py
```

## Testing

```bash
# Quick test
pipenv run python squawkers/scripts/try_squawkers.py

# Simple demo
pipenv run python squawkers/scripts/demo_simple.py

# Discover commands
pipenv run python squawkers/scripts/discover_commands.py
```

## Module Structure

```
squawkers/
├── __init__.py              # Module exports
├── squawkers.py             # Base Squawkers class
├── squawkers_full.py        # SquawkersFull with all 32 methods
├── scripts/                 # Utility scripts
├── docs/                    # Documentation
├── examples/                # Example code
└── arduino/                 # IR research & legacy code
```

## Documentation

- **[Getting Started](docs/START_HERE.md)** - Complete guide
- **[API Reference](docs/USAGE.md)** - Full API documentation
- **[Commands](docs/MY_COMMANDS.md)** - Your learned commands
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Cheat sheet

## Classes

### `Squawkers`

Base class for IR control.

```python
from squawkers import Squawkers

squawkers = Squawkers(
    client,
    entity_id="remote.office_lights",
    device_name="squawkers",
    num_repeats=3,
    delay_between_repeats=0.5
)
```

**Methods:**
- `dance()` - Make it dance
- `reset()` - Stop/reset
- `command(name)` - Send any command
- `test_sequence()` - DANCE → wait → RESET

### `SquawkersFull`

Extended class with convenience methods for all 32 commands.

```python
from squawkers.squawkers_full import SquawkersFull

squawkers = SquawkersFull(client)
```

**Methods (32 total):**
- `dance()`, `reset()` - Universal
- `button_a()` through `button_f()` - Plain buttons (6)
- `command_a()` through `command_f()` - Commands (6)
- `gag_a()` through `gag_f()` - Gags (6)
- `record_command_a()` through `record_command_f()` - Record commands (6)
- `record_response_a()` through `record_response_f()` - Record responses (6)

## Your Setup

- **Home Assistant**: homeassistant.local:8123
- **Broadlink Remote**: remote.office_lights
- **Device**: squawkers
- **Commands**: 32 learned IR commands

## Scripts

All utility scripts are in `scripts/`:

- `discover_commands.py` - Auto-discover all commands
- `try_squawkers.py` - Quick test
- `demo_simple.py` - Simple 3-command demo
- `demo_squawkers.py` - Interactive menu
- See `scripts/` directory for more

## Examples

Example code snippets are in `examples/` directory.

## Arduino/IR Research

All IR protocol research and Arduino code is in `arduino/` directory.

See [arduino/README_ARDUINO.md](arduino/README_ARDUINO.md) for details.

## Requirements

- Home Assistant with Broadlink integration
- Learned IR commands for device "squawkers"
- Python 3.13+
- See parent project's Pipfile for dependencies

## Import Reference

```python
# Main classes
from squawkers import Squawkers
from squawkers.squawkers_full import SquawkersFull

# Exceptions
from squawkers import SquawkersError, CommandError

# Home Assistant client (from parent project)
from saga_assistant.ha_client import HomeAssistantClient
```

## Links

- **Documentation**: See `docs/START_HERE.md`
- **Scripts**: See `scripts/` directory
- **Arduino/IR**: See `arduino/` directory

---

**Quick start:** Read [docs/START_HERE.md](docs/START_HERE.md)
