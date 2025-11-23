# Arduino/ESP32 IR Control Research

This directory contains all the files related to **researching and hacking** Squawkers McCaw's IR protocol using Arduino/ESP32 hardware.

**Note:** If you just want to **use** Squawkers with Home Assistant, you don't need anything in this directory. Go back to the parent directory and use the Python classes!

## What's Here

This is the research/experimentation directory for understanding how Squawkers' IR remote works.

### Hardware Research Documentation

- **`README.md`** - Original hardware research and overview
- **`IR_CONTROL_RESEARCH.md`** - Deep dive into IR control methods
- **`ARDUINO_SETUP.md`** - How to set up Arduino IR transmitter
- **`PROTO_SHIELD_SETUP.md`** - Proto shield assembly guide
- **`SENSOR_CONTROL_METHODS.md`** - Alternative control via sensors
- **`SENSOR_QUICK_START.md`** - Quick start for sensor control
- **`QUICK_START.md`** - Original quick start guide
- **`BROADLINK_USAGE.md`** - Broadlink integration guide

### Arduino/ESP32 Code

- **`arduino_ir_transmitter.ino`** - Arduino sketch for IR transmission

### IR Code Conversion Tools

Scripts for converting between IR timing formats:

- **`convert_to_broadlink.py`** - Convert timing arrays to Broadlink format
- **`convert_to_broadlink_fixed.py`** - Fixed version of converter
- **`demo_codes.py`** - Demo of IR code conversion

### IR Timing Data

Raw IR timing codes from GitHub research:

- **`broadlink_codes.txt`** - Original IR timing codes
- **`broadlink_codes_fixed.txt`** - Fixed IR timing codes

### Testing/Debugging Scripts

Scripts used during IR code testing:

- **`send_raw_test.py`** - Test sending raw IR codes
- **`test_broadlink_ir.py`** - Test Broadlink IR sending
- **`test_fixed_codes.py`** - Test fixed IR codes
- **`debug_api_call.py`** - Debug Home Assistant API calls

### Legacy Code

Original learning/testing classes (superseded by production code in parent dir):

- **`broadlink_squawkers.py`** - Original IR control class with learning
- **`test_squawkers.py`** - Original interactive test script

## Production Code

**Don't use files from this directory for production!**

For actual Squawkers control, use the production code in the parent directory:

```python
# Use this (in parent directory)
from squawkers import Squawkers
from squawkers.squawkers_full import SquawkersFull

# Not this (in arduino/ directory)
from broadlink_squawkers import SquawkersMcGraw  # Old/deprecated
```

## Purpose of This Directory

This directory exists for:

1. **Historical reference** - How we figured out the IR protocol
2. **Alternative methods** - Arduino/ESP32 approaches if you don't have Broadlink
3. **Learning** - Understanding IR codes and conversion
4. **Experimentation** - Testing new IR approaches

## If You're Hacking

If you want to experiment with Arduino/ESP32 control or learn IR codes:

1. Read `IR_CONTROL_RESEARCH.md` for overview
2. Check `ARDUINO_SETUP.md` for hardware setup
3. Use `arduino_ir_transmitter.ino` as starting point
4. Test with `convert_to_broadlink.py` scripts

## If You Just Want to Use Squawkers

Go to the parent directory and use:

- `squawkers.py` - Production control class
- `demo_simple.py` - Easy demo script
- `START_HERE.md` - Complete guide

You don't need anything from this `arduino/` directory!

## File Summary

| Type | Count | Purpose |
|------|-------|---------|
| Documentation | 8 | Hardware research, guides |
| Arduino Code | 1 | IR transmitter sketch |
| Conversion Scripts | 3 | IR format conversion |
| IR Data | 2 | Timing codes |
| Test Scripts | 4 | IR testing |
| Legacy Code | 2 | Old/deprecated classes |

**Total: 20 files** - All related to IR protocol research and hardware hacking.

---

**For production use**, go to parent directory and read `START_HERE.md`!
