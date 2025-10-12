# Learning Broadlink IR Codes into Home Assistant

## The Problem

IR codes stored in the Broadlink iPhone app are **NOT** accessible to Home Assistant. HA needs to learn the codes separately directly from your physical remote.

## Solution: Learn Commands in HA

### Option 1: Use the Python Script (Easiest)

Run the interactive learning script:

```bash
cd /home/nthmost/projects/home_assistant_AI_integration/light_effects
python3 learn_broadlink_codes.py
```

**What it does:**
1. Puts Broadlink into learning mode for each command
2. Gives you 20 seconds to press the button on your physical remote
3. Saves the IR code to Home Assistant
4. Tests one command when done

**You'll need:**
- Your physical IR remote (the one that controls the Office Lights)
- To be near the Broadlink device so it can receive the IR signal

### Option 2: Use HA Developer Tools (Manual)

1. Go to **Home Assistant UI** → **Developer Tools** → **Services**
2. Select service: `remote.learn_command`
3. Fill in:
   ```yaml
   entity_id: remote.office_lights
   command: Red
   timeout: 20
   ```
4. Click **"Call Service"**
5. Within 20 seconds, point your physical remote at the Broadlink and press the Red button
6. Repeat for each button: Light+, Light-, Flash, Fade, Smooth, Red, Green, Blue, etc.

## Where Are Codes Stored?

After learning, HA stores the codes in:
```
/config/broadlink_remote_<mac_address>_codes
```

This file is automatically created and updated by HA.

## Testing Learned Codes

After learning, test with:

```bash
# Use the test script
python3 test_broadlink.py
```

Or manually:
```python
client.call_service("remote", "send_command", {
    "entity_id": "remote.office_lights",
    "command": ["Red"]
})
```

## Commands to Learn

Based on what you mentioned:
- Light+
- Light-
- Flash
- Fade
- Smooth
- Red
- Green
- Blue
- White
- Orange
- Yellow
- Cyan
- Purple
- (any other color buttons on your remote)

## Troubleshooting

**"Timeout" or "No signal received":**
- Make sure you're pressing the button on the **physical IR remote**, not the Broadlink app
- Point the remote directly at the Broadlink device
- Press and hold the button for 1-2 seconds

**"Command already exists":**
- Use `remote.delete_command` first, then re-learn

**"Still getting 500 errors after learning":**
- Restart Home Assistant to reload the codes file
- Check HA logs for specific error messages
