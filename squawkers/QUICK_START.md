# Squawkers McGraw - Quick Start Guide

**Goal:** Control Squawkers McGraw via Home Assistant WITHOUT modifying the toy

---

## TL;DR - What to Buy

### Option 1: Easiest (Recommended for Most)
**Broadlink RM4 Mini** - $22-26 on Amazon
- Plug and play
- 30 minute setup
- Native Home Assistant support

### Option 2: Best Value (Recommended for DIY)
**ESP32 IR Blaster Kit** - $8-15 total
- ESP32 board ($5-10)
- IR LED 940nm ($1-2)
- 2x resistors, 1x transistor ($0.50)
- 2-4 hours assembly + setup
- ESPHome integration

### Option 3: If Remote is RF (Not IR)
**Broadlink RM4 Pro** - $36 on Amazon
- Supports both IR (38kHz) and RF (433MHz)
- Same easy setup as RM4 Mini

---

## Before You Buy: IR or RF Test

**Use your phone camera:**
1. Open camera app
2. Point Squawkers remote at camera
3. Press any button
4. **See purple/white flashes?** = IR → Buy RM4 Mini or ESP32
5. **No flashes?** = RF → Buy RM4 Pro

---

## Quick Comparison

| Feature | Broadlink RM4 Mini | ESP32 DIY | Broadlink RM4 Pro |
|---------|-------------------|-----------|-------------------|
| **Cost** | $22-26 | $8-15 | $36 |
| **Setup Time** | 30 min | 2-4 hours | 30 min |
| **Skill Level** | Beginner | Intermediate | Beginner |
| **IR Support** | ✅ Yes | ✅ Yes | ✅ Yes |
| **RF Support** | ❌ No | ❌ No | ✅ Yes (433MHz) |
| **HA Integration** | ✅ Native | ✅ ESPHome | ✅ Native |
| **Learning** | ✅ Yes | ✅ Yes | ✅ Yes |
| **DIY Control** | ❌ Proprietary | ✅ Full | ❌ Proprietary |

---

## Available IR Commands

All commands use **38kHz carrier frequency** with timing arrays.

### Common Commands (All Modes)
- **Dance** - Makes parrot dance
- **Reset** - Reset to default state

### Mode-Specific Commands
- **Response Mode:** Buttons A-F (behaviors unknown)
- **Command Mode:** Buttons A-F (behaviors unknown)
- **Gags Mode:** Buttons A-F (behaviors unknown)

**Note:** Original remote behavior not documented. You'll need to test and document what each button does!

---

## Next Steps

1. ✅ **Test if IR or RF** (phone camera test - 30 seconds)
2. 📦 **Order hardware** based on test results
3. 🔧 **Follow setup guide** in IR_CONTROL_RESEARCH.md
4. 🧪 **Test commands** and document behaviors
5. 🎙️ **Integrate with Saga assistant** for voice control

---

## Full Documentation

See `/Users/nthmost/projects/git/home_assistant_AI_integration/squawkers/IR_CONTROL_RESEARCH.md` for:
- Detailed hardware specs
- Complete wiring diagrams
- ESPHome configuration examples
- Home Assistant automation examples
- Troubleshooting tips
- Purchase links

---

## Voice Control Example

Once integrated with Home Assistant + Saga:

**You:** "Hey Saga, make Squawkers dance"
**Saga:** *sends command to HA*
**Home Assistant:** *triggers IR transmitter*
**Squawkers:** 🦜💃 *dances*

---

**Created:** November 12, 2025
**Status:** Ready for hardware acquisition
