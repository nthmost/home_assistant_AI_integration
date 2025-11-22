# Squawkers McGraw: Sensor-Based Control Methods

## Executive Summary

This report details alternative methods to trigger Squawkers McGraw behaviors using its built-in sensors instead of the IR/RF remote control. Research reveals **three viable sensor manipulation approaches** that don't require modifying the toy itself, plus creative automation solutions from the maker community.

---

## Built-In Sensors

Squawkers McGraw contains multiple sensors that trigger specific behaviors:

### 1. Light Sensor (Forehead)
**Location:** Top of head (forehead area)
**Wiring:** Red, Black, Grey, White wires to control daughterboard at base of head
**Type:** Likely phototransistor or photoresistor

**Triggered Behaviors:**
- **Covering sensor** → Toy blinks, says "I can't see you" or "Where'd you go?"
- **Uncovering sensor** → Says "Peek-a-boo" or "I see you"
- **Rapid covering/uncovering** → Initiates Peek-A-Boo game interaction
- **Hand placement** → General response to light level changes

### 2. Tongue Switch
**Location:** Inside beak mechanism
**Wiring:** 2x Blue wires (one ground)
**Type:** Momentary push switch

**Triggered Behaviors:**
- Feeding time interactions
- Should only be activated during feeding mode
- Mouth-related responses

### 3. Eyelid Limit Switches (x2)
**Location:** Eye mechanism housing
**Wiring:**
- Fully-open switch: 2x Orange wires (one ground)
- Fully-closed switch: 2x Purple wires (one ground)
- Neutral position: Neither switch pressed

**Function:** Position feedback for motor control (not user-triggerable)

### 4. Leg Position Switch
**Location:** Left leg mechanism
**Function:** Detects specific positions during body movement cycle (motor feedback, not user-triggerable)

### 5. Touch Sensors
**Locations:** Head, beak, back
**Note:** Mentioned in official documentation but not well-documented in reverse engineering materials

**Triggered Behaviors:**
- "Activating any of the touch sensors causes the toy to respond by moving or making various noises"
- Sensitive to "even the slightest touch or nearby movement"

### 6. Microphone
**Location:** Chest area (with IR receiver)
**Function:** Voice command detection, feeding time sounds

---

## Viable Sensor-Based Control Methods

## METHOD 1: Light Sensor Automation (Most Promising)

### Overview
The light sensor is the **most accessible and reliable** sensor for external automation without toy modification.

### Control Techniques

#### A. Smart LED Control (Recommended)
**Hardware Required:**
- Smart LED bulb or strip (Philips Hue, WLED, etc.)
- Home Assistant integration
- Positioning mount/stand near toy's head

**Implementation:**
```yaml
# Home Assistant automation example
automation:
  - alias: "Trigger Squawkers Peek-a-boo"
    trigger:
      - platform: state
        entity_id: binary_sensor.living_room_motion
        to: 'on'
    action:
      # Darken LED to trigger "can't see you"
      - service: light.turn_off
        target:
          entity_id: light.squawkers_control_led
      - delay: 2
      # Brighten LED to trigger "I see you"
      - service: light.turn_on
        target:
          entity_id: light.squawkers_control_led
        data:
          brightness: 255
```

**Advantages:**
- No physical contact with toy
- Fully reversible
- Works with existing HA smart lights
- Can create complex patterns (rapid blink sequences)
- Silent operation
- Remote controllable

**Disadvantages:**
- Requires optimal LED positioning
- Ambient lighting may interfere
- May need light isolation (box/enclosure)

#### B. Motorized Light Blocker
**Hardware Required:**
- Small servo motor (9g micro servo)
- ESP32/Arduino board
- Opaque material flag/flap
- Mount/bracket to position servo

**Implementation:**
- Servo swings opaque material in front of light sensor
- ESP32 receives commands from Home Assistant (ESPHome)
- More reliable than light intensity changes
- Creates definitive on/off transitions

**Advantages:**
- Mechanical reliability
- Independent of ambient lighting
- Clear state transitions
- Cost-effective ($5-15 total)

**Disadvantages:**
- Requires physical mounting near toy
- Potential noise from servo movement
- Needs power supply for servo

#### C. Ambient Room Light Control
**Hardware Required:**
- Smart switches for room lights
- Optionally: smart blinds/curtains

**Implementation:**
- Turn room lights on/off to trigger sensor
- Works best in controlled lighting environments
- Can integrate with existing room automation

**Advantages:**
- Uses existing smart home infrastructure
- No additional hardware near toy
- Natural-looking interaction

**Disadvantages:**
- Least reliable (ambient light leaks)
- Affects entire room lighting
- Slow response time
- Not suitable for daytime use

