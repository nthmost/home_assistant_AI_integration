# USB Wireless Keypad Setup for Home Assistant

## Hardware
- Device: Compx 2.4G Wireless Receiver
- Device Path: `/dev/input/by-id/usb-Compx_2.4G_Wireless_Receiver-event-kbd`

## Setup Instructions

### 1. Add Configuration to Home Assistant

Add the contents of `usb_keypad.yaml` to your Home Assistant configuration. You can either:

**Option A: Include in configuration.yaml**
```yaml
# Add to configuration.yaml
automation: !include_dir_merge_list automations/
linux_event: !include usb_keypad.yaml
```

**Option B: Add directly to configuration.yaml**
Copy the linux_event section from `usb_keypad.yaml` to your main `configuration.yaml` file.

### 2. Set Permissions (if needed)

If Home Assistant doesn't have permission to read the device, you may need to:

```bash
# Add your user to the input group
sudo usermod -a -G input $USER

# Or create a udev rule for Home Assistant
sudo nano /etc/udev/rules.d/99-input.rules
```

Add this line:
```
SUBSYSTEM=="input", GROUP="input", MODE="0660"
```

Then reload:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 3. Restart Home Assistant

Restart Home Assistant to load the new configuration.

### 4. Test the Setup

1. Go to Developer Tools > Events in Home Assistant
2. Listen for event type: `linux_event`
3. Press keys on your numpad
4. You should see events like:
```json
{
  "event_type": "linux_event",
  "data": {
    "device_name": "Wireless Numpad",
    "key_code": 79,
    "key_state": 1
  }
}
```

## Current Configuration

The keypad is currently configured for PIN code entry:

**PIN Code: `123` + `Enter` = Turn ON Tube Lamp**

See `keypad_pin_code.yaml` and `docs/setup/keypad_pin_setup.md` for details on the PIN code system.

## Available Key Codes

All numpad keys are available for custom automations:

| Key | Key Code |
|-----|----------|
| 0 | 82 |
| 1 | 79 |
| 2 | 80 |
| 3 | 81 |
| 4 | 75 |
| 5 | 76 |
| 6 | 77 |
| 7 | 71 |
| 8 | 72 |
| 9 | 73 |
| + | 78 |
| - | 74 |
| Enter | 96 |
| . | 83 |
| / | 98 |
| * | 55 |

## Finding Key Codes

To find the key code for any key:

```bash
# Install evtest if not available
sudo apt install evtest

# Run evtest on your device
sudo evtest /dev/input/by-id/usb-Compx_2.4G_Wireless_Receiver-event-kbd

# Press keys and note the "code" value in the output
```

Or use the Home Assistant Events listener (Developer Tools > Events > linux_event) and press keys to see their codes.

## Customizing Automations

Each automation in `usb_keypad.yaml` follows this pattern:

```yaml
- id: keypad_custom_action
  alias: "Keypad: X = Your Action"
  description: "Description of what this key does"

  trigger:
    - platform: event
      event_type: linux_event
      event_data:
        device_name: Wireless Numpad
        key_code: XX  # Replace with your key code
        key_state: 1  # 1 = pressed, 0 = released

  action:
    - service: your.service
      # Your action here
```

## Troubleshooting

### Device not found
```bash
# Check if device exists
ls -l /dev/input/by-id/usb-Compx*

# List all input devices
ls -l /dev/input/by-id/
```

### No events in Home Assistant
1. Check Home Assistant logs for errors
2. Verify the device path is correct in configuration
3. Check permissions on the device file
4. Make sure the wireless receiver is powered and connected

### Events detected but automations not firing
1. Check that the key_code matches what you see in Developer Tools
2. Verify the device_name matches exactly ("Wireless Numpad")
3. Check automation logs for any errors

## Notes

- The numpad operates wirelessly, so ensure the receiver has good USB connection
- Key state: 1 = key pressed down, 0 = key released, 2 = key held (repeat)
- Use key_state: 1 to trigger on press only (recommended)
- The device path uses `by-id` which is stable across reboots
