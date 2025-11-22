# Squawkers IR Transmitter - Prototype Shield v.5 Setup

Clean, compact setup using your Proto Shield v.5!

## Parts Needed

### From Your Smraza S20 Kit:
- ✅ Arduino Uno
- ✅ Prototype Shield v.5
- ✅ 220Ω resistor (red-red-brown)
- ✅ Small piece of solid-core wire (22-24 AWG)
- ✅ USB cable

### Parts You Ordered:
- ✅ 940nm IR LED (from your 10-pack)

### Tools:
- Soldering iron + solder
- Wire strippers
- Needle-nose pliers (helpful)

---

## Wiring Diagram

```
Proto Shield v.5 Connections:
┌─────────────────────────────────┐
│  RESET    S1                    │
│   [O]    [O]                    │
│                                 │
│  LED1    LED2                   │
│   [●]    [●]                    │
│                                 │
│  [Proto Area]                   │
│     IR LED here                 │
│                                 │
└─────────────────────────────────┘

Connections to Make:
1. S1 button → Pin 2 (one jumper wire)
2. LED1 (+) → Pin 13 (one jumper wire)
3. IR LED → Pin 3 (via 220Ω resistor)
```

---

## Step-by-Step Assembly

### Step 1: Wire S1 Button to Pin 2

1. Look at S1 button - it has 2 solder pads/holes nearby
2. One side is already connected to GND (the shield does this)
3. Solder a wire from the **other pad** to **pin 2 header**
   - Use solid-core wire (easier to plug into headers)
   - About 1-2 inches long

**How to know which pad:**
- Try continuity test with multimeter to GND, or
- Just pick one - if it doesn't work, use the other pad!

### Step 2: Wire LED1 to Pin 13

1. Find LED1's **positive (+)** solder pad
   - Usually labeled, or has square pad vs round
2. Solder a wire from LED1 (+) to **pin 13 header**
   - LED1 is already connected to GND via resistor
   - Pin 13 is Arduino's built-in LED pin (perfect for status!)

### Step 3: Mount IR LED in Proto Area

**Option A: Soldered (permanent):**
1. Bend IR LED legs 90° so it points outward
2. Insert into proto area holes
3. Solder **shorter leg (−)** to a **GND hole/rail**
4. Solder **220Ω resistor** between **longer leg (+)** and **pin 3**

**Option B: Socket/Removable (flexible):**
1. Solder female header pins in proto area
2. Plug in IR LED with resistor on breadboard-style
3. Wire to pin 3 and GND

**Pro tip:** Orient IR LED so it points **forward off the shield** for easy aiming.

---

## Visual Aid - IR LED Wiring

```
IR LED (940nm, clear)
      ↓
   Long leg (+)
      ↓
  [220Ω Resistor]
      ↓
   Pin 3 ←───────────────┐
                         │
   Short leg (−)         │
      ↓                  │
   GND ──────────────────┘
```

---

## Testing After Assembly

### Step 1: Visual Inspection
- ✅ No solder bridges (shorts)
- ✅ IR LED polarity correct (long leg to resistor)
- ✅ All connections secure

### Step 2: Power On Test
1. Stack shield on Arduino Uno
2. Plug in USB
3. **LED1 should blink 3 times** (if sketch is uploaded)
4. This confirms LED1 wiring is correct!

### Step 3: Upload Sketch
1. Open `arduino_ir_transmitter.ino`
2. **Tools → Board → Arduino Uno**
3. **Tools → Port → (your port)**
4. **Upload** (→ button)

### Step 4: Serial Monitor Test
1. **Tools → Serial Monitor**
2. Set to **9600 baud**
3. Should see:
   ```
   Squawkers McGraw IR Transmitter
   ================================
   Proto Shield v.5 Configuration:
     IR LED on pin 3 (via 220ohm resistor)
     S1 button on pin 2
     LED1 status on pin 13

   Ready!
   ```

### Step 5: Button Test
1. **Press S1 button** (short press)
2. **LED1 should:**
   - Turn ON (solid)
   - Blink rapidly twice
   - Turn OFF
3. Serial Monitor shows: "Sending DANCE command..."

**If LED1 blinks, IR is being sent!** ✅

---

## Testing with Squawkers

### Positioning:
1. **Point IR LED at Squawkers' chest** (IR sensor location)
2. **Distance:** Start at 1-2 feet
3. **Angle:** Direct line of sight is best
4. **Power:** Make sure Squawkers is ON with fresh batteries

### Send Command:
1. Press S1 button (short press for DANCE)
2. Watch LED1 blink (confirms transmission)
3. **Watch Squawkers!** 🦜

### Commands:
- **Short press S1** = DANCE
- **Hold S1 for 2+ seconds** = RESET
- **Serial Monitor** = Type `d` (dance), `r` (reset), `a` (response A)

---

## LED Status Indicators

**LED1 (Status LED) tells you what's happening:**

| Pattern | Meaning |
|---------|---------|
| 3 quick blinks at startup | Arduino is ready |
| Solid ON | Transmitting IR code |
| 2 rapid blinks | Transmission complete |
| OFF | Idle, waiting for button |

This way you can see the Arduino is working even if Squawkers doesn't respond!

---

## If Squawkers Responds 🎉

**SUCCESS!** Now you can:

1. **Point Arduino at Broadlink** (instead of Squawkers)
2. **Use Home Assistant Learn Mode:**
   - Service: `remote.learn_command`
   - Entity: `remote.office_lights`
   - Device: `Squawkers McGraw`
   - Command: `dance`
3. **Press S1 button** on Arduino
4. **Broadlink captures the code!**
5. Repeat for all commands

Then you have full Home Assistant control! 🎊

---

## If Squawkers Doesn't Respond 😞

**Troubleshooting:**

1. **Check IR LED is transmitting:**
   - Point at phone camera
   - Press S1
   - Should see purple/white flashes on camera screen
   - If not, check IR LED polarity

2. **Verify timing:**
   - Serial Monitor shows "Code sent!"
   - LED1 blinks as described
   - Means Arduino is working correctly

3. **Try different positions:**
   - Closer (6 inches)
   - Different angles
   - Directly at chest IR sensor

4. **Verify Squawkers is responsive:**
   - Try manual triggers (noise, motion)
   - Check batteries
   - Look for power switch

5. **Consider:**
   - GitHub codes might be for different model
   - May need to adjust timing in code
   - Time to try light sensor method instead

---

## Next Steps

Once codes work with Squawkers:
→ See `squawkers/BROADLINK_LEARNING.md` (coming next!)

This will guide you through teaching Broadlink all 20 Squawkers commands using the Arduino as your "remote"!

**Happy building! 🔧🦜**
