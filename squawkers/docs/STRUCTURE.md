# Squawkers Module Structure

Clean Python module organization (reorganized 2025-11-22).

## Directory Structure

```
squawkers/                      # Clean Python module
├── __init__.py                 # Module exports
├── squawkers.py                # Base Squawkers class
├── squawkers_full.py           # SquawkersFull class (32 methods)
├── README.md                   # Module overview
│
├── docs/                       # All documentation (15 files)
│   ├── README.md
│   ├── START_HERE.md           ⭐ Main guide
│   ├── QUICK_REFERENCE.md
│   ├── MY_COMMANDS.md
│   ├── USAGE.md
│   └── ...
│
├── scripts/                    # Utility scripts (9 files)
│   ├── discover_commands.py    ⭐ Auto-discover
│   ├── try_squawkers.py        ⭐ Quick test
│   ├── demo_simple.py          ⭐ Simple demo
│   └── ...
│
├── examples/                   # Example code (3 files)
│   ├── README.md
│   ├── simple_demo.py
│   └── usage_examples.py
│
└── arduino/                    # IR research & legacy (21 files)
    ├── README_ARDUINO.md
    ├── arduino_ir_transmitter.ino
    └── ...
```

## File Counts

| Location | Files | Purpose |
|----------|-------|---------|
| **Root** | **4 files** | **Module code** |
| docs/ | 15 files | Documentation |
| scripts/ | 9 files | Utility scripts |
| examples/ | 3 files | Example code |
| arduino/ | 21 files | IR research |
| **Total** | **52 files** | |

## Top Level (Module Root)

**Only 4 files** - clean and focused!

- `__init__.py` - Module exports
- `squawkers.py` - Base class (210 lines)
- `squawkers_full.py` - Full class with all 32 methods (280 lines)
- `README.md` - Module overview

## Import as Module

```python
# Clean imports from module root
from squawkers import Squawkers
from squawkers.squawkers_full import SquawkersFull
from squawkers import SquawkersError, CommandError
```

## Run Scripts

```bash
# All scripts are in scripts/
pipenv run python squawkers/scripts/discover_commands.py
pipenv run python squawkers/scripts/try_squawkers.py
pipenv run python squawkers/scripts/demo_simple.py
```

## Read Docs

```bash
# All docs are in docs/
cat squawkers/docs/START_HERE.md
cat squawkers/docs/QUICK_REFERENCE.md
cat squawkers/docs/USAGE.md
```

## Run Examples

```bash
# All examples are in examples/
pipenv run python squawkers/examples/simple_demo.py
pipenv run python squawkers/examples/usage_examples.py
```

## Arduino/IR Research

```bash
# All research is in arduino/
cat squawkers/arduino/README_ARDUINO.md
cat squawkers/arduino/IR_CONTROL_RESEARCH.md
```

## Benefits of This Structure

### For Importers
- **Clean module root** - Only 4 files
- **Simple imports** - `from squawkers import Squawkers`
- **No clutter** - Scripts/docs separate

### For Users
- **Easy to navigate** - Clear separation
- **Docs in one place** - docs/
- **Scripts in one place** - scripts/
- **Examples ready** - examples/

### For Maintainers
- **Organized** - Everything has a place
- **Scalable** - Easy to add more files
- **Standard** - Follows Python best practices

## Navigation

| I want to... | Go to |
|--------------|-------|
| Import the module | `from squawkers import Squawkers` |
| Read docs | `squawkers/docs/START_HERE.md` |
| Run a script | `squawkers/scripts/` directory |
| See examples | `squawkers/examples/` directory |
| Research IR codes | `squawkers/arduino/` directory |

## Module Metadata

```
Name: squawkers
Type: Python package/module
Purpose: Control Squawkers McCaw via Home Assistant IR
Classes: Squawkers, SquawkersFull
Dependencies: See parent project Pipfile
Python: 3.13+
```

## Comparison

### Before (Messy)
```
squawkers/
├── 43 files all mixed together
└── (very busy!)
```

### After (Clean)
```
squawkers/
├── 4 module files (clean!)
├── docs/ (15 files)
├── scripts/ (9 files)
├── examples/ (3 files)
└── arduino/ (21 files)
```

## This is a Python Module

The `squawkers/` directory is now a proper Python module:
- Importable: `from squawkers import ...`
- Documented: See `docs/`
- Tested: See `scripts/`
- Examples included: See `examples/`
- Clean structure: Only 4 files in root

---

**Updated:** 2025-11-22 - Final clean organization
