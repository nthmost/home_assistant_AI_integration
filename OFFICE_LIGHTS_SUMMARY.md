# Office Lights (Broadlink IR) - Integration Complete ✅

## Overview

Successfully integrated Office Lights IR control via Broadlink RM device into the Home Assistant effects library.

## Device Details

- **Entity**: `remote.office_lights`
- **Device Name**: `Office Lights` (used for command learning)
- **Control Method**: Broadlink IR emitter via Home Assistant

## Learned Commands (20 total)

### Colors (16)
- Orange
- Marigold
- Gold
- Yellow
- Seafoam
- Turquoise
- Aquamarine
- Teal
- Lavender
- Cyan
- Fuschia
- Magenta
- Green
- Blue
- Red
- White

### Effects (4)
- Flash
- Strobe
- Fade
- Smooth

### Brightness Controls (2)
- Light+ (increase brightness)
- Light- (decrease brightness)

## Implementation

### Files Created

1. **`light_effects/broadlink_client.py`**
   - `BroadlinkRemote` - Generic Broadlink IR remote wrapper
   - `OfficeLights` - Specific wrapper for Office Lights with all learned commands

2. **`light_effects/demo_office_lights.py`**
   - Full demo showcasing all colors and effects
   - Color cycling functions
   - Effect testing

3. **Documentation**
   - `BROADLINK_LEARNING.md` - How to learn IR codes
   - `BROADLINK_API_SUMMARY.md` - API capabilities and limitations

## Usage Examples

### Python API

```python
from ha_client import HomeAssistantClient
from broadlink_client import OfficeLights

client = HomeAssistantClient(HA_URL, HA_TOKEN)
office = OfficeLights(client)

# Set colors
office.set_color("Red")
office.set_color("Cyan")

# Use effects
office.flash()
office.fade()

# Brightness control
office.brightness_up()
office.brightness_down()

# Color cycle through all colors
office.color_cycle(duration_per_color=1.0)

# Cycle through specific colors
warm_colors = ["Orange", "Marigold", "Gold", "Yellow"]
office.color_cycle(colors=warm_colors, duration_per_color=1.5)
```

### Direct HA API

```python
client.call_service("remote", "send_command", {
    "entity_id": "remote.office_lights",
    "device": "Office Lights",
    "command": ["Red"]
})
```

## How IR Learning Works

1. Go to HA UI: http://homeassistant.local:8123/developer-tools/service
2. Select service: `remote.learn_command`
3. Fill in:
   - **Entity**: `remote.office_lights`
   - **Device ID**: `Office Lights` (must match exactly)
   - **Command**: Button name (e.g., "Green")
   - **Command type**: `ir`
   - **Timeout**: `20` seconds
4. Click "Call Service"
5. Point physical IR remote at Broadlink and press the button within 20 seconds
6. Command is learned and stored

## Integration with Other Lights

The Office Lights can now be synchronized with:
- **Tube Lamp** (Tuya, via HA)
- **RGBIC TV Light Bars** (Govee, via HA)

All three light systems are now controllable via the unified `ha_client` interface.

## Next Steps

- ✅ Office Lights fully integrated
- ⏭️ Create event monitoring system
- ⏭️ Build AI agent framework for condition-based actions
- 🔮 Potential: Multi-light synchronized effects across all 3 systems
