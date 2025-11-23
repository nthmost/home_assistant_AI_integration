# Squawkers McGraw Home Assistant Integration

The goal is to use Home Assistant to control my Squawkers McGraw mechanical infrared-activated "pet".

**Reference:** https://github.com/playfultechnology/SquawkersMcGraw

We're not changing out the hardware, just activating its existing functions.

---

## Hardware Overview

**What it is:** Hasbro FurReal Friend animatronic parrot

**Actuators:**
- Head motor (controls eyelids and mouth movement)
- Hip motor (controls wings and body tilt)

**Sensors:**
- IR receiver (38kHz carrier frequency)
- Light sensor (in head)
- Tongue switch
- Eyelid limit switches (open/closed positions)
- Leg position switch

**Movement system:** Both motors use a clever cam system - reversing motor direction triggers different actuators.

---

## Control Methods

### Method 1: Original IR Remote (38kHz Infrared)

The toy ships with an IR remote that has:
- 3-position mode switch (Response / Command / Gags)
- 3 play mode buttons
- 6 programmable buttons (A-F)
- Custom record button
- Dance button
- Reset button
- Repeat button

**Protocol:** Custom timing-based IR protocol at 38kHz
- Each command = 17 timing values (mark/space durations in microseconds)
- Example: Dance = `{3000,3000,1000,2000,2000,1000,1000,2000,2000,1000,2000,1000,1000,2000,2000,1000,1000}`

**Challenge:** The original remote is RF (radio frequency), not IR, according to GitHub discussions. The reverse-engineered IR codes in the repo may not work with stock hardware.

### Method 2: ESP32 Replacement Controller

The playfultechnology repo includes an ESP32-based replacement that bypasses the original control board and drives the motors directly.

**Control interface:** Serial/Bluetooth character commands

**Available commands:**
- `!` - Report all sensor values
- `$` - Calibrate head to neutral
- `f` - Flap wings (reverse last direction)
- `b` - Blink eyes
- `z` - Move body direction 0
- `x` - Move body direction 1
- `o` - Open wings
- `s` - Shut/close wings
- `t` - Talk (play audio, move mouth/eyes)
- `1` - Move head direction 0
- `2` - Move head direction 1
- `3` - Open and close mouth
- `4` - Blink
- `5` - Open eyes
- `6` - Close eyes
- `7` - Body movement 0
- `8` - Body movement 1

**Bluetooth:** ESP32 advertises as "SquawkersMcGraw" over Bluetooth Serial

---

## Can We Do This At All?

### ✅ **YES - If using ESP32 replacement**

Replace the original control board with an ESP32 running the playfultechnology firmware. Then:
- Home Assistant can send Bluetooth Serial commands
- Or, modify ESP32 firmware to expose HTTP/MQTT API
- Full control over all movements and behaviors

**Pros:**
- Well-documented, proven to work
- Fine-grained control (individual movements)
- No IR hardware needed
- Can add additional sensors/features

**Cons:**
- Requires hardware modification (replacing control board)
- Loses original toy behaviors/sounds
- More invasive than we wanted

### ❓ **MAYBE - If using original IR/RF remote**

Use the stock remote control, but there's confusion:
- README claims 38kHz IR protocol
- GitHub issues suggest it's actually RF (radio frequency)
- One user reported RAW IR codes work "if repeated gently several times with pause"

**If IR:** Need IR transmitter (ESP32 + IR LED, Broadlink RM, etc.) to send the timing codes

**If RF:** Need RF transmitter on the correct frequency - much harder to implement

**Unknown:** What behaviors the buttons actually trigger (no documentation of what A-F do)

### 🔍 **NEEDS INVESTIGATION**

**Next steps to determine feasibility:**

1. **Confirm IR vs RF**: Open the remote and look at the transmitter chip
   - IR LED = infrared
   - RF antenna/module = radio frequency

2. **Test IR codes**: If IR, try sending the documented codes with an IR transmitter
   - Use an ESP32 + IR LED or Broadlink RM
   - Try the "gentle repeat with pause" technique from GitHub issue #2
   - Document which codes produce which behaviors

