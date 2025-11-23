# My Squawkers Commands

**DISCOVERED AUTOMATICALLY** from your Home Assistant setup on 2025-11-21.

You have **32 IR commands** learned for the 'squawkers' device.

## How to Verify Your Learned Commands

### Automatic Discovery (Recommended!)

```bash
pipenv run python squawkers/discover_commands.py
```

This automatically SSHs to Home Assistant and shows all your learned commands.

### Manual Methods

See `HOW_TO_CHECK_COMMANDS.md` for Web UI and other manual methods.

## Your Commands

### Universal (Most Reliable)
- `DANCE`
- `RESET`

### Plain Buttons (A-F)
- `Button A`
- `Button B`
- `Button C`
- `Button D`
- `Button E`
- `Button F`

### Command Mode (A-F)
For custom programmed voice commands:
- `Command A`
- `Command B`
- `Command C`
- `Command D`
- `Command E`
- `Command F`

### Gags Mode (A-F)
- `Gags A`
- `Gags B`
- `Gags C`
- `Gags D`
- `Gags E`
- `Gags F`

### Record Command (A-F)
For recording new custom commands:
- `Record Command A`
- `Record Command B`
- `Record Command C`
- `Record Command D`
- `Record Command E`
- `Record Command F`

### Record Response (A-F)
For recording responses to custom commands:
- `Record Response A`
- `Record Response B`
- `Record Response C`
- `Record Response D`
- `Record Response E`
- `Record Response F`

**Total: 32 commands**

## Usage

### Option 1: Base Class (Manual Command Names)

```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = Squawkers(client)

# Universal (most reliable)
squawkers.dance()
squawkers.reset()

# Plain buttons
squawkers.command("Button A")
squawkers.command("Button B")

# Gags
squawkers.command("Gags A")
squawkers.command("Gags B")

# Commands
squawkers.command("Command A")

# Recording
squawkers.command("Record Command A")
squawkers.command("Record Response A")
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

# Plain buttons
squawkers.button_a()
squawkers.button_b()

# Gags
squawkers.gag_a()
squawkers.gag_b()

# Commands
squawkers.command_a()
squawkers.command_b()

# Recording
squawkers.record_command_a()
squawkers.record_response_a()
```

## Response Mode vs Command Mode

**Note:** You have "Command A-F" and "Button A-F", but no "Response Button A-F" commands.

According to the manual:
- **Response Mode** buttons trigger preset behaviors (laugh, squawk, etc.)
- **Command Mode** buttons trigger custom programmed commands
- **Record Command/Response** are for programming new custom behaviors

Your setup appears to use:
- `Button A-F` for general buttons
- `Command A-F` for command mode
- `Gags A-F` for gags mode
- `Record Command/Response A-F` for programming

## Behaviors (from manual)

While you don't have Response Button commands, here's what the manual says those buttons do:
- **Response A**: Startled squawk
- **Response B**: Laugh
- **Response C**: Laugh hilariously
- **Response D**: Warble
- **Response E**: "Whatever!!"
- **Response F**: Play along

Your `Button A-F` or `Gags A-F` may trigger similar behaviors - test them to find out!

## Testing Commands

```bash
# Discover all commands
pipenv run python squawkers/discover_commands.py

# Quick test
pipenv run python squawkers/try_squawkers.py

# Interactive testing
pipenv run python squawkers/demo_squawkers.py
```

## All Convenience Methods (SquawkersFull)

```python
# Universal (2 methods)
squawkers.dance()
squawkers.reset()

# Plain Buttons (6 methods)
squawkers.button_a() through squawkers.button_f()

# Commands (6 methods)
squawkers.command_a() through squawkers.command_f()

# Gags (6 methods)
squawkers.gag_a() through squawkers.gag_f()

# Record Command (6 methods)
squawkers.record_command_a() through squawkers.record_command_f()

# Record Response (6 methods)
squawkers.record_response_a() through squawkers.record_response_f()
```

**Total: 32 convenience methods** (matching your 32 IR commands!)

## Integration Example

```python
from squawkers.squawkers_full import SquawkersFull
from saga_assistant.ha_client import HomeAssistantClient

def squawkers_demo():
    client = HomeAssistantClient()
    squawkers = SquawkersFull(client)

    # Morning routine
    squawkers.dance()
    time.sleep(5)
    squawkers.gag_a()
    time.sleep(2)
    squawkers.reset()

    # Test buttons
    for i, method in enumerate(['button_a', 'button_b', 'button_c']):
        print(f"Testing {method}...")
        getattr(squawkers, method)()
        time.sleep(3)

    squawkers.reset()
```

## Re-discovery

If you learn new commands, re-run discovery:

```bash
pipenv run python squawkers/discover_commands.py
```

This will show your updated command list!
