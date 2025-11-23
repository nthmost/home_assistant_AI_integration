# Squawkers Update - Your Command Names

## What Changed

Added support for your actual learned IR command names:

### Your Command Naming Convention

**Response Mode:**
- `Response Button A` through `Response Button F`

**Command Mode:**
- `Command Button A` through `Command Button F`

**Plain Buttons:**
- `Button A` through `Button F`

**Gags Mode:**
- `Gags A` through `Gags F`

**Universal:**
- `DANCE`
- `RESET`

**Total: 26 commands**

## New Files

1. **`MY_COMMANDS.md`** - Quick reference for YOUR specific command names
2. **`squawkers_full.py`** - Extended class with convenience methods
3. **`try_all_commands.py`** - Test script for all command types

## Updated Files

- **`list_commands.py`** - Now shows your actual command names

## Two Ways To Use

### Option 1: Base Class (Manual Command Names)

```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = Squawkers(client)

# Universal
squawkers.dance()
squawkers.reset()

# Manual command names
squawkers.command("Response Button A")
squawkers.command("Gags B")
squawkers.command("Command Button C")
squawkers.command("Button F")
```

### Option 2: Full Class (Convenience Methods)

```python
from squawkers.squawkers_full import SquawkersFull
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = SquawkersFull(client)

# Universal
squawkers.dance()
squawkers.reset()

# Response mode
squawkers.response_a()  # "Response Button A" - Startled squawk
squawkers.response_b()  # "Response Button B" - Laugh
squawkers.response_c()  # "Response Button C" - Laugh hilariously

# Command mode
squawkers.command_a()   # "Command Button A"
squawkers.command_b()   # "Command Button B"
squawkers.command_c()   # "Command Button C"

# Plain buttons
squawkers.button_a()    # "Button A"
squawkers.button_b()    # "Button B"

# Gags mode
squawkers.gag_a()       # "Gags A"
squawkers.gag_b()       # "Gags B"
squawkers.gag_c()       # "Gags C"
```

## Available Methods in SquawkersFull

### Universal
- `dance()` - DANCE command
- `reset()` - RESET command

### Response Mode (A-F)
- `response_a()` through `response_f()`

### Command Mode (A-F)
- `command_a()` through `command_f()`

### Plain Buttons (A-F)
- `button_a()` through `button_f()`

### Gags Mode (A-F)
- `gag_a()` through `gag_f()`

## Testing

```bash
# List all your commands
pipenv run python squawkers/list_commands.py

# Test all command types
pipenv run python squawkers/try_all_commands.py

# See all available methods
pipenv run python squawkers/squawkers_full.py
```

## Which One Should You Use?

**Use `Squawkers` (base class) if:**
- You prefer explicit command names
- You're only using a few commands
- You want minimal overhead

**Use `SquawkersFull` if:**
- You want autocomplete/IDE support
- You're using many different commands
- You prefer method calls over string parameters

Both classes have the same behavior and reliability. It's just syntax preference!

## Example: Voice Assistant Integration

```python
# In your voice command handler
from squawkers.squawkers_full import SquawkersFull

def handle_voice_command(command_text):
    client = HomeAssistantClient()
    squawkers = SquawkersFull(client)

    if "dance" in command_text.lower():
        squawkers.dance()

    elif "laugh" in command_text.lower():
        squawkers.response_b()  # Laugh

    elif "squawk" in command_text.lower():
        squawkers.response_a()  # Startled squawk

    elif "reset" in command_text.lower() or "stop" in command_text.lower():
        squawkers.reset()
```

## Reference Files

- **MY_COMMANDS.md** - Your command names and usage
- **COMMANDS_REFERENCE.md** - Manual-based behaviors
- **USAGE.md** - Complete API docs
- **QUICK_REFERENCE.md** - Cheat sheet

---

All existing code still works! This is purely additive.