---

## METHOD 2: Mechanical Switch Actuation

### Overview
Use servo motors or commercial button pushers to physically press the tongue switch, back touch sensors, or head sensors.

### Commercial Solutions

#### SwitchBot Bot
**Product:** SwitchBot Smart Switch Button Pusher
**Price:** ~$30-40 per unit
**Battery Life:** 600 days
**Home Assistant Integration:** Yes (via Bluetooth or Hub)

**Features:**
- Mechanical finger that pushes/presses switches
- Adhesive mounting (no toy modification)
- Switch mode and Press mode
- WiFi control via SwitchBot Hub
- Bluetooth Low Energy (BLE) direct control
- Voice assistant compatible

**Implementation for Squawkers:**
- Mount near tongue switch inside beak (tricky but possible)
- Mount on back touch sensor (easier)
- Configure press duration and timing
- Integrate with HA via SwitchBot integration

**Pros:**
- Commercial product (reliable)
- Official HA integration available
- No custom electronics needed
- Removable (non-destructive)

**Cons:**
- Expensive for multiple sensors
- Mounting may be challenging for internal switches
- BLE range limitations
- Requires hub for remote access

### DIY Solutions

#### ESP32 + Servo Button Pusher
**Hardware Required:**
- ESP32 development board ($5-10)
- 9g micro servo motor ($2-5)
- ESPHome firmware (free)
- 3D printed or crafted actuator arm
- USB power supply

**Implementation:**
```yaml
# ESPHome configuration
esphome:
  name: squawkers-control
  platform: ESP32

servo:
  - id: tongue_presser
    output: servo_output

switch:
  - platform: template
    name: "Press Tongue Switch"
    turn_on_action:
      - servo.write:
          id: tongue_presser
          level: 100%  # Press
      - delay: 500ms
      - servo.write:
          id: tongue_presser
          level: 0%    # Release
```

**Advantages:**
- Low cost ($7-15 total)
- Full Home Assistant integration via ESPHome
- Highly customizable timing
- Can control multiple servos from one ESP32
- WiFi connectivity
- OTA updates

**Disadvantages:**
- DIY assembly required
- Need to design/fabricate mounting
- Servo noise
- Requires positioning precision

---

## METHOD 3: Sound/Microphone Activation

### Overview
Trigger behaviors by playing sounds or speaking commands near the microphone.

### Implementation Options

#### A. Smart Speaker Near Toy
**Hardware Required:**
- ESP32 with speaker/DAC
- Home Assistant TTS integration
- Positioning near toy's chest microphone

**Use Cases:**
- Trigger "Peek-A-Boo" voice command
- Play feeding time sounds
- Voice command sequences

**Advantages:**
- Non-contact method
- Uses existing HA TTS capabilities
- Can automate voice interactions

**Disadvantages:**
- Limited documented commands
- Ambient noise interference
- Requires precise audio playback
- Not all behaviors are voice-triggered

---

## Advanced Automation Strategies

### Multi-Sensor Orchestration
Combine multiple sensor triggers for complex behaviors:

```yaml
# Example: Motion detection triggers peek-a-boo sequence
automation:
  - alias: "Squawkers Greets Visitors"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: 'on'
    action:
      # Cover light sensor
      - service: light.turn_off
        target:
          entity_id: light.squawkers_led
      - delay: 1
      # Trigger voice command
      - service: tts.speak
        data:
          entity_id: media_player.squawkers_speaker
          message: "Peek-a-boo!"
      - delay: 2
      # Uncover light sensor
      - service: light.turn_on
        target:
          entity_id: light.squawkers_led
```

### Time-Based Behaviors
Schedule regular interactions to keep toy "alive":

```yaml
automation:
  - alias: "Squawkers Morning Greeting"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: script.squawkers_peekaboo
```

---

## Community Solutions

### Halloween Haunt Community Modifications

The haunt/Halloween community has extensive experience with Squawkers automation:

#### All-in-One Control Boards
**Product:** SQUAWKER TALKERS board
**Manufacturer:** Custom maker boards (info@audioservocontroller.com)
**Price:** $74
**Features:**
- Auto beak sync
- Random body movement
- Built-in 3W stereo amplifier with volume control
- Single 5V 2A power supply
- Multi-bird synchronization (stereo channels)
- No perch or remote needed

**Note:** This solution requires opening the toy and connecting to internal wiring, which **does not meet your "no modification" requirement**, but is included for completeness.

#### Tiki Room Recreations
Forum users have created multi-parrot synchronized displays:
- External USB 5.1 sound cards for 4-channel control
- MP3 players with stereo files control two birds
- Background music + individual bird tracks

---

