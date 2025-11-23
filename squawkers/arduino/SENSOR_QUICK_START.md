# Squawkers McGraw Sensor Automation - Quick Start Guide

## TL;DR: Can We Do This?

**YES!** You can automate Squawkers McGraw using Home Assistant without modifying the toy.

**Best Method:** Smart LED light control of the forehead light sensor.
**Cost:** $10-30 for basic setup, $40-70 for full automation.
**Difficulty:** Easy to Medium.

---

## The Simplest Way to Get Started

### What You Need
1. Smart LED bulb or WLED strip (any RGB light that works with Home Assistant)
2. A way to position the LED near Squawkers' forehead (lamp, clip, mount)
3. Optional: Small box or hood to isolate the light sensor from ambient light

### How It Works
- Squawkers has a light sensor on its forehead
- Covering the sensor makes it say "I can't see you!" or "Where'd you go?"
- Uncovering makes it say "Peek-a-boo!" or "I see you!"
- You can trigger this by turning a smart LED on/off

### Basic Home Assistant Setup

```yaml
# configuration.yaml or automations.yaml

automation:
  # Trigger when someone arrives home
  - alias: "Squawkers Greets Family"
    trigger:
      - platform: state
        entity_id: person.family_member
        to: 'home'
    action:
      # Turn off light (cover sensor)
      - service: light.turn_off
        target:
          entity_id: light.squawkers_control
      - delay:
          seconds: 2
      # Turn on light (uncover sensor)
      - service: light.turn_on
        target:
          entity_id: light.squawkers_control
        data:
          brightness: 255

  # Morning greeting
  - alias: "Squawkers Morning Greeting"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - repeat:
          count: 3
          sequence:
            - service: light.turn_off
              target:
                entity_id: light.squawkers_control
            - delay:
                milliseconds: 500
            - service: light.turn_on
              target:
                entity_id: light.squawkers_control
              data:
                brightness: 255
            - delay:
                seconds: 2
```

---

## Next Level: Add Touch Sensor Control

### Option A: SwitchBot (Commercial)
**Cost:** $30-40 per button pusher
**Pros:** Reliable, official HA integration, easy to use
**Cons:** More expensive, requires hub for remote access

**What it does:** Physically presses touch sensors on Squawkers' back/head

**Setup:**
1. Buy SwitchBot Bot
2. Mount it near a touch sensor (back is easiest)
3. Add to Home Assistant via SwitchBot integration
4. Create automations to trigger presses

### Option B: DIY ESP32 + Servo
**Cost:** $7-15
**Pros:** Cheaper, fully customizable, ESPHome integration
**Cons:** Requires assembly and programming

**Shopping List:**
- ESP32 dev board ($5-10)
- 9g micro servo ($2-5)
- Jumper wires, mounting materials

**ESPHome Config:**
```yaml
esphome:
  name: squawkers-control
  platform: ESP32
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

output:
  - platform: ledc
    pin: GPIO18
    id: servo_output
    frequency: 50Hz

servo:
  - id: touch_actuator
    output: servo_output
    min_level: 3%
    max_level: 12%

switch:
  - platform: template
    name: "Squawkers Touch Sensor"
    turn_on_action:
      - servo.write:
          id: touch_actuator
          level: 100%
      - delay: 500ms
      - servo.write:
          id: touch_actuator
          level: 0%
```

---

## Troubleshooting

### Light Sensor Not Responding
- **Problem:** LED too far away
  - **Solution:** Move LED closer to forehead sensor
- **Problem:** Ambient light interference
  - **Solution:** Add a hood/box to isolate the sensor, or use a brighter LED
- **Problem:** LED not bright/dark enough
  - **Solution:** Increase brightness to 255, or add multiple LEDs

### Touch Sensor Not Working
- **Problem:** Servo not pressing hard enough
  - **Solution:** Adjust servo position or angle
- **Problem:** Wrong sensor location
  - **Solution:** Try different areas (back, head, beak sides)

### Inconsistent Behavior
- **Problem:** Toy battery low
  - **Solution:** Replace batteries (requires 4x C batteries)
- **Problem:** Timing too fast
  - **Solution:** Add longer delays between actions

---

## What Sensors Are Available?

| Sensor | Location | Trigger Method | Difficulty | Recommended |
|--------|----------|----------------|------------|-------------|
| **Light Sensor** | Forehead | Smart LED on/off | Easy | ⭐ YES |
| **Touch Sensors** | Back, head, beak | Mechanical actuator | Medium | ⭐ YES |
| **Tongue Switch** | Inside beak | Mechanical actuator | Hard | ⚠️ Difficult |
| **Microphone** | Chest | Play sounds/voice | Medium | ⚠️ Limited commands |
| **Eyelid Switches** | Eyes | N/A (feedback only) | N/A | ❌ Not user-triggerable |
| **Leg Switch** | Left leg | N/A (feedback only) | N/A | ❌ Not user-triggerable |

---

## Shopping List

### Starter Kit (Light Control Only)
- [ ] Smart RGB LED bulb OR WLED ESP32 board + LED strip ($10-30)
- [ ] Clip lamp or adjustable mount ($5-15)
- [ ] Optional: Small cardboard box for light isolation (free)

**Total: $15-45**

### Complete Kit (Light + Touch)
- [ ] Smart RGB LED bulb or WLED setup ($10-30)
- [ ] SwitchBot Bot ($30-40) OR ESP32 + servo ($7-15)
- [ ] If SwitchBot: SwitchBot Hub Mini for remote access ($40)
- [ ] Mounting supplies (Command strips, brackets, etc.) ($5-10)

**Total Commercial: $85-125**
**Total DIY: $22-55**

---

## Further Reading

- **Full Details:** See `SENSOR_CONTROL_METHODS.md` in this directory
- **IR Control Info:** See main `README.md` for infrared remote control options
- **GitHub Reference:** https://github.com/playfultechnology/SquawkersMcGraw

---

## Success Stories from the Community

The Halloween/haunt community has been automating Squawkers parrots for years:
- Synchronized multi-parrot displays for Tiki Room recreations
- Pirate fortune teller exhibits
- Motion-activated greeting displays
- Sound-reactive behaviors

**You're in good company!** This is a proven, reliable approach.
