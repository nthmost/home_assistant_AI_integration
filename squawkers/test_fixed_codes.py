#!/usr/bin/env python3
"""
Test the FIXED Broadlink codes with Squawkers
"""

import os
import sys
import time
from dotenv import load_dotenv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from saga_assistant.ha_client import HomeAssistantClient

load_dotenv()
HA_URL = os.getenv("HA_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.getenv("HA_TOKEN")

# FIXED codes using correct python-broadlink formula
FIXED_CODES = {
    "dance": "JgARAGJiIEFBICBBQSBBICBBQSAg",
    "reset": "JgARAGJiIEFBIEEgIEEgQUEgIEEg",
    "response_a": "JgARAGJiIEEgQSBBIEFBICBBQSAg",
    "response_b": "JgARAGJiIEEgQSBBQSAgQUEgIEEg",
}

print("\n" + "="*70)
print("🦜 TESTING FIXED BROADLINK CODES")
print("="*70)
print("\nThese use the CORRECT python-broadlink encoding formula")
print("Old code: JgAiAFsAWwAeAD0APQAeAB4APQA9AB4APQAeAB4APQA9AB4AHgA=")
print("New code: JgARAGJiIEFBICBBQSBBICBBQSAg")
print("\nMuch shorter = more accurate!\n")

client = HomeAssistantClient(HA_URL, HA_TOKEN)

print("Testing DANCE command...")
print("Sending 5 times with pauses...\n")

dance_code = f"b64:{FIXED_CODES['dance']}"

for i in range(5):
    print(f"Attempt {i+1}/5... ", end="", flush=True)
    try:
        client.call_service(
            "remote",
            "send_command",
            entity_id="remote.office_lights",
            command=[dance_code]
        )
        print("✅ Sent")
        time.sleep(0.8)
    except Exception as e:
        print(f"❌ {e}")

print("\n" + "="*70)
print("👀 DID SQUAWKERS DANCE?")
print("="*70)
response = input("(y/n): ").lower()

if response == 'y':
    print("\n🎉🎉🎉 SUCCESS! THE CODES WORK! 🎉🎉🎉")
    print("\nThe problem was the encoding formula!")
    print("We can now control Squawkers with ALL 20 commands!")
else:
    print("\n😞 Still not working...")
    print("\nPossible remaining issues:")
    print("1. GitHub codes might be for different Squawkers model")
    print("2. Need even MORE repetitions")
    print("3. Carrier frequency modulation issue")
    print("4. Time to try light sensor method instead")
