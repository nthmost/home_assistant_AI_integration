# Squawkers McGraw IR Control Research Report

**Research Date:** November 12, 2025
**Objective:** Find methods to control Squawkers McGraw WITHOUT the original remote and WITHOUT hardware modification

---

## Executive Summary

After comprehensive research, there are **THREE VIABLE OPTIONS** for controlling Squawkers McGraw via Home Assistant without modifying the toy itself:

1. **Broadlink RM4 Mini** - Easiest plug-and-play solution ($22-26)
2. **ESP32 IR Blaster with ESPHome** - Best value for DIY enthusiasts ($8-15)
3. **Universal IR Learning Remote** - Limited compatibility, not recommended

**Key Finding:** The GitHub repository (playfultechnology/SquawkersMcGraw) contains complete IR code timings at 38kHz that can be transmitted using standard IR hardware. However, there are reports suggesting the original remote may be RF-based, which requires further investigation.

---

## Option 1: Broadlink RM4 Mini (RECOMMENDED FOR EASE)

### Overview
Commercial IR blaster with native Home Assistant integration and IR learning capability.

### Hardware Details
- **Model:** Broadlink RM4 Mini (IR-only version)
- **Frequency:** 38kHz IR carrier (matches Squawkers McGraw)
- **Range:** 8-10 meters
- **Connectivity:** 2.4GHz WiFi
- **Integration:** Native Home Assistant support with auto-discovery

### Cost
- **RM4 Mini:** $22-26 (Amazon, eBay, AliExpress)
- **RM Mini 3:** $10-20 (older model, functionally identical)
- **Alternative:** RM4 Pro at $36 (adds 433MHz RF support - useful if remote is RF)

### Home Assistant Setup Process

1. **Physical Setup:**
   - Plug in Broadlink device
   - Connect via Broadlink app for initial WiFi setup
   - Position within IR range of Squawkers McGraw

2. **Home Assistant Configuration:**
   ```yaml
   # Configuration automatically discovered
   # Or manually add in configuration.yaml:
   remote:
     - platform: broadlink
       host: 192.168.1.XXX
       mac: 'AA:BB:CC:DD:EE:FF'
   ```

3. **Learning IR Codes:**
   ```yaml
   # Developer Tools > Services
   service: remote.learn_command
   data:
     device: squawkers
     command: dance
     target:
       entity_id: remote.broadlink_rm4_mini

   # Point original Squawkers remote at Broadlink, press button
   # LED will blink when learning
   ```

4. **Sending Commands:**
   ```yaml
   service: remote.send_command
   data:
     device: squawkers
     command: dance
     target:
       entity_id: remote.broadlink_rm4_mini
   ```

5. **Alternative: Manually Program IR Codes**
   Since the GitHub repo has documented timing codes, you can program them directly:
   ```yaml
   # Use remote.send_command with raw timing data
   # Convert microsecond timings to Broadlink format
   ```

