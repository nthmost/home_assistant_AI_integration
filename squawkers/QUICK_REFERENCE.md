# Squawkers McCaw - Quick Reference

## 30-Second Start

```bash
pipenv run python squawkers/try_squawkers.py
```

## 1-Minute Code

```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = Squawkers(client)

squawkers.dance()           # Make it dance
squawkers.reset()           # Stop it
squawkers.test_sequence()   # Dance → wait → reset
```

## Commands

| Command | What it does | Reliability |
|---------|--------------|-------------|
| `dance()` | Make it dance | ⭐⭐⭐ Most reliable |
| `reset()` | Stop current action | ⭐⭐⭐ Most reliable |
| `command("NAME")` | Send custom command | ⭐⭐ Depends on learning |
| `test_sequence()` | DANCE → wait → RESET | ⭐⭐⭐ Full test |

## Files You Care About

| File | Purpose |
|------|---------|
| `try_squawkers.py` | Quick test script |
| `demo_squawkers.py` | Interactive demo |
| `list_commands.py` | Find learned commands |
| `USAGE.md` | Complete API docs |
| `COMMANDS_REFERENCE.md` | What buttons do |
| `MANUAL.txt` | Official manual |

## Customization

```python
# More repeats for unreliable reception
squawkers = Squawkers(
    client,
    num_repeats=5,              # Default: 3
    delay_between_repeats=1.0   # Default: 0.5
)
```

## Common Tasks

**Test if it works:**
```bash
pipenv run python squawkers/try_squawkers.py
```

**Find what commands you have:**
```bash
pipenv run python squawkers/list_commands.py
```

**Try different commands:**
```bash
pipenv run python squawkers/demo_squawkers.py
```

**See code examples:**
```bash
pipenv run python squawkers/example_usage.py
```

## Documentation Map

- 🚀 **Start here**: `README_PYTHON_CLASS.md`
- 📖 **API Reference**: `USAGE.md`
- 🎮 **Command List**: `COMMANDS_REFERENCE.md`
- 📚 **Full Manual**: `MANUAL.txt`
- 🏗️ **What we built**: `SUMMARY.md`
- ⚡ **This file**: Quick cheatsheet

## Error Handling

```python
from squawkers import CommandError

try:
    squawkers.dance()
except CommandError as e:
    print(f"Failed: {e}")
```

## Configuration

Default settings (usually work fine):
- Entity: `remote.office_lights`
- Device: `squawkers`
- Repeats: 3
- Delay: 0.5 seconds

Change if needed:
```python
squawkers = Squawkers(
    client,
    entity_id="remote.my_broadlink",
    device_name="my_parrot_device"
)
```

## Button Functions (from manual)

**Response Mode:**
- A: Startled squawk
- B: Laugh
- C: Laugh hilariously
- D: Warble
- E: "Whatever!!"
- F: Play along

**Note:** You need to learn these in Home Assistant first!

## Help

- Stuck? Read `USAGE.md`
- Want details? Read `COMMANDS_REFERENCE.md`
- Have the parrot? Read `MANUAL.txt`
- Need the old code? See `broadlink_squawkers.py`

---

**TL;DR**: Import `Squawkers`, call `dance()` and `reset()`. Done.
