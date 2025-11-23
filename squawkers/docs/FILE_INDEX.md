# Squawkers McCaw - File Index

Quick reference for all files in this directory.

## 📖 START HERE

- **`START_HERE.md`** ⭐ - Main entry point, complete overview

## 🎯 Quick Reference Docs

- **`QUICK_REFERENCE.md`** - Cheat sheet (commands, usage)
- **`MY_COMMANDS.md`** - Your specific learned commands (auto-discovered)
- **`HOW_TO_CHECK_COMMANDS.md`** - How to verify what commands you have

## 📚 Complete Documentation

- **`USAGE.md`** - Full API reference
- **`DEMO_SEQUENCES.md`** - Example sequences to copy-paste
- **`DISCOVERY_UPDATE.md`** - Automated discovery details
- **`COMMANDS_REFERENCE.md`** - IR commands and behaviors from manual
- **`MANUAL.txt`** - Official Hasbro user manual
- **`README_PYTHON_CLASS.md`** - Project overview
- **`SQUAWKERS_CLASS.md`** - Feature list
- **`SUMMARY.md`** - What we built (original)
- **`UPDATE_SUMMARY.md`** - Latest updates
- **`FILE_INDEX.md`** - This file

## 💻 Core Python Code (Production)

- **`squawkers.py`** - Base Squawkers class
- **`squawkers_full.py`** - Extended class with all 32 convenience methods
- **`__init__.py`** - Package initialization

## 🧪 Test/Demo Scripts

- **`demo_simple.py`** ⭐ - Easy 3-command sequence (modify and run!)
- **`discover_commands.py`** ⭐ - Auto-discover all commands via SSH
- **`try_squawkers.py`** - Quick test (DANCE → wait → RESET)
- **`try_all_commands.py`** - Test one of each command type
- **`demo_squawkers.py`** - Interactive demo menu
- **`example_usage.py`** - Various usage examples
- **`list_commands.py`** - Show all learned commands
- **`check_ha_codes.py`** - Find HA storage file locally
- **`fetch_ha_codes.sh`** - SSH to HA and fetch codes

## 🔧 Arduino/IR Hacking (arduino/ directory)

**All IR protocol research, Arduino/ESP32 code, and legacy scripts:**

- **`arduino/README_ARDUINO.md`** - Guide to arduino directory
- **`arduino/arduino_ir_transmitter.ino`** - Arduino IR transmitter
- **`arduino/IR_CONTROL_RESEARCH.md`** - IR protocol research
- **`arduino/ARDUINO_SETUP.md`** - Arduino setup guide
- **`arduino/broadlink_squawkers.py`** - Legacy IR control class
- **`arduino/test_squawkers.py`** - Legacy test script
- Plus 14 more research/testing files

See `arduino/README_ARDUINO.md` for details.

**Note:** You don't need arduino/ files for normal use!

## Production vs Research

| Purpose | Use These Files | Location |
|---------|----------------|----------|
| **Control Squawkers** | `squawkers.py`, `demo_simple.py` | Root directory |
| **Discover commands** | `discover_commands.py` | Root directory |
| **Documentation** | `START_HERE.md`, `USAGE.md` | Root directory |
| **IR research** | `arduino/` files | arduino/ subdirectory |
| **Hardware hacking** | `arduino/` files | arduino/ subdirectory |

## File Count Summary

### Root Directory (Production Code)
- 📖 Documentation: 11 files
- 💻 Python Code: 3 files
- 🧪 Scripts: 9 files
- **Total: 23 files**

### arduino/ Directory (Research/Legacy)
- 📄 Documentation: 8 files
- 🔧 Code/Scripts: 12 files
- **Total: 20 files**

### Grand Total: 43 files

## Recommended Reading Order

1. **`START_HERE.md`** - Overview and quick start
2. **`MY_COMMANDS.md`** - Your specific commands
3. **`QUICK_REFERENCE.md`** - Cheat sheet
4. **`demo_simple.py`** - Try running it!
5. **`USAGE.md`** - When you need API details
6. **`COMMANDS_REFERENCE.md`** - For behavior details
7. **`MANUAL.txt`** - For complete parrot documentation

## Quick Commands

```bash
# Discover all your commands
pipenv run python squawkers/discover_commands.py

# Test basic functionality
pipenv run python squawkers/try_squawkers.py

# Run simple demo (3 commands)
pipenv run python squawkers/demo_simple.py

# Interactive demo
pipenv run python squawkers/demo_squawkers.py

# See all available methods
pipenv run python squawkers/squawkers_full.py
```

## Import Reference

```python
# Production code (use these!)
from squawkers import Squawkers                    # Base class
from squawkers.squawkers_full import SquawkersFull # Full class
from squawkers import SquawkersError, CommandError # Exceptions

# Legacy code (don't use for production)
from arduino.broadlink_squawkers import SquawkersMcGraw  # Old
```

## Directory Structure

```
squawkers/
├── START_HERE.md              ⭐ Start here!
├── demo_simple.py             ⭐ Easy demo
├── discover_commands.py       ⭐ Auto-discover
├── squawkers.py               💻 Production code
├── squawkers_full.py          💻 Production code
├── [other production files]
└── arduino/                   🔧 Research/legacy
    ├── README_ARDUINO.md
    ├── arduino_ir_transmitter.ino
    └── [IR research files]
```

## Navigation

- **Lost?** → `START_HERE.md`
- **Need API docs?** → `USAGE.md`
- **Want quick cheat sheet?** → `QUICK_REFERENCE.md`
- **Want to hack IR codes?** → `arduino/README_ARDUINO.md`
- **See all files?** → You're reading it!

---

**Updated:** 2025-11-21 - Reorganized with arduino/ subdirectory