## Recommended Implementation Path

### Phase 1: Light Sensor Control (Start Here)
**Why:** Non-invasive, reversible, uses existing HA infrastructure

**Hardware Shopping List:**
- Smart RGB LED bulb or WLED strip controller ($10-30)
- Small enclosure or hood to isolate light sensor ($5-10 or 3D print)
- Mounting supplies (Command strips, stand, etc.)

**Steps:**
1. Position smart LED near Squawkers' forehead
2. Test manual on/off to verify sensor detection
3. Create HA automations for light control
4. Refine timing and brightness levels
5. Add light isolation if needed

**Expected Success Rate:** High (light sensor is confirmed to work)

### Phase 2: Mechanical Touch Automation
**Why:** Adds more interaction variety, proven technology

**Hardware Shopping List:**
Option A (Commercial):
- SwitchBot Bot ($30-40)
- SwitchBot Hub Mini (if remote access needed) ($40)

Option B (DIY):
- ESP32 dev board ($5-10)
- 9g micro servo ($2-5)
- Mounting materials ($5-10)

**Steps:**
1. Identify accessible touch sensors (back sensor recommended)
2. Mount SwitchBot or DIY servo actuator
3. Configure press timing in HA
4. Create automation triggers
5. Test and refine

**Expected Success Rate:** Medium-High (depends on mounting precision)

### Phase 3: Multi-Sensor Orchestration
**Why:** Complex, lifelike behaviors

**Combine:**
- Light sensor control
- Touch sensor actuation
- Sound/voice triggers
- Motion detection
- Time-based scheduling

---

## Feasibility Assessment

### Without Hardware Modification to Toy: ✅ FEASIBLE

**Best Methods (in order):**
1. **Light sensor control via smart LED** - Highly feasible, non-invasive, reversible
2. **Mechanical touch actuation** - Feasible with careful mounting, no internal modification
3. **Microphone/voice triggers** - Limited feasibility (few documented commands)

### Hardware Requirements Summary

**Minimum Setup (Light Control Only):**
- Cost: $10-30
- Components: Smart LED + mounting
- Complexity: Low
- HA Integration: Native (existing smart light integrations)

**Recommended Setup (Light + Touch):**
- Cost: $40-70
- Components: Smart LED + SwitchBot or ESP32 + servo
- Complexity: Medium
- HA Integration: Native (SwitchBot integration) or ESPHome

**Advanced Setup (Full Automation):**
- Cost: $70-150
- Components: Multiple LEDs, servos, speakers, ESP32 boards
- Complexity: High
- HA Integration: ESPHome + custom automations

---

## Key Findings from Maker Community

### What Works:
- Light sensor is reliable and well-documented
- Touch sensors are sensitive and responsive
- Mechanical actuation is proven (haunt community uses it extensively)
- ESP32 + ESPHome integration is robust
- Multiple parrots can be synchronized

### What Doesn't Work / Unknown:
- Original remote may be RF, not IR (conflicting reports)
- Documented IR codes have mixed success reports
- Touch sensor exact locations not fully mapped
- Voice command vocabulary is limited
- Microphone sensitivity thresholds unknown

### Common Pitfalls:
- Ambient lighting interference with light sensor
- Servo motor noise during operation
- Mounting challenges for internal sensors (tongue)
- Power supply requirements for multiple devices
- WiFi/Bluetooth range limitations

---

## Technical References

### Primary Source
- **GitHub Repository:** https://github.com/playfultechnology/SquawkersMcGraw
  - Reverse engineering details
  - Wiring diagrams
  - ESP32 replacement firmware
  - Community discussions

### Hardware Integration Tools
- **ESPHome:** https://esphome.io/ - ESP32/ESP8266 firmware for HA
- **SwitchBot HA Integration:** Native Home Assistant integration
- **WLED:** https://wled.me/ - LED control firmware

### Community Forums
- Haunt Forum (hauntforum.com) - Halloween animatronics community
- Halloween Forum (halloweenforum.com) - Squawkers modification discussions

---

## Conclusion

**Sensor-based control of Squawkers McGraw is highly viable without modifying the toy itself.** The light sensor provides the most accessible entry point, with proven effectiveness for triggering behaviors. Combined with mechanical touch actuation, you can create rich, automated interactions through Home Assistant.

**Recommended Next Steps:**
1. Purchase smart LED bulb/strip for light sensor control
2. Test light sensor responsiveness with manual control
3. Implement basic HA automations for peek-a-boo behavior
4. Evaluate need for touch sensor actuation
5. Expand to multi-sensor orchestration based on desired complexity

**Total Investment (Recommended Path):** $40-70 for reliable automation with no toy modification.
