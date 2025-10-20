#!/usr/bin/env python3
"""
Test if Broadlink learned any commands
"""

import sys
sys.path.insert(0, '.')

from ha_client import HomeAssistantClient

HA_URL = "http://homeassistant.local:8123"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwMTU0ZTE4MzQ5ZjA0NzhiYWNjNzEzOGI5MjA0Y2ViYyIsImlhdCI6MTc2MDI0Njc0NCwiZXhwIjoyMDc1NjA2NzQ0fQ.gomMUtxThNUPJTUTlz6mflDtRD_HUza8s7pQNLMVQZE"

client = HomeAssistantClient(HA_URL, HA_TOKEN)

print("Testing learned Broadlink commands")
print("=" * 50)

# Common device IDs and command names to try
test_combinations = [
    # (device_id, command)
    ("Office Lights", "Red"),
    ("Office Lights", "red"),
    ("office_lights", "Red"),
    ("office_lights", "red"),
    ("Office Lights", "Light+"),
    ("Office Lights", "LightPlus"),
    ("Office Lights", "Flash"),
    ("Office Lights", "Fade"),
]

for device_id, command in test_combinations:
    print(f"\nTrying: device='{device_id}', command='{command}'")
    try:
        result = client.call_service("remote", "send_command", {
            "entity_id": "remote.office_lights",
            "device": device_id,
            "command": [command]
        })
        print(f"  ✓ SUCCESS! This combination works!")
        print(f"    Response: {result}")
        break
    except Exception as e:
        error_msg = str(e)
        if "KeyError" in error_msg:
            print(f"  ✗ Not found (KeyError)")
        elif "400" in error_msg:
            print(f"  ✗ Bad request")
        elif "500" in error_msg:
            print(f"  ✗ Server error")
        else:
            print(f"  ✗ Error: {e}")
else:
    print("\n" + "=" * 50)
    print("No learned commands found with common names.")
    print("\nDo you remember:")
    print("  1. What 'Device ID' you entered when learning?")
    print("  2. What 'Command' name you entered?")
    print("\nThose exact values need to match when sending commands.")
