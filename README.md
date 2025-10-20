# Home Assistant AI Integration

A personal Home Assistant project featuring programmable light effects, hardware integrations, and smart home automations. This repository contains Python libraries, automation configurations, and documentation for a multi-device smart home setup.

## What's Inside

This project combines several components:

1. **Light Effects Library** - Python library for creating dynamic, programmable light effects
2. **Hardware Integrations** - Broadlink IR remotes, Govee lights, USB keypad control
3. **Automations** - Wake-up lights, keypad shortcuts, and automated lighting scenes
4. **Documentation** - Setup guides, troubleshooting docs, and device status tracking

## Quick Start

### Running Light Effects

```python
from light_effects import HomeAssistantClient, AdvancedEffects

# Initialize
client = HomeAssistantClient('http://homeassistant.local:8123', 'YOUR_TOKEN')
effects = AdvancedEffects(client, 'light.tube_lamp')

# Run effects
effects.surge('red', duration=5.0)      # Emergency alert
effects.cascade(duration=20.0)           # Rainbow cascade
effects.ocean_swim(duration=30.0)        # Blue/cyan flow
```

See [light_effects/README.md](light_effects/README.md) for full documentation.

### Testing Automations

```bash
# Test the wake-up light sequence (accelerated)
python light_effects/demos/test_wakeup.py

# Demo various light effects
python light_effects/demos/demo_effects.py

# Test office lights (Broadlink IR)
python light_effects/demos/demo_office_lights.py
```

## Repository Structure

```
home_assistant_AI_integration/
├── README.md                          # This file
├── docs/                              # Documentation
│   ├── setup/                         # Setup & configuration guides
│   │   ├── govee_setup.md            # Govee light integration
│   │   ├── broadlink_setup.md        # Broadlink IR remote setup
│   │   ├── broadlink_api_summary.md  # Broadlink API reference
│   │   ├── keypad_setup.md           # USB wireless keypad config
│   │   ├── tuya_troubleshooting.md   # Fixing Tuya integration issues
│   │   └── office_lights_summary.md  # Office lights (IR) setup
│   ├── shopping/                      # Planning & shopping guides
│   │   └── zigbee_shopping_guide.md  # AliExpress Zigbee sensor guide
│   └── device_status.md               # Current device inventory & status
│
├── automations/                       # Home Assistant automations
│   ├── wake_up_lights.yaml           # Gradual sunrise wake-up sequence
│   └── usb_keypad.yaml               # Numpad shortcuts for lights
│
├── light_effects/                     # Python library for light effects
│   ├── README.md                     # Full library documentation
│   ├── __init__.py
│   ├── ha_client.py                  # Home Assistant API wrapper
│   ├── advanced_effects.py           # Extended effects (surge, cascade, etc)
│   ├── broadlink_client.py           # Broadlink IR remote client
│   ├── govee_client.py               # Govee API client
│   └── demos/                        # Demo & test scripts
│       ├── demo_effects.py           # Basic effects demo
│       ├── demo_office_lights.py     # Broadlink IR demo
│       ├── test_wakeup.py            # Test wake-up sequence
│       ├── test_broadlink.py         # Test Broadlink connection
│       ├── test_broadlink_learned.py # Test learned IR codes
│       └── learn_broadlink_codes.py  # Learn IR codes from remotes
│
└── scripts/                           # Utility scripts
    └── zigbee_sensor_finder.py       # Find Zigbee sensors by type
```

## Hardware Setup

### Current Devices

**Working:**
- TP-Link Power Strip (5 switches)
- Tube Lamp (Zigbee - needs Tuya reconfiguration)
- Govee RGBIC TV Light Bars
- Office Lights (via Broadlink IR)
- Brother Printer with ink monitoring
- USB Wireless Keypad for shortcuts
- Sonoff Zigbee 3.0 USB Dongle

**Needs Attention:**
- 3x Smart Candelabra Bulbs (Tuya integration broken)
- Third Reality Motion Sensor (battery dead)
- RPi Power sensor (offline)

See [docs/device_status.md](docs/device_status.md) for full device inventory.

### Integration Guides

- **Govee Lights**: [docs/setup/govee_setup.md](docs/setup/govee_setup.md)
- **Broadlink IR Remote**: [docs/setup/broadlink_setup.md](docs/setup/broadlink_setup.md)
- **USB Keypad**: [docs/setup/keypad_setup.md](docs/setup/keypad_setup.md)
- **Tuya Issues**: [docs/setup/tuya_troubleshooting.md](docs/setup/tuya_troubleshooting.md)

## Automations

### Wake-Up Lights

Gradual sunrise simulation across 3 lighting systems:
- Starts at 5% warm orange at sunrise
- Gradually brightens to 80% daylight over 2 hours
- Controls Tube Lamp, Govee Bars, and Office Lights simultaneously

Config: [automations/wake_up_lights.yaml](automations/wake_up_lights.yaml)

### USB Keypad Control

Physical numpad shortcuts for instant light control:
- **0**: All lights off
- **1-3**: Toggle individual light zones
- **+/-**: Brightness up/down
- **Enter**: Trigger sunrise sequence

Config: [automations/usb_keypad.yaml](automations/usb_keypad.yaml)

## Light Effects Library

The `light_effects` Python library provides:

### Basic Effects
- `smooth_transition()` - Smooth color blends
- `rainbow_cycle()` - Rainbow rotation
- `pulse()` - Breathing effect
- `gradient_flow()` - Flow through color palette
- `strobe()` - Rapid flashing

### Advanced Effects
- `surge()` - Intense energy surge with emotional color mapping
- `cascade()` - Rapid rainbow cascade
- `ocean_swim()` - Blue/cyan flowing theme
- `fire_swim()` - Red/orange/yellow theme
- `aurora()` - Green/purple northern lights theme

Full documentation: [light_effects/README.md](light_effects/README.md)

## Scripts & Utilities

### Zigbee Sensor Finder
```bash
python scripts/zigbee_sensor_finder.py
```
Queries Home Assistant for Zigbee sensors and groups them by type (motion, temperature, door/window, etc).

### Learn IR Codes
```bash
python light_effects/demos/learn_broadlink_codes.py
```
Interactive script to learn IR codes from existing remotes using Broadlink devices.

## Development

### Requirements

```bash
pip install requests python-broadlink
```

### Configuration

Most scripts expect:
- Home Assistant at `http://homeassistant.local:8123`
- Long-lived access token (see HA Profile settings)
- Broadlink device on local network (for IR features)

### Testing

Run demo scripts to verify setup:
```bash
# Test all basic light effects
python light_effects/demos/demo_effects.py

# Test wake-up sequence (accelerated)
python light_effects/demos/test_wakeup.py
```

## Project Goals

This project explores:
- **Programmable IoT** - Treating lights as programmable display devices
- **Physical Interfaces** - USB keypad as tactile control interface
- **Wake-Up Automation** - Natural circadian-aware lighting
- **Multi-Protocol Integration** - Zigbee, WiFi, IR working together
- **AI Integration** - Claude conversation agent for natural language control

## Future Plans

- Add temperature/humidity sensors (see [docs/shopping/zigbee_shopping_guide.md](docs/shopping/zigbee_shopping_guide.md))
- Expand motion sensor coverage
- Fix Tuya integration for unavailable bulbs
- Create more themed light effect sequences
- Integrate door/window sensors for security automations

## Notes

- All automations are tested with Home Assistant 2024.x
- IR codes are specific to the remotes used - you'll need to learn your own
- Token shown in test scripts should be replaced with your own

## License

Personal project - use at your own risk!
