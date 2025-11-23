# Squawkers McCaw Python Class

Clean, reusable Python object for controlling Squawkers McCaw via Home Assistant.

## What is it?

A simple wrapper around the Home Assistant Broadlink remote API that makes it easy to control a Squawkers McCaw animatronic parrot with IR commands.

## Files

- **`squawkers/squawkers.py`** - Main Squawkers class
- **`squawkers/USAGE.md`** - Complete usage guide and examples
- **`squawkers/demo_squawkers.py`** - Interactive demo script
- **`squawkers/try_squawkers.py`** - Quick test script

## Quick Test

```bash
# Run the quick test (DANCE → wait 5s → RESET)
pipenv run python squawkers/try_squawkers.py

# Or run the interactive demo
pipenv run python squawkers/demo_squawkers.py
```

## Quick Code Example

```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

# Initialize
client = HomeAssistantClient()
squawkers = Squawkers(client)

# Make it dance!
squawkers.dance()

# Stop it
squawkers.reset()

# Test sequence
squawkers.test_sequence()  # DANCE → wait 5s → RESET
```

## Features

- **Simple API**: Just `dance()` and `reset()` for the most reliable commands
- **Automatic retries**: Commands are repeated 3x with delays for reliability
- **Flexible**: Supports custom commands via `command("COMMAND_NAME")`
- **Well-documented**: Full docstrings and usage guide
- **Proper logging**: See exactly what's happening
- **Error handling**: Specific exception types for debugging

## Why this exists

The existing `broadlink_squawkers.py` was complex and designed for learning/testing IR codes. This new class is:

- **Simpler** - Just control the parrot, no IR code management
- **More Pythonic** - Clean class interface, not script-based
- **Reusable** - Easy to import and use from other code
- **Production-ready** - Proper error handling, logging, docs

## Integration Points

Works with:
- Home Assistant API via `saga_assistant.ha_client`
- Broadlink IR remotes (via HA integration)
- Any code that needs to control Squawkers

Perfect for:
- Voice assistant commands
- Automation scripts
- Home Assistant automations (via Python scripts)
- Integration with Saga assistant

## Commands

Most reliable (work in any mode):
- `DANCE` - Make it dance
- `RESET` - Stop/reset

You can also use any commands learned in your Home Assistant Broadlink setup via the `command()` method.

## Next Steps

See **USAGE.md** for complete documentation and examples.
