# My Squawkers Commands

These are the actual IR commands learned in your Home Assistant setup.

## Command Naming Convention

You've learned commands using these templates:

### Response Mode (A-F)
- `Response Button A`
- `Response Button B`
- `Response Button C`
- `Response Button D`
- `Response Button E`
- `Response Button F`

### Command Mode (A-F)
- `Command Button A`
- `Command Button B`
- `Command Button C`
- `Command Button D`
- `Command Button E`
- `Command Button F`

### Plain Buttons (A-F)
- `Button A`
- `Button B`
- `Button C`
- `Button D`
- `Button E`
- `Button F`

### Gags Mode (A-F)
- `Gags A`
- `Gags B`
- `Gags C`
- `Gags D`
- `Gags E`
- `Gags F`

### Universal Commands
- `DANCE` - Most reliable
- `RESET` - Most reliable

## Quick Usage

```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = Squawkers(client)

# Universal commands (most reliable)
squawkers.dance()
squawkers.reset()

# Response mode buttons
squawkers.command("Response Button A")  # Startled squawk
squawkers.command("Response Button B")  # Laugh
squawkers.command("Response Button C")  # Laugh hilariously
squawkers.command("Response Button D")  # Warble
squawkers.command("Response Button E")  # "Whatever!!"
squawkers.command("Response Button F")  # Play along

# Command mode buttons
squawkers.command("Command Button A")
squawkers.command("Command Button B")
squawkers.command("Command Button C")
# ... etc

# Plain buttons
squawkers.command("Button A")
squawkers.command("Button B")
squawkers.command("Button C")
# ... etc

# Gags mode
squawkers.command("Gags A")
squawkers.command("Gags B")
squawkers.command("Gags C")
# ... etc
```

## Behaviors (Response Mode)

From the manual, Response Mode buttons do:

- **Response Button A**: Startled squawk
- **Response Button B**: Laugh
- **Response Button C**: Laugh hilariously
- **Response Button D**: Warble
- **Response Button E**: "Whatever!!"
- **Response Button F**: Play along

## Notes

- **Response Button X**: Preset responses from manual
- **Command Button X**: For custom programmed voice commands
- **Button X**: Unknown (might be default/mixed mode?)
- **Gags X**: Gag responses (manual doesn't specify exact behaviors)

## Testing

Try them out with the demo:

```bash
pipenv run python squawkers/demo_squawkers.py
```

Or test individually:

```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = Squawkers(client)

# Test Response Button A
print("Testing Response Button A (startled squawk)...")
squawkers.command("Response Button A")

# Test Gags B
print("Testing Gags B...")
squawkers.command("Gags B")
```

## All Commands Quick Reference

```python
# Universal (work in any mode)
"DANCE"
"RESET"

# Response mode (A-F)
"Response Button A"
"Response Button B"
"Response Button C"
"Response Button D"
"Response Button E"
"Response Button F"

# Command mode (A-F)
"Command Button A"
"Command Button B"
"Command Button C"
"Command Button D"
"Command Button E"
"Command Button F"

# Plain buttons (A-F)
"Button A"
"Button B"
"Button C"
"Button D"
"Button E"
"Button F"

# Gags mode (A-F)
"Gags A"
"Gags B"
"Gags C"
"Gags D"
"Gags E"
"Gags F"
```

**Total: 26 commands** (2 universal + 24 buttons)
