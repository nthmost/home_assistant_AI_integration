# Keypad PIN Code System - Final Setup

## Summary

USB wireless numpad on **nike.local** monitors for PIN codes and calls Home Assistant API to control lights.

- **PIN `123` + Enter** = Turn ON light
- **PIN `321` + Enter** = Turn OFF light (to be implemented)

## The Journey: What Didn't Work

### Attempt 1: Direct Script on Home Assistant OS ❌
**Problem**: Home Assistant OS runs in a container with strict security. Even with `sudo`, couldn't access `/dev/input` devices.

**Tried:**
- Running Python script directly on HA OS host
- Adding user to input group
- Using sudo with various permission combinations

**Result**: `Permission denied` even as root due to container isolation.

---

### Attempt 2: Home Assistant keyboard_remote Integration ❌
**Problem**: The built-in `keyboard_remote` integration exists but couldn't access the device.

**Tried:**
- Configured `keyboard_remote` in `configuration.yaml`
- Set `devices: ["/dev/input:/dev/input:rwm"]`
- Used both symlink path and direct device path

**Result**: Integration loaded but still got permission denied accessing devices.

---

### Attempt 3: Custom Home Assistant Add-on ❌
**Problem**: Even Docker containers with `full_access: true` and `apparmor: false` couldn't access input devices.

**What we built:**
- Complete add-on with Dockerfile
- `config.json` with `full_access: true`, `apparmor: false`, `devices: ["/dev/input"]`
- Python script with evdev
- Deployed to `/addons/local/keypad_pin_monitor/`

**Result**: Add-on installed and started, but still got `Permission denied` accessing `/dev/input/event0`. Home Assistant OS container isolation is VERY strict.

**Files created (still exist but unused):**
```
/addons/local/keypad_pin_monitor/
├── config.json
├── Dockerfile
├── build.json
├── run.sh
├── keypad_monitor.py
├── README.md
└── CHANGELOG.md
```

---

## The Solution: Nike.local as Keypad Bridge ✅

**Key insight**: Use a separate always-on Linux box (nike.local) with direct hardware access to monitor the keypad and call the HA API.

### Why This Works

1. **nike.local** is a regular Linux system with full hardware access
2. The keypad is **physically plugged into nike.local**
3. Python script runs natively (not in container) with proper device permissions
4. Script calls **Home Assistant REST API** over the network
5. No container isolation, no permission issues

### Architecture

```
┌─────────────────────┐
│   nike.local        │
│   (Ubuntu/Linux)    │
│                     │
│  ┌───────────────┐  │
│  │ USB Wireless  │  │
│  │ Receiver      │  │
│  │ (2.4GHz)      │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │       ┌──────────────────┐
│  │ keypad_monitor│  │       │  Home Assistant  │
│  │ Python script │──┼──────▶│  REST API        │
│  │ (systemd)     │  │ HTTP  │  :8123           │
│  └───────────────┘  │       └──────────────────┘
└─────────────────────┘
         ▲
         │ 2.4GHz Wireless
         │
    ┌────┴─────┐
    │ Wireless │
    │ Numpad   │
    └──────────┘
```

---

## Deployment Details

### Hardware Setup

- **Keypad**: Compx 2.4G Wireless Receiver
  - USB dongle plugged into **nike.local**
  - Wireless numpad paired to dongle (had to re-pair using manual)
  - Device path: `/dev/input/by-id/usb-Compx_2.4G_Wireless_Receiver-event-kbd`
  - Also available as: `/dev/input/event9` (may change on reboot)

### Software Components

**On nike.local:**

1. **Script**: `/usr/local/bin/keypad_monitor.py`
   - Python 3.12
   - Uses `evdev` to read keypad events
   - Uses `requests` to call HA API
   - Runs as root (needed for device access)

2. **Systemd Service**: `/etc/systemd/system/keypad-monitor.service`
   - Starts automatically on boot
   - Auto-restarts if it crashes
   - Runs as root

3. **Dependencies** (installed via apt):
   ```bash
   sudo apt install python3-evdev python3-requests
   ```

**On Home Assistant:**
- No special configuration needed
- Just needs the REST API (always enabled)
- Uses long-lived access token for authentication

### Current Configuration

```python
# In /usr/local/bin/keypad_monitor.py
DEVICE_PATH = '/dev/input/by-id/usb-Compx_2.4G_Wireless_Receiver-event-kbd'
PIN_CODE = '123'
TIMEOUT_SECONDS = 10
HA_URL = 'http://homeassistant.local:8123'
HA_TOKEN = 'eyJhbGci...' # Long-lived access token
ENTITY_ID = 'light.rgbic_tv_light_bars'  # Currently Govee TV bars
```

---

## Installation Steps (for reference)

