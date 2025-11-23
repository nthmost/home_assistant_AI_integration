# Squawkers McGraw Broadlink Control - Usage Guide

This guide shows how to control Squawkers McGraw using your existing Office Broadlink device.

## Quick Start

### Prerequisites

- ✅ Home Assistant running
- ✅ Broadlink device configured (`remote.office_lights`)
- ✅ Squawkers McGraw in line of sight of Broadlink
- ✅ Python environment with `pipenv`

### Files Created

1. **`broadlink_squawkers.py`** - Main control module with IR codes
2. **`test_squawkers.py`** - Interactive testing tool
3. **`BROADLINK_USAGE.md`** - This guide

---

## The Challenge: No Original Remote

The GitHub repo provides IR timing codes, but you don't have the original remote. This creates a chicken-and-egg problem:

- **Broadlink can't send raw timing arrays** via Home Assistant API
- **Broadlink needs learned codes** to send commands
- **You can't learn codes** without a working remote

### Solutions

#### Option 1: Borrow/Buy a Remote (Easiest)

If you can get access to an original remote:

```bash
cd squawkers
pipenv run python test_squawkers.py
# Choose option 1: Learn commands from original remote
```

The script will guide you through learning all 20+ commands.

**Where to get remotes:**
- eBay: $175-500 (complete units with remote)
- See: `squawkers/` research docs for details

#### Option 2: ESP32 IR Transmitter Bridge (Recommended)

Use an ESP32 to transmit the timing codes, then use Broadlink to learn them:

**Hardware needed:**
- ESP32 board ($5-10)
- 940nm IR LED ($1-2)
- 2N2222 transistor + resistors ($1)

**Process:**
1. Flash ESP32 with IRremoteESP8266 library
2. Program it to send the timing codes from `broadlink_squawkers.py`
3. Point ESP32 at Broadlink
4. Use Broadlink learn mode to capture each code
5. Test codes with Squawkers

**Cost:** $8-15 total
**Time:** 2-4 hours setup

See: `squawkers/IR_CONTROL_RESEARCH.md` for wiring diagrams

#### Option 3: Use ESP32 Directly (Skip Broadlink)

Since you'd be building an ESP32 IR transmitter anyway, you could:
- Connect it directly to Home Assistant via ESPHome
- Skip Broadlink entirely for Squawkers
- Keep Broadlink for other devices

**Pros:**
- Direct control with timing codes (already in the script)
- No learning mode needed
- Cheaper than buying remote

**Cons:**
- Another device to maintain
- Need to position ESP32 near Squawkers

---

## IR Command Reference

All commands are defined in `broadlink_squawkers.py`:

### Common Commands (All Modes)
- `dance` - Dance behavior
- `reset` - Reset/stop current behavior

### Response Mode (6 buttons)
- `response_a` through `response_f`
- Behavior: Unknown (needs testing)

### Command Mode (6 buttons)
- `command_a` through `command_f`
- Behavior: Unknown (needs testing)

### Gags Mode (6 buttons)
- `gags_a` through `gags_f`
- Behavior: Unknown (needs testing)

**Total: 20 documented commands**

---

## Using the Python Module

Once commands are learned, you can control Squawkers programmatically:

```python
from ha_client import HomeAssistantClient
from squawkers.broadlink_squawkers import SquawkersMcGraw
import os

# Setup
HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")

client = HomeAssistantClient(HA_URL, HA_TOKEN)
squawkers = SquawkersMcGraw(client, entity_id="remote.office_lights")

# Send commands
squawkers.dance()
squawkers.reset()
squawkers.response_mode_button("A")
squawkers.command_mode_button("C")
squawkers.gags_mode_button("F")

# Document discovered behaviors
squawkers.document_behavior("dance", "Squawks and flaps wings")
```

---

## Interactive Testing Tool

Use the test script to systematically test and document behaviors:

```bash
cd squawkers
pipenv run python test_squawkers.py
```

### Features:
- ✅ Guide for learning commands from remote
- ✅ Interactive command testing
- ✅ Behavior documentation
- ✅ Save results to `discovered_behaviors.txt`

### Testing Workflow:

