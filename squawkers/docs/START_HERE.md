# Squawkers McCaw Python Control - START HERE

Welcome! This is your complete guide to controlling Squawkers McCaw via Python.

## Quick Start (30 seconds)

```bash
# Test basic functionality
pipenv run python squawkers/try_squawkers.py

# Discover all your commands
pipenv run python squawkers/discover_commands.py
```

First command runs: DANCE → wait 5s → RESET

Second command shows all 32 of your learned IR commands!

If both work, you're all set! 🎉

## What Is This?

A clean Python library for controlling your Squawkers McCaw animatronic parrot through Home Assistant IR commands.

## Your Setup

- **Home Assistant**: homeassistant.local:8123
- **Broadlink Remote**: `remote.office_lights`
- **Device Name**: `squawkers`
- **Commands Learned**: 32 (DANCE, RESET, Button/Command/Gags/Record A-F)

## Two Ways to Use

### 1. Simple (Base Class)

```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = Squawkers(client)

squawkers.dance()
squawkers.reset()
squawkers.command("Response Button A")
```

### 2. Convenient (Full Class)

```python
from squawkers.squawkers_full import SquawkersFull
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = SquawkersFull(client)

squawkers.dance()
squawkers.response_a()  # Response Button A - Startled squawk
squawkers.gag_b()       # Gags B
```

## Documentation Guide

Lost? Here's where to look:

| I want to... | Read this file |
|--------------|----------------|
| **Get started quickly** | `START_HERE.md` (you are here) |
| **See available commands** | `MY_COMMANDS.md` |
| **Check what commands I have** | `HOW_TO_CHECK_COMMANDS.md` |
| **Learn the full API** | `USAGE.md` |
| **Understand behaviors** | `COMMANDS_REFERENCE.md` or `MANUAL.txt` |
| **Quick cheat sheet** | `QUICK_REFERENCE.md` |
| **Know what we built** | `SUMMARY.md` or `UPDATE_SUMMARY.md` |

## Test Scripts

| Script | What it does |
|--------|--------------|
| `try_squawkers.py` | Quick test: DANCE → wait → RESET |
| `try_all_commands.py` | Test one of each type |
| `demo_squawkers.py` | Interactive menu |
| `list_commands.py` | Show all your commands |
| `check_ha_codes.py` | Find HA storage file |
| `fetch_ha_codes.sh` | SSH to HA and get codes |

Run any script:
```bash
pipenv run python squawkers/SCRIPT_NAME.py
```

## Your Commands

**Automatically discovered!** You have **32 IR commands** learned:

Run `pipenv run python squawkers/discover_commands.py` to see them all!

**Universal (most reliable):**
- `DANCE`
- `RESET`

**Response Mode (A-F):**
- `Response Button A` (Startled squawk)
- `Response Button B` (Laugh)
- `Response Button C` (Laugh hilariously)
- `Response Button D` (Warble)
- `Response Button E` ("Whatever!!")
- `Response Button F` (Play along)

**Command Mode (A-F):**
- `Command Button A` through `Command Button F`

**Plain Buttons (A-F):**
- `Button A` through `Button F`

**Gags Mode (A-F):**
- `Gags A` through `Gags F`

See `MY_COMMANDS.md` for usage examples.

## Verify Your Commands

Don't trust this list? Check what you actually have:

**Easiest way (Web UI):**
1. Open Home Assistant
2. Developer Tools > Services
3. Service: `remote.send_command`
4. Entity: `remote.office_lights`
5. Device: `squawkers`
6. Click in "command" field → dropdown shows all learned commands

**Via SSH:**
```bash
./squawkers/fetch_ha_codes.sh
```

See `HOW_TO_CHECK_COMMANDS.md` for details.

## Common Tasks

### Make it dance
```python
squawkers.dance()
```