3. **Consider hybrid approach**:
   - Keep stock hardware for authenticity
   - Add ESP32 alongside (not replacing) to send IR/RF codes
   - Preserve original behaviors while adding HA control

---

## IR Command Reference

**Note:** These may not work if the remote is actually RF-based.

### Common commands (all modes):
- **Dance**: `{3000,3000,1000,2000,2000,1000,1000,2000,2000,1000,2000,1000,1000,2000,2000,1000,1000}`
- **Reset**: `{3000,3000,1000,2000,2000,1000,2000,1000,1000,2000,1000,2000,2000,1000,1000,2000,1000}`

### Response Mode:
- **Button A**: `{3000,3000,1000,2000,1000,2000,1000,2000,1000,2000,2000,1000,1000,2000,2000,1000,1000}`
- **Button B**: `{3000,3000,1000,2000,1000,2000,1000,2000,2000,1000,1000,2000,2000,1000,1000,2000,1000}`
- **Button C**: `{3000,3000,1000,2000,1000,2000,1000,2000,2000,1000,2000,1000,2000,1000,2000,1000,1000}`
- **Button D**: `{3000,3000,1000,2000,1000,2000,2000,1000,1000,2000,2000,1000,1000,2000,1000,2000,1000}`
- **Button E**: `{3000,3000,1000,2000,1000,2000,2000,1000,2000,1000,1000,2000,1000,2000,2000,1000,1000}`
- **Button F**: `{3000,3000,1000,2000,1000,2000,2000,1000,2000,1000,2000,1000,2000,1000,1000,2000,1000}`

### Command Mode:
- **Button A**: `{3000,3000,1000,2000,1000,2000,1000,2000,1000,2000,2000,1000,2000,1000,1000,2000,1000}`
- **Button B**: `{3000,3000,1000,2000,1000,2000,1000,2000,2000,1000,1000,2000,2000,1000,2000,1000,1000}`
- **Button C**: `{3000,3000,1000,2000,1000,2000,2000,1000,1000,2000,1000,2000,1000,2000,1000,2000,1000}`
- **Button D**: `{3000,3000,1000,2000,1100,2000,2000,1000,1000,2000,2000,1000,1100,2000,2000,1000,1000}`
- **Button E**: `{3000,3000,1000,2000,1000,2000,2000,1000,2000,1000,1000,2000,2000,1000,1000,2000,1000}`
- **Button F**: `{3000,3000,1000,2000,1000,2000,2000,1000,2000,1000,2000,1000,2000,1000,2000,1000,1000}`

### Gags Mode:
- **Button A**: `{3000,3000,1000,2000,1000,2000,1000,2000,1000,2000,2000,1000,2000,1000,2000,1000,1000}`
- **Button B**: `{3000,3000,1000,2000,1000,2000,1000,2000,2000,1000,2000,1000,1000,2000,1000,2000,1000}`
- **Button C**: `{3000,3000,1000,2000,1000,2000,2000,1000,1000,2000,1000,2000,1000,2000,2000,1000,1000}`
- **Button D**: `{3000,3000,1000,2000,1000,2000,2000,1000,1000,2000,2000,1000,2000,1000,1000,2000,1000}`
- **Button E**: `{3000,3000,1000,2000,1000,2000,2000,1000,2000,1000,1000,2000,2000,1000,2000,1000,1000}`
- **Button F**: `{3000,3000,1000,2000,2000,1000,1100,2000,1000,2000,1000,2000,1000,2000,1000,2000,1000}`

**Behavior unknown** - no documentation of what these buttons actually do.

---

## Questions to Answer

1. Is the remote IR or RF?
2. Do the documented IR codes work with stock hardware?
3. What do the different mode buttons (A-F) actually make it do?
4. Can we trigger original sounds/behaviors, or only motor movements?
5. What IR/RF hardware do we already have available in the HA setup?
