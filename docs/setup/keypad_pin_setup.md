# Keypad PIN Code Setup

## Overview

This setup allows you to use a 3-digit PIN code on your wireless numpad to control the Tube Lamp.

**PIN Code:** `123` + `Enter` = Turn ON Tube Lamp

## Features

- ✅ Tracks digit sequence as you type
- ✅ Validates PIN when Enter is pressed
- ✅ Always turns ON the Tube Lamp (even if already on)
- ✅ Auto-resets after 10 seconds of inactivity
- ✅ Resets on wrong digits (0, 4-9)
- ✅ Resets after successful activation

## Files

- `automations/keypad_helpers.yaml` - Helper entity for storing PIN sequence
- `automations/keypad_pin_code.yaml` - PIN code automation logic

## Installation

### 1. Add Helper Configuration

Add the helper entity to your Home Assistant `configuration.yaml`:

```yaml
# Add to configuration.yaml
input_text: !include automations/keypad_helpers.yaml
```

Or if you already have an `input_text:` section, merge the contents:

```yaml
input_text:
  # ... your existing helpers ...
  keypad_pin_sequence:
    name: Keypad PIN Sequence
    initial: ""
    max: 10
    mode: text
```

### 2. Add Automations

Add the PIN code automations to your configuration. You have two options:

**Option A: Include the file in configuration.yaml**

```yaml
# Add to configuration.yaml
automation: !include_dir_merge_list automations/
```

This will automatically load `keypad_pin_code.yaml` along with other automation files.

**Option B: Manual merge**

Copy the automation content from `keypad_pin_code.yaml` into your existing automation configuration.

### 3. Restart Home Assistant

Restart Home Assistant to load the new configuration:
- Go to Settings → System → Restart
- Or use the CLI: `ha core restart`

### 4. Verify Setup

After restart, check that everything is loaded:

1. **Check Helper Entity:**
   - Go to Settings → Devices & Services → Helpers
   - Look for "Keypad PIN Sequence"
   - It should show an empty text field

2. **Check Automations:**
   - Go to Settings → Automations & Scenes
   - Look for automations starting with "Keypad PIN:"
   - You should see 5 new automations

## Usage

1. **Type the PIN:** Press `1`, then `2`, then `3` on your numpad
2. **Execute:** Press `Enter`
3. **Result:** The Tube Lamp turns ON

### Behavior Notes

- **Wrong digits:** If you press 0, 4, 5, 6, 7, 8, or 9, the sequence resets
- **Timeout:** If you wait more than 10 seconds between presses, the sequence resets
- **Wrong PIN + Enter:** If you press Enter with the wrong sequence, it just resets (no action)
- **Multiple presses:** You can keep pressing 1-2-3-Enter repeatedly to ensure the light is on

## Troubleshooting

### PIN doesn't work

1. **Check Helper State:**
   - Go to Developer Tools → States
   - Search for `input_text.keypad_pin_sequence`
   - Press digits 1-2-3 and watch the value change to "123"

2. **Check Automation Logs:**
   - Go to Settings → Automations → Click on "Keypad PIN: Enter = Validate & Turn ON Tube Lamp"
   - Click the three dots menu → Traces
   - Look for recent executions and check conditions

3. **Check Linux Events:**
   - Go to Developer Tools → Events
   - Listen for `linux_event`
   - Press keys and verify events are firing

### Helper not found

- Make sure you restarted Home Assistant after adding the helper configuration
- Check the logs for YAML errors: Settings → System → Logs

### Automations not firing

- Verify the device_name in events matches "Wireless Numpad" exactly
- Check that key codes match (use Developer Tools → Events to verify)

## Customization

### Change PIN Code

Edit `automations/keypad_pin_code.yaml`:

```yaml
# In the "Enter Key: Validate PIN" automation
- conditions:
    - condition: template
      value_template: "{{ states('input_text.keypad_pin_sequence') == '456' }}"  # Change to your PIN
```

### Change Timeout Duration

Edit `automations/keypad_pin_code.yaml`:

```yaml
# In the "Timeout: Reset sequence" automation
trigger:
  - platform: state
    entity_id: input_text.keypad_pin_sequence
    to: ~
    for:
      seconds: 15  # Change from 10 to your preferred timeout
```

### Change Light Action

Edit the action in the Enter validation automation:

```yaml
# Turn OFF instead of ON
- service: light.turn_off
  target:
    entity_id: light.tube_lamp

# Or toggle
- service: light.toggle
  target:
    entity_id: light.tube_lamp

# Or set specific brightness
- service: light.turn_on
  target:
    entity_id: light.tube_lamp
  data:
    brightness: 128
```

### Add Multiple PIN Codes

Add more conditions to the Enter automation:

```yaml
action:
  - choose:
      # PIN 123: Turn ON Tube Lamp
      - conditions:
          - condition: template
            value_template: "{{ states('input_text.keypad_pin_sequence') == '123' }}"
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.tube_lamp
          - service: input_text.set_value
            target:
              entity_id: input_text.keypad_pin_sequence
            data:
              value: ""

      # PIN 456: Turn OFF all lights
      - conditions:
          - condition: template
            value_template: "{{ states('input_text.keypad_pin_sequence') == '456' }}"
        sequence:
          - service: light.turn_off
            target:
              entity_id: all
          - service: input_text.set_value
            target:
              entity_id: input_text.keypad_pin_sequence
            data:
              value: ""

    # Wrong PIN: just reset
    default:
      - service: input_text.set_value
        target:
          entity_id: input_text.keypad_pin_sequence
        data:
          value: ""
```

## Key Codes Reference

| Key | Code | Used in PIN |
|-----|------|-------------|
| 0 | 82 | ❌ (resets) |
| 1 | 79 | ✅ |
| 2 | 80 | ✅ |
| 3 | 81 | ✅ |
| 4 | 75 | ❌ (resets) |
| 5 | 76 | ❌ (resets) |
| 6 | 77 | ❌ (resets) |
| 7 | 71 | ❌ (resets) |
| 8 | 72 | ❌ (resets) |
| 9 | 73 | ❌ (resets) |
| Enter | 96 | ✅ (validates) |

## Conflicts with Existing Automations

⚠️ **Important:** The original `usb_keypad.yaml` automations for keys 1, 2, and 3 will now **append digits to the PIN sequence** instead of directly controlling lights.

If you want to keep direct control AND have PIN codes, you have these options:

### Option 1: Use Different Keys for Direct Control
- Move direct toggle actions to keys 4-9
- Reserve 1-3 exclusively for PIN codes

### Option 2: Disable Conflicting Automations
- Disable the original automations for keys 1, 2, 3 in `usb_keypad.yaml`
- Use only PIN codes for control

### Option 3: Require Modifier Key
- Use a key combo like `* + 1 + 2 + 3 + Enter` for PIN mode
- Keep single key presses for direct control
- (Requires more complex automation logic)

## Security Notes

- 🔓 This is a convenience feature, not a security system
- PIN code is stored in plain text in configuration files
- Anyone with physical access to the keypad can try PIN codes
- There is no lockout mechanism after wrong attempts
- Suitable for basic access control in trusted environments
