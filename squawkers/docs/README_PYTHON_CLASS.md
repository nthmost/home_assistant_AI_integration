# Squawkers McCaw Python Control Class

Clean, production-ready Python class for controlling Squawkers McCaw animatronic parrot via Home Assistant IR commands.

## Quick Start

```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = Squawkers(client)

squawkers.dance()           # Make it dance!
squawkers.reset()           # Stop it
squawkers.test_sequence()   # Dance → wait 5s → reset
```

## Testing It Works

```bash
# Quick test (DANCE → wait 5s → RESET)
pipenv run python squawkers/try_squawkers.py

# Interactive demo menu
pipenv run python squawkers/demo_squawkers.py

# All usage examples
pipenv run python squawkers/example_usage.py

# Discover learned commands
pipenv run python squawkers/list_commands.py
```

## What Commands Are Available?

**Confirmed working:**
- `DANCE` - Most reliable, works in any mode
- `RESET` - Stops current action

**From manual (if you've learned them):**
- Buttons A-F in Response/Command/Gags modes
- See `COMMANDS_REFERENCE.md` for details

**How to find YOUR learned commands:**
Run `python squawkers/list_commands.py` for instructions.

## File Guide

### 📦 Core
- `squawkers.py` - Main Squawkers class
- `__init__.py` - Package exports

### 🧪 Test/Demo Scripts
- `try_squawkers.py` - Quick test (5 second sequence)
- `demo_squawkers.py` - Interactive menu
- `example_usage.py` - Code examples
- `list_commands.py` - Discover learned commands

### 📚 Documentation
- `USAGE.md` - Complete API reference and examples
- `COMMANDS_REFERENCE.md` - IR command reference from manual
- `SQUAWKERS_CLASS.md` - Overview and features
- `MANUAL.txt` - Official Hasbro manual
- `README_PYTHON_CLASS.md` - This file
- `SUMMARY.md` - What we built

### 🔧 Legacy/Reference
- `broadlink_squawkers.py` - Original IR code management (for learning/testing)
- `test_squawkers.py` - Original interactive test script
- Other files for IR code conversion and testing

## Usage Examples

### Basic Control
```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = Squawkers(client)

squawkers.dance()
squawkers.reset()
```

### Custom Settings
```python
# More repeats for better reliability
squawkers = Squawkers(
    client,
    entity_id="remote.office_lights",  # Your Broadlink entity
    device_name="squawkers",            # Device name in HA
    num_repeats=5,                      # Repeat 5 times
    delay_between_repeats=1.0           # 1 second between
)
```

### Custom Commands
```python
# Send any learned command
squawkers.command("RESPONSE_A")
squawkers.command("BUTTON_B", num_repeats=5)
```

### Error Handling
```python
from squawkers import Squawkers, CommandError

try:
    squawkers.dance()
except CommandError as e:
    print(f"Failed: {e}")
```

## Features

- **Simple API**: Just `dance()`, `reset()`, and `command()`
- **Automatic retries**: Commands sent 3x with delays by default
- **Configurable**: Adjust repeats, delays, entity/device names
- **Proper error handling**: Specific exception types
- **Good logging**: See what's happening
- **Well-documented**: Docstrings, usage guide, examples
- **Production-ready**: Follows project coding standards

## Integration

Perfect for:
- Voice assistant commands (Saga)
- Home automation scripts
- HA Python scripts
- Custom behaviors and sequences

## Documentation

- **New to this?** Start with `SQUAWKERS_CLASS.md`
- **Want API docs?** See `USAGE.md`
- **Need command list?** Check `COMMANDS_REFERENCE.md`
- **Have the parrot?** Read `MANUAL.txt`

## Why This Exists

The existing `broadlink_squawkers.py` was great for learning IR codes and testing. This new class is:

- **Simpler** - Just control, no IR management
- **Cleaner** - Class-based, not script-based
- **More reusable** - Easy to import and use
- **Better documented** - Complete usage guide
- **Production-ready** - Proper structure and error handling

Both coexist peacefully. Use the old code for IR learning/testing, use this class for production control.

## Requirements

- Home Assistant with Broadlink integration
- A Broadlink IR remote (e.g., RM4 Pro)
- Device "squawkers" configured with learned commands
- Minimum learned commands: DANCE, RESET

## Next Steps

1. Test it: `pipenv run python squawkers/try_squawkers.py`
2. Read docs: `USAGE.md` and `COMMANDS_REFERENCE.md`
3. Import and use in your code!
4. Integrate with Saga voice assistant

---

**Created:** November 2024
**Status:** Production-ready, tested and working
**License:** Same as project
