#!/usr/bin/env python3
"""
Test Broadlink IR control
"""

import sys
sys.path.insert(0, '.')

from ha_client import HomeAssistantClient
import time

HA_URL = "http://homeassistant.local:8123"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwMTU0ZTE4MzQ5ZjA0NzhiYWNjNzEzOGI5MjA0Y2ViYyIsImlhdCI6MTc2MDI0Njc0NCwiZXhwIjoyMDc1NjA2NzQ0fQ.gomMUtxThNUPJTUTlz6mflDtRD_HUza8s7pQNLMVQZE"

client = HomeAssistantClient(HA_URL, HA_TOKEN)

print("Testing Broadlink IR Office Lights")
print("=" * 50)

# Test with different command formats
commands_to_test = [
    "Light+",
    "Light-",
    "Red",
    "Flash",
]

for cmd in commands_to_test:
    print(f"\nTrying command: {cmd}")
    try:
        # Try without device parameter
        result = client.call_service("remote", "send_command", {
            "entity_id": "remote.office_lights",
            "command": cmd  # Send as string, not list
        })
        print(f"  ✓ Success: {result}")
        time.sleep(1)
    except Exception as e:
        print(f"  ✗ Error: {e}")

        # Try with list format
        try:
            result = client.call_service("remote", "send_command", {
                "entity_id": "remote.office_lights",
                "command": [cmd]
            })
            print(f"  ✓ Success (list format): {result}")
            time.sleep(1)
        except Exception as e2:
            print(f"  ✗ Error (list format): {e2}")

print("\n" + "=" * 50)
print("Test complete")