### Pros
- Zero technical knowledge required
- Works immediately after setup
- Can learn from original remote OR use documented codes
- Excellent Home Assistant integration
- Reliable, tested hardware
- Local control (no cloud after setup)
- Can control multiple IR devices
- 50,000+ device database (though Squawkers isn't in it)

### Cons
- Costs $22-26
- Requires manufacturer app for initial setup
- Proprietary firmware
- RF model (RM4 Pro) costs more at $36

### Where to Buy
- **Amazon:** BroadLink RM4 Mini - $25.99
- **eBay:** BroadLink RM4 Mini - $22+
- **Broadlink Official Store:** ebroadlink.com
- **AliExpress:** Various sellers, $20-25

---

## Option 2: ESP32 IR Blaster with ESPHome (BEST VALUE)

### Overview
DIY solution using ESP32 microcontroller with ESPHome firmware for Home Assistant integration.

### Hardware Required

| Component | Specs | Cost | Source |
|-----------|-------|------|--------|
| ESP32 Development Board | ESP32-WROOM or compatible | $5-10 | AliExpress, Amazon |
| IR LED | 940nm, 5mm, 20mA+ | $0.50-2 | Electronic suppliers |
| NPN Transistor | 2N2222 or PN2222 | $0.10-0.50 | Electronic suppliers |
| Resistor (LED) | 100-330Ω, 1/4W | $0.05 | Electronic suppliers |
| Resistor (Transistor) | 1kΩ, 1/4W | $0.05 | Electronic suppliers |
| **Optional:** IR Receiver | VS1838B or TSOP38238 | $1-2 | For learning codes |
| Breadboard/Perfboard | For assembly | $2-5 | Electronic suppliers |
| USB Cable | Micro-USB or USB-C | $2-5 | Likely already owned |

**Total Cost:** $8-15 for basic transmitter, $10-17 with IR receiver for learning

### Wiring Diagram
```
ESP32 GPIO Pin (e.g., GPIO4)
    |
    ├── 1kΩ resistor ──→ Transistor Base (2N2222)
    |
Transistor Collector ──→ IR LED Cathode (-)
Transistor Emitter ────→ GND
IR LED Anode (+) ──┬───→ 100Ω resistor ──→ 5V/3.3V
                   └───→ (resistor value depends on supply voltage)

Optional IR Receiver:
VS1838B Data Pin ──→ ESP32 GPIO (e.g., GPIO14)
VS1838B VCC ───────→ 3.3V
VS1838B GND ───────→ GND
```

### ESPHome Configuration

```yaml
# squawkers_ir_blaster.yaml
esphome:
  name: squawkers-ir-blaster
  platform: ESP32
  board: esp32dev

wifi:
  ssid: "YourWiFiSSID"
  password: "YourWiFiPassword"

api:
  encryption:
    key: "your-encryption-key"

ota:
  password: "your-ota-password"

logger:

# IR Transmitter
remote_transmitter:
  pin: GPIO4
  carrier_duty_percent: 50%  # For IR (use 100% for RF)

# Optional: IR Receiver for learning codes
remote_receiver:
  pin:
    number: GPIO14
    inverted: true
  dump: all  # Show all received codes in log
  tolerance: 25%

# Define Squawkers commands as buttons
button:
  - platform: template
    name: "Squawkers Dance"
    on_press:
      - remote_transmitter.transmit_raw:
          carrier_frequency: 38kHz
          code: [3000, 3000, 1000, 2000, 2000, 1000, 1000, 2000, 2000, 1000, 2000, 1000, 1000, 2000, 2000, 1000, 1000]

  - platform: template
    name: "Squawkers Reset"
    on_press:
      - remote_transmitter.transmit_raw:
          carrier_frequency: 38kHz
          code: [3000, 3000, 1000, 2000, 2000, 1000, 2000, 1000, 1000, 2000, 1000, 2000, 2000, 1000, 1000, 2000, 1000]

  - platform: template
    name: "Squawkers Response Button A"
    on_press:
      - remote_transmitter.transmit_raw:
          carrier_frequency: 38kHz
          code: [3000, 3000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 2000, 1000, 1000, 2000, 2000, 1000, 1000]

  # Add more buttons for each command...
```

### Setup Process

1. **Hardware Assembly:**
   - Solder components on breadboard/perfboard according to wiring diagram
   - Connect ESP32 via USB to computer
   - Test basic functionality

2. **ESPHome Installation:**
   ```bash
   # Install ESPHome (if not already installed)
   pip install esphome

   # Create and compile firmware
   esphome run squawkers_ir_blaster.yaml

   # Flash to ESP32
   # Follow on-screen instructions
   ```

3. **Home Assistant Integration:**
   - ESPHome device auto-discovered in Home Assistant
   - Add integration via Settings > Devices & Services
   - Buttons appear as entities

4. **Learning Original Remote (Optional):**
   - If you have IR receiver wired up
   - Watch ESPHome logs while pressing remote buttons
   - Copy raw timing codes into configuration

5. **Testing:**
   - Use buttons in Home Assistant to trigger commands
   - Adjust IR LED positioning/power if needed
   - May need to repeat commands (GitHub issue #2 mentions "gentle repeat with pause")

### Pros
- Cheapest solution ($8-15)
- Complete control and customization
- Open-source hardware and software
- No proprietary apps needed
- Can add multiple IR LEDs for better range
- Can integrate other sensors (temperature, motion, etc.)
- Fully local, no cloud dependencies
- Great learning opportunity
- Active community support

### Cons
- Requires DIY assembly and soldering
- More technical setup (ESPHome, YAML configuration)
- No pre-built device database
- Manual code entry or learning required
- Troubleshooting may be needed

### Additional Resources
- ESPHome IR Transmitter Docs: https://esphome.io/components/remote_transmitter/
- ESPHome IR Receiver Docs: https://esphome.io/components/remote_receiver/
- Community Guide: "Faking an IR remote control using ESPHome"
- GitHub: Multiple ESP32 IR blaster projects available

---

## Option 3: Universal IR Learning Remote (NOT RECOMMENDED)

### Overview
Physical universal remote controls that can learn IR codes from the original Squawkers remote.

### Compatible Devices
- **Logitech Harmony 600:** Reports suggest DOES NOT WORK with Squawkers
- **SofaBaton X1S:** Modern Harmony alternative, no confirmed compatibility
- **Generic Learning Remotes:** May work but unconfirmed

### Issues
- Logitech Harmony database does not include Squawkers McGraw
- Manual learning mode required
- One user confirmed Harmony 600 fails to sync properly
- No confirmed working universal remotes found in research
- These don't integrate with Home Assistant directly

### Cost
- Generic learning remotes: $15-30
- SofaBaton X1S: $50-80

### Verdict
**Not recommended** - no confirmed compatibility, doesn't integrate with Home Assistant, more expensive than better options.

---

## Important Technical Considerations

### IR vs RF Confusion

There is conflicting information about whether the original Squawkers remote uses IR or RF:

**Evidence for IR:**
- GitHub repo documents 38kHz IR protocol
- Timing codes provided for IR transmission
- Toy has documented IR receiver at 38kHz

**Evidence for RF:**
- GitHub issue #2 suggests remote may be RF-based
- One user mentions codes work "if repeated gently several times with pause"
- Some reports of inconsistent IR performance

**Recommendation:**
1. **Try IR first** - documented codes, cheaper hardware
2. **If IR fails consistently**, consider RF options:
   - Broadlink RM4 Pro ($36) supports both IR and 433MHz RF
   - May need to analyze original remote to determine RF frequency
   - RF learning/transmission is more complex

### Command Behavior Unknown

The GitHub repository provides IR timing codes but **does not document what behaviors each button triggers**. You will need to:

1. Experiment with each command
2. Document what Response/Command/Gags modes do
3. Record which buttons trigger which behaviors
4. Create meaningful button names in Home Assistant

### Code Repetition

According to GitHub issue #2, the IR codes may need to be repeated several times with pauses for reliable operation. This can be handled in automation:

**Broadlink:**
```yaml
service: remote.send_command
data:
  device: squawkers
  command: dance
  num_repeats: 3
  delay_secs: 0.5
```

**ESPHome:**
```yaml
button:
  - platform: template
    name: "Squawkers Dance (Reliable)"
    on_press:
      - remote_transmitter.transmit_raw:
          carrier_frequency: 38kHz
          code: [3000, 3000, 1000, 2000, 2000, 1000, 1000, 2000, 2000, 1000, 2000, 1000, 1000, 2000, 2000, 1000, 1000]
          repeat:
            times: 3
            wait_time: 500ms
```

---

## Step-by-Step Implementation Plan

### Phase 1: Confirm IR/RF (REQUIRED)

**Option A: Inspect Original Remote**
1. Carefully open remote control case
2. Look at transmitter chip:
   - Clear LED visible = IR
   - Metal can/antenna = RF
3. Document findings with photos

**Option B: Test with Phone Camera**
1. Point remote at phone camera
2. Press buttons while viewing camera screen
3. If you see purple/white flashes = IR
4. If no flashes = likely RF

**Option C: IR Detector Test**
1. Buy cheap IR receiver module ($1-2)
2. Connect to Arduino/ESP32
3. Run IR decoder sketch
4. Point remote at receiver
5. If codes detected = IR, if not = RF

### Phase 2: Choose and Acquire Hardware

**For Most Users (Recommended):**
- Purchase Broadlink RM4 Mini ($22-26)
- 3-5 day delivery from Amazon
- Ready to use immediately

**For DIY Enthusiasts:**
- Order ESP32 kit and components ($8-15)
- 1-2 weeks delivery from AliExpress (or faster from Amazon)
- Budget 2-4 hours for assembly and setup

**If RF is Confirmed:**
- Purchase Broadlink RM4 Pro ($36) instead
- Supports both IR and 433MHz RF

### Phase 3: Integration with Home Assistant

**Broadlink Setup (30 minutes):**
1. Install Broadlink app on phone
2. Add device to WiFi network
3. Home Assistant auto-discovers device
4. Use Developer Tools to learn commands
5. Test each command with Squawkers
6. Document button behaviors
7. Create automation scripts

**ESP32/ESPHome Setup (2-4 hours):**
1. Assemble hardware on breadboard
2. Test with basic blink sketch
3. Install ESPHome and compile firmware
4. Flash ESP32 via USB
5. Add to Home Assistant
6. Program IR codes from GitHub repo
7. Test and adjust as needed
8. Document button behaviors
9. Create automation scripts

### Phase 4: Create Useful Automations

Once basic control works, create Home Assistant automations:

**Example Ideas:**
- "Squawkers, dance!" voice command via Saga assistant
- Random parrot noises every hour
- Squawk when front door opens
- React to specific events (sunrise, doorbell, etc.)
- Integration with pirate-themed Halloween display
- Tiki bar party mode synchronization

---

## Cost Comparison Summary

| Solution | Hardware Cost | Setup Time | Skill Level | HA Integration |
|----------|--------------|------------|-------------|----------------|
| Broadlink RM4 Mini | $22-26 | 30 min | Beginner | Excellent (native) |
| Broadlink RM4 Pro | $36 | 30 min | Beginner | Excellent (native) |
| ESP32 IR Blaster | $8-15 | 2-4 hours | Intermediate | Excellent (ESPHome) |
| Universal Remote | $15-80 | 1 hour | Beginner | Poor (none) |

**Best Value:** ESP32 solution if you enjoy DIY
**Easiest:** Broadlink RM4 Mini
**Most Versatile:** Broadlink RM4 Pro (handles IR + RF)
**Not Recommended:** Universal learning remotes

---

## Reference Links

### Primary Resources
- **GitHub Repository:** https://github.com/playfultechnology/SquawkersMcGraw
  - Complete IR code timings
  - Hardware documentation
  - Alternative ESP32 controller firmware

### Broadlink Resources
- **Home Assistant Integration:** https://www.home-assistant.io/integrations/broadlink/
- **Setup Guide:** https://www.bazmac.me/blog/using-broadlink-rm4-pro-with-home-assistant
- **Learning IR Codes Tutorial:** https://peyanski.com/broadlink-rm4-pro-with-home-assistant-and-node-red/
- **Broadlink Manager (GUI):** https://community.home-assistant.io/t/broadlink-manager-nicer-way-to-learn-and-send-ir-rf-commands/58770

### ESPHome Resources
- **Remote Transmitter Component:** https://esphome.io/components/remote_transmitter/
- **Remote Receiver Component:** https://esphome.io/components/remote_receiver/
- **Community Guide:** https://community.home-assistant.io/t/faking-an-ir-remote-control-using-esphome/369071
- **IR Blaster Examples:** https://community.home-assistant.io/t/esphome-ir-blaster-example/453159
- **Complete Tutorial:** https://newerest.space/esphome-infrared-control-home-assistant/

### Hardware Purchasing
- **Amazon (fast shipping):**
  - Broadlink RM4 Mini: $25.99
  - ESP32 Dev Boards: $8-12
  - IR LED kits: $5-10

- **AliExpress (cheaper, slower):**
  - Broadlink RM4 Mini: $20-22
  - ESP32 Dev Boards: $3-6
  - Complete IR kits: $5-8

---

## Conclusion and Recommendation

### For Your Saga Assistant Project

Given your existing Home Assistant setup and voice assistant development, I recommend:

**PRIMARY RECOMMENDATION: ESP32 IR Blaster with ESPHome**

**Reasons:**
1. **Fits Your Skill Level:** You're already doing advanced DIY with wakeword training, ESP32 is within your capabilities
2. **Best Integration:** ESPHome integrates seamlessly with your HA setup
3. **Voice Control Ready:** Easy to trigger from Saga assistant
4. **Learning Opportunity:** Aligns with your project's exploratory nature
5. **Cost Effective:** $8-15 total
6. **Expandable:** Can add more IR/RF capabilities later
7. **No Proprietary Apps:** Fully local, open-source

**FALLBACK: Broadlink RM4 Pro**

If the remote turns out to be RF-based, or if you want the quickest path to working control:
- $36 gets you both IR and RF
- Plug-and-play setup
- Reliable, proven hardware
- Can still integrate with Saga assistant

**AVOID:** Universal learning remotes - no HA integration

### Next Immediate Steps

1. **Confirm IR vs RF** using phone camera test (takes 30 seconds)
2. **If IR confirmed:** Order ESP32 components or Broadlink RM4 Mini
3. **If RF confirmed:** Order Broadlink RM4 Pro
4. **While waiting for hardware:** Set up test automation scripts in HA
5. **Document button behaviors** as you discover them

### Integration with Saga Assistant

Once Squawkers is controllable via HA, you can add voice commands to Saga:

```yaml
# Example automation in Home Assistant
automation:
  - alias: "Saga triggers Squawkers dance"
    trigger:
      platform: event
      event_type: saga_command
      event_data:
        command: "squawkers dance"
    action:
      service: remote.send_command
      data:
        device: squawkers
        command: dance
        entity_id: remote.squawkers_blaster
```

This creates a fully local, voice-controlled animatronic parrot integrated with your Home Assistant system!

---

**Research completed:** November 12, 2025
**Status:** Ready for hardware acquisition and implementation
