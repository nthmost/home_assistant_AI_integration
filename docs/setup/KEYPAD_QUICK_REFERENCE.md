# Keypad PIN System - Quick Reference

## Current Setup

**Location**: nike.local (always-on deployment box)
**Target Device**: `light.rgbic_tv_light_bars` (Govee TV Light Bars)

## PIN Codes

- **`123` + Enter** = Turn ON lights 💡
- **`321` + Enter** = Turn OFF lights ⚫

## System Status

```bash
# Check if running
sudo systemctl status keypad-monitor

# Watch live activity
sudo journalctl -u keypad-monitor -f

# Restart if needed
sudo systemctl restart keypad-monitor
```

## Files

- **Script**: `/usr/local/bin/keypad_monitor.py`
- **Service**: `/etc/systemd/system/keypad-monitor.service`
- **Device**: `/dev/input/by-id/usb-Compx_2.4G_Wireless_Receiver-event-kbd`

## Changing Target Device

Edit the script:
```bash
sudo nano /usr/local/bin/keypad_monitor.py
```

Change this line:
```python
ENTITY_ID = 'light.rgbic_tv_light_bars'  # Change to any HA entity
```

Then restart:
```bash
sudo systemctl restart keypad-monitor
```

## Adding More PIN Codes

Edit `/usr/local/bin/keypad_monitor.py` and add more conditions in the `handle_key()` function:

```python
elif sequence == '456':
    print(f"✅ SUCCESS! PIN {sequence} = Turn ON Bedroom Lights")
    call_ha_service('light', 'turn_on', 'light.bedroom_light')
```

See full documentation: `docs/setup/keypad_pin_final_setup.md`