### Make it laugh
```python
# Option 1: Manual command name
squawkers.command("Response Button B")

# Option 2: Convenience method
from squawkers.squawkers_full import SquawkersFull
squawkers = SquawkersFull(client)
squawkers.response_b()
```

### Test sequence
```python
squawkers.test_sequence()  # DANCE → wait 5s → RESET
```

### Custom behavior
```python
squawkers.dance()
time.sleep(10)
squawkers.response_b()  # Laugh after dancing
time.sleep(2)
squawkers.reset()
```

## Troubleshooting

### Command not working?

1. **Check it's learned**: Run `pipenv run python squawkers/list_commands.py`
2. **Test with DANCE**: It's the most reliable
3. **Try more repeats**: `squawkers.dance(num_repeats=5)`
4. **Check HA logs**: See if Broadlink is responding

### Can't connect to HA?

1. Check `.env` file has `HA_URL` and `HA_TOKEN`
2. Test: `pipenv run python saga_assistant/ha_client.py`

### Import errors?

Make sure you're in the project directory:
```bash
cd /path/to/home_assistant_AI_integration
pipenv run python squawkers/your_script.py
```

## Integration Examples

### Voice Assistant
```python
def handle_squawkers_command(voice_text):
    from squawkers.squawkers_full import SquawkersFull
    client = HomeAssistantClient()
    squawkers = SquawkersFull(client)

    if "dance" in voice_text.lower():
        squawkers.dance()
    elif "laugh" in voice_text.lower():
        squawkers.response_b()
    elif "stop" in voice_text.lower():
        squawkers.reset()
```

### Automation Script
```python
# Morning greeting
squawkers.response_f()  # Play along
time.sleep(2)
squawkers.gag_a()

# Dance party
for i in range(3):
    squawkers.dance()
    time.sleep(10)
    squawkers.reset()
    time.sleep(2)
```

## Files Overview

### Core Code
- `squawkers.py` - Base class
- `squawkers_full.py` - Extended class with convenience methods
- `__init__.py` - Package exports

### Test/Demo Scripts
- `try_squawkers.py` - Quick test
- `try_all_commands.py` - Test all types
- `demo_squawkers.py` - Interactive demo
- `example_usage.py` - Code examples
- `list_commands.py` - List your commands
- `check_ha_codes.py` - Find storage file
- `fetch_ha_codes.sh` - SSH fetch script

### Documentation
- `START_HERE.md` - This file
- `MY_COMMANDS.md` - Your specific commands
- `HOW_TO_CHECK_COMMANDS.md` - How to verify learned commands
- `USAGE.md` - Complete API reference
- `COMMANDS_REFERENCE.md` - Behaviors from manual
- `QUICK_REFERENCE.md` - Cheat sheet
- `MANUAL.txt` - Official Hasbro manual
- `SUMMARY.md` - What we built
- `UPDATE_SUMMARY.md` - Latest updates
- `README_PYTHON_CLASS.md` - Project overview
- `SQUAWKERS_CLASS.md` - Features list

### Legacy/Reference
- `broadlink_squawkers.py` - Original IR learning code
- `test_squawkers.py` - Original test script
- Various IR conversion utilities

## Next Steps

1. ✅ **Test it works**: `pipenv run python squawkers/try_squawkers.py`
2. 📚 **Read the manual**: `MANUAL.txt` to understand behaviors
3. 🎮 **Try commands**: `pipenv run python squawkers/demo_squawkers.py`
4. 🔍 **Verify your codes**: See `HOW_TO_CHECK_COMMANDS.md`
5. 🚀 **Integrate**: Use in your voice assistant or automation

## Get Help

- **API reference**: `USAGE.md`
- **Command list**: `MY_COMMANDS.md`
- **Behaviors**: `COMMANDS_REFERENCE.md`
- **Manual**: `MANUAL.txt`
- **Cheat sheet**: `QUICK_REFERENCE.md`

---

**Ready to make that parrot dance!** 🦜

Start with: `pipenv run python squawkers/try_squawkers.py`
