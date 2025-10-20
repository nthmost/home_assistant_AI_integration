# Fixing Tuya Tube Lamp Connection

## Problem
The Tuya Tube Lamp (`light.tube_lamp`) is returning 500 Internal Server Error when trying to control it via the Home Assistant API.

## Root Cause
Error from Home Assistant logs:
```
Exception: network error:(-9999999) sign invalid
```

This error occurs in the Tuya cloud integration when Home Assistant tries to send commands to the Tuya API. The signature validation is failing.

## Common Causes
1. **Expired API credentials** - Tuya developer account credentials need refreshing
2. **Time synchronization issues** - Server time out of sync with Tuya's servers
3. **Invalid API keys** - Access ID or Access Secret changed or revoked
4. **Account linking broken** - Tuya account needs to be re-linked

## Solution Steps

### Option 1: Reconfigure Tuya Integration (Recommended)
1. Go to Home Assistant UI
2. Navigate to **Settings** → **Devices & Services**
3. Find the **Tuya** integration
4. Click the three dots menu → **Reconfigure**
5. Re-enter your Tuya credentials:
   - Account (Email/Username)
   - Password
   - Country Code
   - Application Type (Smart Life or Tuya Smart)

### Option 2: Remove and Re-add Integration
1. Go to **Settings** → **Devices & Services**
2. Find **Tuya** integration
3. Click three dots → **Delete**
4. Restart Home Assistant
5. Go to **Settings** → **Devices & Services** → **Add Integration**
6. Search for "Tuya" and follow setup wizard

### Option 3: Check Tuya IoT Platform (Advanced)
If you're using the Tuya IoT Platform integration:
1. Log into https://iot.tuya.com
2. Go to your Cloud Project
3. Check if the Access ID/Secret are still valid
4. Verify API permissions are enabled
5. Check if your subscription is active
6. Generate new credentials if needed
7. Update in Home Assistant

### Option 4: Check Time Sync
```bash
# On Home Assistant OS, check time sync
ha os info

# If time is wrong, might need to restart
ha core restart
```

## Verification
After fixing, test the light control:
```bash
curl -X POST "http://homeassistant.local:8123/api/services/light/turn_on" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.tube_lamp"}'
```

## Status
- **Last Error**: 2025-10-12 (when we tried to control it)
- **Last Successful Update**: 2025-02-22 (state last changed)
- **Current State**: Shows "off" but actually is ON (state out of sync)

## Notes
The state being out of sync for ~7 months suggests the Tuya integration has been broken since late February 2025.
