# How to Check Your Learned Broadlink Commands

Home Assistant stores learned Broadlink IR commands in a JSON file, but doesn't expose them via API.

## Where Commands Are Stored

File location: `/config/.storage/broadlink_remote_MACADDRESS_codes`

Where `MACADDRESS` is your Broadlink device's MAC address (e.g., `34ea34abcdef12_codes`)

## Method 1: Home Assistant Web UI (Easiest)

**Best for: Quick verification**

1. Open Home Assistant web interface
2. Go to **Developer Tools** > **Services**
3. Select service: `remote.send_command`
4. Select entity: `remote.office_lights`
5. In "device" field, type: `squawkers`
6. Click in the "command" field
7. **A dropdown appears showing all learned commands!**

This is the quickest way to see what you have.

## Method 2: SSH to Home Assistant

**Best for: Copying command names, scripting**

### Quick Method (using provided script)

```bash
cd /path/to/home_assistant_AI_integration
./squawkers/fetch_ha_codes.sh
```

This will:
- SSH to your HA server
- Find the Broadlink storage file
- Extract 'squawkers' commands
- Pretty-print with `jq` if available

### Manual Method

```bash
# SSH to Home Assistant
ssh root@homeassistant.local

# Find the Broadlink storage file
ls /config/.storage/broadlink_remote_*_codes

# View the entire file (with jq for formatting)
cat /config/.storage/broadlink_remote_*_codes | jq '.'

# Or search for just 'squawkers' device
cat /config/.storage/broadlink_remote_*_codes | jq '.data' | grep -A 100 "squawkers"
```

### File Structure

The file is JSON structured like:
```json
{
  "version": 1,
  "key": "broadlink_remote_34ea34abcdef12_codes",
  "data": {
    "squawkers": {
      "DANCE": "JgBQAA...",
      "RESET": "JgBQAB...",
      "Response Button A": "JgBQAC...",
      "Response Button B": "JgBQAD...",
      ...
    },
    "Office Lights": {
      "Red": "JgBQAE...",
      ...
    }
  }
}
```

The keys under `"squawkers"` are your command names.

## Method 3: File Editor Add-on

**Best for: GUI access on Home Assistant**

1. Install **File Editor** add-on in Home Assistant
2. Open File Editor
3. Navigate to `/.storage/`
4. Find file: `broadlink_remote_*_codes`
5. Open the file
6. Search for `"squawkers"`
7. You'll see all command names listed

## Method 4: Using Our Helper Scripts

### Check Locally (if running on HA server)

```bash
pipenv run python squawkers/check_ha_codes.py
```

This searches common HA config locations for the storage file.

### List Known Commands

```bash
pipenv run python squawkers/list_commands.py
```

Shows the commands we expect you to have based on your naming convention.

## What You'll Find

Based on your setup, you should see 26 commands:

```json
{
  "squawkers": {
    "DANCE": "...",
    "RESET": "...",
    "Response Button A": "...",
    "Response Button B": "...",
    "Response Button C": "...",
    "Response Button D": "...",
    "Response Button E": "...",
    "Response Button F": "...",
    "Command Button A": "...",
    "Command Button B": "...",
    "Command Button C": "...",
    "Command Button D": "...",
    "Command Button E": "...",
    "Command Button F": "...",
    "Button A": "...",
    "Button B": "...",
    "Button C": "...",
    "Button D": "...",
    "Button E": "...",
    "Button F": "...",
    "Gags A": "...",
    "Gags B": "...",
    "Gags C": "...",
    "Gags D": "...",
    "Gags E": "...",
    "Gags F": "..."
  }
}
```

The values (e.g., `"JgBQAA..."`) are base64-encoded Broadlink IR signal data.

## Troubleshooting

### Can't SSH to Home Assistant?

**Option A: Enable SSH**
1. Install "SSH & Web Terminal" or "Terminal & SSH" add-on
2. Configure with your SSH key or password
3. Try again

**Option B: Use the Web UI method**
The UI dropdown is the easiest way to see your commands!

### File not found?

The file only exists if you've learned commands using the Broadlink integration.

Check:
```bash
ssh root@homeassistant.local
ls -la /config/.storage/broadlink_*
```

### Wrong device name?

Make sure you're searching for the exact device name you used when learning commands.

If you're not sure, list all devices:
```bash
cat /config/.storage/broadlink_remote_*_codes | jq '.data | keys'
```

## Using Command Names in Code

Once you know the exact command names, use them:

```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = Squawkers(client)

# Use exact names from storage file
squawkers.command("Response Button A")
squawkers.command("Gags B")
squawkers.command("DANCE")
```

Or use the convenience class:

```python
from squawkers.squawkers_full import SquawkersFull

squawkers = SquawkersFull(client)

squawkers.response_a()  # Maps to "Response Button A"
squawkers.gag_b()       # Maps to "Gags B"
squawkers.dance()       # Maps to "DANCE"
```

## Summary

**Recommended approach:**
1. Use **Web UI** (Developer Tools > Services) to see command list
2. Write down the names you see
3. Use those exact names in your code
4. Or use `SquawkersFull` convenience methods

**For automation:**
- Use `fetch_ha_codes.sh` to get a programmatic list
- Parse the JSON to generate code or configs
