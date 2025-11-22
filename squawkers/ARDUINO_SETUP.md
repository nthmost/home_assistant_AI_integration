# Arduino IR Transmitter Setup for Squawkers McGraw

This guide helps you use your Arduino Uno to transmit the Squawkers IR codes and test if they work.

## What You Need

From your Smraza S20 kit:
- ✅ Arduino Uno board
- ✅ IR LED (940nm - clear LED, not colored)
- ✅ 220Ω resistor (red-red-brown)
- ✅ Push button
- ✅ 10kΩ resistor for button (brown-black-orange)
- ✅ Breadboard
- ✅ Jumper wires
- ✅ USB cable (to connect to computer)

## Step 1: Install IRremote Library

1. Open Arduino IDE
2. Go to **Sketch → Include Library → Manage Libraries**
3. Search for **"IRremote"**
4. Install **"IRremote" by shirriff/z3t0/ArminJo**
5. Close Library Manager

## Step 2: Wire the Circuit

### IR LED Connection (Pin 3):
```
Arduino Pin 3 → 220Ω resistor → IR LED (+) → IR LED (-) → Arduino GND
```

**Important:**
- IR LED is usually **clear** (not red/blue/green)
- Longer leg = positive (+)
- Shorter leg = negative (-)

### Button Connection (Pin 2):
```
Arduino Pin 2 → Button → GND
Arduino Pin 2 → 10kΩ resistor → 5V (pull-up)
```

Or use Arduino's internal pull-up (code already configured for this).

### Simplified Breadboard Layout:
```
Arduino 5V  ────────┬─────────────────────
                    │
Arduino Pin 3 ─── [220Ω] ─── IR LED(+)
                              IR LED(-) ─── GND

Arduino Pin 2 ─────┬─── Button ─── GND
                   │
                   └─── [10kΩ] ─── 5V

Arduino GND ─────────────────────────────
```

## Step 3: Upload the Sketch

1. Open `arduino_ir_transmitter.ino` in Arduino IDE
2. Select **Tools → Board → Arduino Uno**
3. Select **Tools → Port → (your Arduino's port)**
4. Click **Upload** (→ button)
5. Wait for "Done uploading"

## Step 4: Test with Squawkers

1. **Open Serial Monitor** (Tools → Serial Monitor)
2. Set baud rate to **9600**
3. **Position:** Point IR LED at Squawkers' chest (IR sensor)
4. **Distance:** Start close (1-2 feet), IR has limited range
5. **Press the button** or type `d` in Serial Monitor

### What should happen:
- Serial Monitor shows "Sending DANCE command..."
- **Squawkers should dance!** 🦜

### If nothing happens:
- Check IR LED is correct way around (swap if needed)
- Move closer to Squawkers
- Make sure Squawkers is powered on
- Try typing `d` in Serial Monitor multiple times

## Step 5: Try Different Commands

In Serial Monitor, type:
- `d` = Dance command
- `r` = Reset command
- `a` = Response A (unknown behavior)

Or use the button:
- **Short press** = Dance
- **Hold 2 seconds** = Reset

## Step 6: If It Works - Learn with Broadlink!

Once Squawkers responds to the Arduino:

1. **Point Arduino IR LED at Broadlink** (instead of Squawkers)
2. **In Home Assistant:**
   - Go to Developer Tools → Services
   - Service: `remote.learn_command`
   - Entity: `remote.office_lights`
   - Device: `Squawkers McGraw`
   - Command: `dance`
   - Timeout: 20
3. **Click "Call Service"**
4. **Press Arduino button** within 20 seconds
5. **Broadlink captures the code!**
6. Repeat for all commands you want

Now you can use `remote.send_command` in HA with the learned codes!

## Troubleshooting

### "IRremote library not found"
- Install via Library Manager (Step 1)

### LED doesn't light up
- Check wiring
- Swap IR LED polarity
- Measure with multimeter (should be ~1.2V forward)

### Serial Monitor shows errors
- Check baud rate is 9600
- Re-upload sketch

### Squawkers doesn't respond but LED works
- Codes might be for different model
- Try increasing repeats in code
- Try different distances/angles

## Next: Add More Commands

To add more Squawkers commands to the Arduino sketch:

1. Get timing array from `squawkers/broadlink_squawkers.py`
2. Add new `const uint16_t COMMAND_NAME_CODE[]` array
3. Add case in `loop()` to send it
4. Re-upload sketch

---

**Good luck! 🦜**
