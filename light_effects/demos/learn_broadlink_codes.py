#!/usr/bin/env python3
"""
Interactive script to learn Broadlink IR codes into Home Assistant

This will guide you through learning each button's IR code.
You'll need your physical IR remote handy.
"""

import sys
sys.path.insert(0, '.')

from ha_client import HomeAssistantClient
import time

HA_URL = "http://homeassistant.local:8123"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwMTU0ZTE4MzQ5ZjA0NzhiYWNjNzEzOGI5MjA0Y2ViYyIsImlhdCI6MTc2MDI0Njc0NCwiZXhwIjoyMDc1NjA2NzQ0fQ.gomMUtxThNUPJTUTlz6mflDtRD_HUza8s7pQNLMVQZE"

client = HomeAssistantClient(HA_URL, HA_TOKEN)

# Commands you want to learn
COMMANDS = [
    "Light+",
    "Light-",
    "Flash",
    "Fade",
    "Smooth",
    "Red",
    "Green",
    "Blue",
    "White",
    "Orange",
    "Yellow",
    "Cyan",
    "Purple",
]

print("=" * 60)
print("Broadlink IR Code Learning for Office Lights")
print("=" * 60)
print("\nYou'll need:")
print("  1. Your physical IR remote control")
print("  2. To be near the Broadlink device")
print("\nFor each command, you'll have ~20 seconds to press the")
print("corresponding button on your physical remote.\n")

input("Press ENTER when ready to start...")

for cmd in COMMANDS:
    print(f"\n{'='*60}")
    print(f"Learning: {cmd}")
    print(f"{'='*60}")
    print(f"\nStarting learning mode...")

    try:
        # Start learning mode
        result = client.call_service("remote", "learn_command", {
            "entity_id": "remote.office_lights",
            "command": [cmd],
            "timeout": 20
        })

        print(f"✓ Ready! Point remote at Broadlink and press '{cmd}' button NOW!")
        print("  (waiting 20 seconds...)")

        time.sleep(22)  # Wait for learning to complete

        print(f"✓ Code learned for '{cmd}'")

    except Exception as e:
        print(f"✗ Error learning '{cmd}': {e}")
        retry = input(f"  Retry {cmd}? (y/n): ")
        if retry.lower() == 'y':
            continue

    time.sleep(1)

print("\n" + "="*60)
print("Learning complete!")
print("="*60)
print("\nTesting learned codes...")

# Test one command
test_cmd = "Red"
print(f"\nTesting '{test_cmd}' command...")
try:
    client.call_service("remote", "send_command", {
        "entity_id": "remote.office_lights",
        "command": [test_cmd]
    })
    print(f"✓ Test successful! Did the lights respond?")
except Exception as e:
    print(f"✗ Test failed: {e}")