1. Learn all commands (if you have remote)
2. Test each command one by one
3. Document what Squawkers does
4. Build automation based on discovered behaviors

---

## Home Assistant Integration

Once you know what each command does, create HA scripts:

### Example `configuration.yaml` or package:

```yaml
script:
  squawkers_dance:
    alias: "Squawkers Dance"
    sequence:
      - service: remote.send_command
        target:
          entity_id: remote.office_lights
        data:
          device: "Squawkers McGraw"
          command: ["dance"]
          num_repeats: 3
          delay_secs: 0.5

  squawkers_response_a:
    alias: "Squawkers Response A"
    sequence:
      - service: remote.send_command
        target:
          entity_id: remote.office_lights
        data:
          device: "Squawkers McGraw"
          command: ["response_a"]
          num_repeats: 3
          delay_secs: 0.5
```

### Voice Control (Future - Saga Integration)

Once commands are working, integrate with Saga assistant:

```python
# In saga_assistant integration
if "squawkers" in user_command:
    if "dance" in user_command:
        squawkers.dance()
    elif "talk" in user_command:
        squawkers.response_mode_button("A")
```

---

## Troubleshooting

### Commands don't work

**Problem:** Sent command but Squawkers doesn't respond

**Solutions:**
1. Check line of sight between Broadlink and Squawkers' chest IR sensor
2. Increase `num_repeats` (GitHub issue suggests "gentle repeats with pause")
3. Try different distances (IR effective range: ~10-15 feet)
4. Check battery level in Squawkers
5. Verify command was learned correctly (re-learn if needed)

### Can't learn commands

**Problem:** Broadlink learning mode times out

**Solutions:**
1. Point remote directly at Broadlink (close range, ~6 inches)
2. Fresh batteries in remote
3. Try learning mode via HA UI instead of script
4. Check Broadlink firmware is up to date

### Wrong behaviors triggered

**Problem:** Command triggers unexpected behavior

**Possible causes:**
1. Squawkers may be in different mode than expected
2. Commands may be mapped differently in your unit
3. IR interference from other devices

**Solution:** Document actual behaviors and adjust automations accordingly

---

## IR Code Technical Details

### Format

All codes from GitHub repo are timing arrays in microseconds:

```python
[3000, 3000, 1000, 2000, 2000, 1000, ...]
#  ^     ^     ^     ^
# mark space mark space (alternating)
```

### Carrier Frequency

- **38kHz** (standard consumer IR)

### Protocol

- **Custom protocol** (not NEC, RC5, or other standard)
- 17 timing values per command
- Requires precise microsecond timing

### Conversion Process

The `broadlink_squawkers.py` module includes converters:

1. **Timing array → Pronto Hex** (`timing_to_pronto`)
2. **Pronto Hex → Broadlink base64** (`pronto_to_broadlink`)

**Note:** These converters are for reference. Broadlink API doesn't accept raw codes via Home Assistant, so learning mode is required.

---

## Next Steps

### Immediate:
1. ✅ Decide on hardware approach (borrow remote vs ESP32)
2. ⏳ Learn IR commands into Broadlink
3. ⏳ Test each command systematically
4. ⏳ Document discovered behaviors

### Short-term:
5. Create Home Assistant scripts/automations
6. Test different command combinations
7. Explore light sensor control (parallel approach)

### Long-term:
8. Integrate with Saga voice assistant
9. Create complex behavior sequences
10. Share discovered behaviors with community

---

## Files & Resources

### In This Project:
- `squawkers/broadlink_squawkers.py` - Control module
- `squawkers/test_squawkers.py` - Testing tool
- `squawkers/IR_CONTROL_RESEARCH.md` - Full research
- `squawkers/SENSOR_CONTROL_METHODS.md` - Alternative approach
- `squawkers/README.md` - Project overview

### External Resources:
- GitHub: https://github.com/playfultechnology/SquawkersMcGraw
- Broadlink HA Docs: https://www.home-assistant.io/integrations/broadlink/

---

## Questions?

Check the research docs in `squawkers/` or update this guide as you learn more!

**Happy Squawking! 🦜**
