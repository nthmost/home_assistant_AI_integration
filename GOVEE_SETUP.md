# Adding Govee Light Bars to Home Assistant

## Current Status
- Light Bars work via Alexa ✓
- Not yet visible in Home Assistant ✗

## Integration Options

### Option 1: Govee LAN Control (Recommended - Local, Fast)

**Best for:** Direct local network control without cloud dependency

**Steps:**
1. In Home Assistant:
   - Go to **Settings** → **Devices & Services**
   - Click **Add Integration**
   - Search for **"Govee"**
   - If devices support LAN mode, they should auto-discover

2. If not auto-discovered, you may need to enable LAN control in the Govee app:
   - Open Govee Home app
   - Select your Light Bars
   - Go to device settings
   - Look for "LAN Control" or "Local Control" option
   - Enable it

3. Once enabled, HA should detect them automatically

**Pros:**
- Fast, local control
- No cloud dependency
- Works when internet is down

**Cons:**
- Not all Govee models support LAN mode

---

### Option 2: Govee Cloud API Integration

**Best for:** When LAN control isn't available

**Steps:**
1. Get Govee API Key:
   - Open Govee Home app
   - Go to Account → About Us → Apply for API Key
   - You'll receive the key via email

2. In Home Assistant:
   - Go to **Settings** → **Devices & Services**
   - Click **Add Integration**
   - Search for **"Govee"**
   - Enter your API key when prompted

**Pros:**
- Works with all Govee devices
- Official support

**Cons:**
- Requires internet
- May have rate limits
- Slower than LAN

---

### Option 3: Via Alexa Media Player

**Best for:** Quick solution if you already have Alexa integration

**Steps:**
1. Install Alexa Media Player custom integration (if not installed):
   - Go to HACS (Home Assistant Community Store)
   - Search for "Alexa Media Player"
   - Install

2. Configure:
   - Go to **Settings** → **Devices & Services**
   - Add "Alexa Media Player" integration
   - Sign in with Amazon account

3. Your Govee lights should appear as Alexa entities

**Pros:**
- Quick if you have Alexa already
- Leverages existing setup

**Cons:**
- Indirect control (goes through Amazon)
- Slower response
- Requires internet

---

### Option 4: Bluetooth (If supported)

Some Govee devices support Bluetooth.

**Steps:**
1. Ensure HA has Bluetooth enabled
2. Check **Settings** → **Devices & Services** → **Bluetooth**
3. Put lights in pairing mode
4. They should appear in Bluetooth devices

**Pros:**
- Direct local control

**Cons:**
- Limited range
- May not support all features

---

## Recommended Approach

1. **First try:** Option 1 (LAN Control) - Enable in Govee app, then auto-discover in HA
2. **If that fails:** Check your specific Light Bars model to see what protocols it supports
3. **Quick fallback:** Option 2 (Cloud API) - Always works

## Next Steps

1. Check which model of Govee Light Bars you have
2. Enable LAN control in Govee app (if available)
3. Try auto-discovery in HA
4. If needed, get API key and use cloud integration

---

## Troubleshooting

**Device not discovered:**
- Ensure device and HA are on same network
- Check if device supports the integration method
- Restart HA after enabling LAN control in app

**Can't find Govee integration in HA:**
- May need to install HACS first
- Or use the Govee Cloud API integration (built-in to newer HA versions)

**Lights control slowly:**
- LAN control is fastest
- Cloud/Alexa have inherent delays
