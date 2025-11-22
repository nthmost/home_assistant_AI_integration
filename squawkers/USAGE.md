# Squawkers McCaw Python Usage Guide

## Quick Start

```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

# Initialize
client = HomeAssistantClient()
squawkers = Squawkers(
    client,
    entity_id="remote.office_lights",  # Your Broadlink remote entity
    device_name="squawkers"             # Device name in HA
)

# Basic commands
squawkers.dance()      # Make it dance!
squawkers.reset()      # Stop/reset

# Test sequence
squawkers.test_sequence()  # Dance for 5 seconds, then reset
```

## Installation

The Squawkers class is already in your project. Just import it:

```python
from squawkers.squawkers import Squawkers
```

## Class Reference

### `Squawkers(ha_client, entity_id="remote.office_lights", device_name="squawkers", num_repeats=3, delay_between_repeats=0.5)`

**Parameters:**
- `ha_client` (HomeAssistantClient): Initialized HA client
- `entity_id` (str): Broadlink remote entity ID in Home Assistant (default: `"remote.office_lights"`)
- `device_name` (str): IR device name in Home Assistant (default: `"squawkers"`)
- `num_repeats` (int): How many times to repeat each command (default: `3`)
- `delay_between_repeats` (float): Seconds between repeats (default: `0.5`)

**Why repeats?** The Squawkers IR receiver is more reliable when commands are repeated with gentle pauses (from GitHub issue #2).

### Methods

#### `dance(num_repeats=None)`
Make Squawkers dance. Most reliable command, works in any mode.

```python
squawkers.dance()           # Use default repeats (3)
squawkers.dance(num_repeats=5)  # Override to 5 repeats
```

#### `reset(num_repeats=None)`
Reset/stop current action. Works in any mode.

```python
squawkers.reset()
squawkers.reset(num_repeats=1)  # Send only once
```

#### `test_sequence(dance_duration=5.0)`
Run a test: DANCE → wait → RESET

```python
squawkers.test_sequence()             # Dance 5 seconds
squawkers.test_sequence(dance_duration=10.0)  # Dance 10 seconds
```

#### `command(command_name, num_repeats=None)`
Send any arbitrary command.

```python
squawkers.command("DANCE")
squawkers.command("RESPONSE_A", num_repeats=5)
squawkers.command("CUSTOM_COMMAND")
```

## Demo Script

Run the interactive demo:

```bash
cd squawkers
./demo_squawkers.py
```

Or:

```bash
pipenv run python squawkers/demo_squawkers.py
```

## Examples

### Simple test
```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = Squawkers(client)

# Quick test
squawkers.test_sequence()
```

### With custom settings
```python
# More repeats for unreliable reception
squawkers = Squawkers(
    client,
    entity_id="remote.office_lights",  # Your Broadlink entity
    device_name="squawkers",
    num_repeats=5,                     # Repeat 5 times
    delay_between_repeats=1.0          # Wait 1 second between
)

squawkers.dance()  # Will repeat 5 times with 1s delays
```

### Error handling
```python
from squawkers import Squawkers, CommandError

try:
    squawkers.dance()
except CommandError as e:
    print(f"Failed to send command: {e}")
```

### Custom commands
```python
# You can add any IR commands learned in Home Assistant
squawkers.command("RESPONSE_A")
squawkers.command("GAGS_F")
squawkers.command("CUSTOM_RECORDING_1")
```

## Logging

Enable detailed logs:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Now you'll see all command sends
squawkers.dance()
# Output:
# INFO: Sending command 'DANCE' to squawkers (3x)
# DEBUG:   Repeat 1/3
# DEBUG:   Repeat 2/3
# DEBUG:   Repeat 3/3
# INFO: ✓ Command 'DANCE' sent successfully
```

## Device Setup in Home Assistant

Make sure you have:
1. A Broadlink remote entity (e.g., `remote.office_lights`)
2. A device named `"squawkers"` configured in that remote
3. Commands learned for "DANCE" and "RESET" at minimum

If your setup is different, adjust the parameters:

```python
# Custom entity/device names
squawkers = Squawkers(
    client,
    entity_id="remote.my_broadlink",
    device_name="my_squawkers"
)
```

The Broadlink integration should support the `remote.send_command` service.

## Available Commands

The most reliable commands are:
- **DANCE** - Works in any mode, always gets a response
- **RESET** - Works in any mode, stops current action

Other commands depend on what you've learned/programmed into your IR remote in Home Assistant.

## Notes

- Commands are uppercase (e.g., "DANCE" not "dance")
- The class automatically handles retries with delays
- Default settings (3 repeats, 0.5s delay) work well for most cases
- Increase repeats if your IR receiver is far away or has obstacles