### 1. Install Dependencies on nike.local
```bash
sudo apt update
sudo apt install -y python3-evdev python3-requests
```

### 2. Deploy Script
```bash
# Copy script to nike.local
scp keypad_final.py nike.local:/tmp/

# On nike.local:
sudo mv /tmp/keypad_final.py /usr/local/bin/keypad_monitor.py
sudo chmod +x /usr/local/bin/keypad_monitor.py
```

### 3. Install Systemd Service
```bash
# Copy service file
scp keypad-monitor.service nike.local:/tmp/

# On nike.local:
sudo mv /tmp/keypad-monitor.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/keypad-monitor.service
sudo systemctl daemon-reload
sudo systemctl enable keypad-monitor
sudo systemctl start keypad-monitor
```

### 4. Verify
```bash
# Check service status
sudo systemctl status keypad-monitor

# Watch logs
sudo journalctl -u keypad-monitor -f

# Test: Press 1-2-3-Enter on keypad
```

---

## Management Commands

### Service Control
```bash
# Start service
sudo systemctl start keypad-monitor

# Stop service
sudo systemctl stop keypad-monitor

# Restart service
sudo systemctl restart keypad-monitor

# Check status
sudo systemctl status keypad-monitor

# View logs
sudo journalctl -u keypad-monitor -f

# View recent logs
sudo journalctl -u keypad-monitor -n 50
```

### Updating the Script

1. **Edit the script:**
   ```bash
   sudo nano /usr/local/bin/keypad_monitor.py
   ```

2. **Restart the service:**
   ```bash
   sudo systemctl restart keypad-monitor
   ```

3. **Check it's working:**
   ```bash
   sudo systemctl status keypad-monitor
   sudo journalctl -u keypad-monitor -f
   ```

---

## Troubleshooting

### Keypad Not Responding

**Check if device exists:**
```bash
ls -la /dev/input/by-id/ | grep -i compx
```

**Check if service is running:**
```bash
sudo systemctl status keypad-monitor
```

**Check logs for errors:**
```bash
sudo journalctl -u keypad-monitor -n 50
```

**Common issues:**
1. **Keypad not paired**: Need to re-pair wireless keypad with dongle (check manual)
2. **Dead batteries**: Replace keypad batteries
3. **Wrong device path**: Device number changes on reboot, symlink should work but can check `dmesg`
4. **Script crashed**: Check logs with journalctl

### Testing Keypad Manually

Stop the service and run the script directly to see output:
```bash
sudo systemctl stop keypad-monitor
sudo python3 /usr/local/bin/keypad_monitor.py
# Press keys and watch output
# Ctrl+C to stop
sudo systemctl start keypad-monitor
```

### HA API Not Responding

**Test API manually:**
```bash
curl -X POST "http://homeassistant.local:8123/api/services/light/turn_on" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.rgbic_tv_light_bars"}'
```

**Check HA is reachable:**
```bash
ping homeassistant.local
curl http://homeassistant.local:8123
```

---

## Future Enhancements

### Multiple PIN Codes
- `123` = Turn ON
- `321` = Turn OFF
- `456` = Different device
- `789` = Scene/automation

### Different Actions
- Toggle instead of ON/OFF
- Set brightness levels
- Trigger automations
- Control multiple devices

### Configuration File
Move settings to `/etc/keypad-monitor.conf`:
```ini
[device]
path = /dev/input/by-id/usb-Compx_2.4G_Wireless_Receiver-event-kbd

[homeassistant]
url = http://homeassistant.local:8123
token = eyJhbGci...

[pins]
123_on = light.rgbic_tv_light_bars
321_off = light.rgbic_tv_light_bars
456_on = light.tube_lamp
```

---

## Security Considerations

1. **Long-lived access token**: Stored in plaintext in script
   - Token has full HA access
   - Stored on nike.local which is network-accessible
   - Acceptable for home network, would need vault for production

2. **Running as root**: Required for device access
   - Could create udev rule and run as service user instead
   - Current approach is simpler for home use

3. **No PIN attempt limiting**: Can try unlimited PINs
   - Add rate limiting if needed
   - Add notification on wrong PIN

4. **Physical security**: Anyone with keypad access can control lights
   - This is by design for convenience
   - Not suitable for security-critical applications

---

## Related Files

- Script source: `/tmp/keypad_final.py` (on development machine)
- Service file: `/tmp/keypad-monitor.service` (on development machine)
- Failed add-on: `/addons/local/keypad_pin_monitor/` (on HA)
- This documentation: `docs/setup/keypad_pin_final_setup.md`

---

**Status**: ✅ Working as of 2025-10-24
**Location**: nike.local (always-on deployment box)
**Target**: Home Assistant at homeassistant.local:8123
