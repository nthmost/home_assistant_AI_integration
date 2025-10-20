# What You Can Do With Broadlink via Home Assistant API

## Current Situation

You have:
- **Entity**: `remote.office_lights`
- **Status**: On
- **Supported Features**: 3 (turn on/off + send command)

## Available API Services

### 1. **remote.send_command** ✓
Sends IR codes to control devices.

**Problem**: This requires IR codes to be stored in Home Assistant first. The codes in your iPhone Broadlink app are NOT accessible to HA.

**What we tried**: Various command names failed because no codes are stored in HA yet.

### 2. **remote.learn_command** ✗
Would normally let you teach HA IR codes.

**Problem**: Your specific remote entity doesn't support this feature (needs `supported_features: 8`, but yours is `3`).

### 3. **remote.turn_on / turn_off** ✓
Turns the Broadlink device itself on/off (not the lights).

## Why Commands Are Failing

**The IR codes from your iPhone Broadlink app are stored in the Broadlink cloud, NOT in Home Assistant.**

HA needs its own copy of the IR codes to send them. There are two ways to get codes into HA:

### Option A: Learn via HA UI (Recommended)
Since the API doesn't support learning, use the HA web interface:

1. Go to http://homeassistant.local:8123
2. **Settings** → **Devices & Services** → Find Broadlink device
3. Look for "Learn Command" or "Configure" button
4. Follow prompts to learn each IR code from your physical remote

### Option B: Manual Code Entry
If you can extract the raw IR codes from the Broadlink app (advanced), you could:
1. Find the codes file: `/config/broadlink_remote_<mac>_codes`
2. Manually add codes in the format Broadlink uses
3. Restart HA

### Option C: Use Broadlink Directly (Not via HA)
You could control the Broadlink device directly using its own API, bypassing HA entirely. But this defeats the purpose of integration.

## What We Can Do Next

**Immediate options:**

1. **Learn codes via HA UI** - Use your physical IR remote to teach HA each button
   - Go to HA web interface
   - Find Broadlink device settings
   - Use the learn command feature in the UI

2. **Use a different integration** - If you have the raw IR codes, we could:
   - Set up a direct Broadlink API client (similar to how we did with Govee)
   - Control via Broadlink cloud API instead of local IR

3. **Wait for codes** - Once codes are in HA (via method 1), then:
   ```python
   client.call_service("remote", "send_command", {
       "entity_id": "remote.office_lights",
       "command": ["Red"]  # Will work once learned
   })
   ```

## Bottom Line

**Via API alone**: Can't learn codes (feature not supported)
**Via HA UI**: Can learn codes using web interface
**After learning**: API will work perfectly for sending commands

The blockage is that the learning feature must be done through the HA UI, not the REST API, for your specific Broadlink setup.
