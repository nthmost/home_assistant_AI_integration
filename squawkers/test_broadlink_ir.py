#!/usr/bin/env python3
"""
Test if Broadlink is actually transmitting IR at all
We'll test with a known-working Office Lights command first
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from saga_assistant.ha_client import HomeAssistantClient

load_dotenv()
HA_URL = os.getenv("HA_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.getenv("HA_TOKEN")

print("\n" + "="*70)
print("🔍 BROADLINK IR TRANSMISSION TEST")
print("="*70)

print("\nFirst, let's verify Broadlink is working AT ALL...")
print("\nStep 1: Test with a known-working command (Office Lights)")

client = HomeAssistantClient(HA_URL, HA_TOKEN)

# Send a known Office Lights command
print("\nSending 'Red' command to Office Lights...")
try:
    client.call_service(
        "remote",
        "send_command",
        entity_id="remote.office_lights",
        device="Office Lights",
        command=["Red"]
    )
    print("✅ Command sent")
    print("\n👀 Did the office lights turn red?")
    response = input("   (y/n): ").lower()

    if response == 'y':
        print("\n✅ Great! Broadlink IS transmitting IR successfully")
        print("   This means the problem is with the Squawkers codes")
    else:
        print("\n❌ Problem: Broadlink isn't transmitting IR at all")
        print("   Check:")
        print("   - Is Broadlink powered on?")
        print("   - Is it connected to HA?")
        print("   - Are the Office Lights codes actually learned?")
        exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print("\n" + "="*70)
print("Step 2: Physical positioning test for Squawkers")
print("="*70)

print("\nPosition check:")
print("1. Where is Squawkers relative to the Broadlink?")
print("2. Is the IR sensor on Squawkers' CHEST facing the Broadlink?")
print("3. What's the distance? (IR works best under 10-15 feet)")
print("4. Any obstacles between Broadlink and Squawkers?")
print()

input("Press ENTER when Squawkers is optimally positioned...")

print("\n" + "="*70)
print("Step 3: Test if Squawkers is even ON and responsive")
print("="*70)

print("\nManual test:")
print("1. Does Squawkers have batteries?")
print("2. Is there an ON/OFF switch? Is it ON?")
print("3. Try manually triggering Squawkers:")
print("   - Wave your hand in front of it")
print("   - Make a loud noise near it")
print("   - Press any physical buttons")
print()

response = input("Does Squawkers respond to manual triggers? (y/n): ").lower()

if response != 'y':
    print("\n❌ Squawkers isn't responding to anything!")
    print("   Check batteries and power switch")
    exit(1)

print("\n✅ Squawkers is alive and responsive")

print("\n" + "="*70)
print("Step 4: Understanding the IR protocol issue")
print("="*70)

print("\nPossible problems with our codes:")
print("1. Timing conversion math might be wrong")
print("2. GitHub codes might be for a DIFFERENT Squawkers model")
print("3. The IR protocol might need carrier frequency modulation")
print("4. Codes might need to be repeated MORE times")
print()

print("Let's try sending the dance code MANY times in a row...")
print("(GitHub issue mentioned 'gentle repeats with pause')")
print()

# Squawkers dance code
dance_code = "b64:JgAiAFsAWwAeAD0APQAeAB4APQA9AB4APQAeAB4APQA9AB4AHgA="

input("Press ENTER to send dance code 10 times...")

for i in range(10):
    print(f"Attempt {i+1}/10...", end=" ")
    try:
        client.call_service(
            "remote",
            "send_command",
            entity_id="remote.office_lights",
            command=[dance_code]
        )
        print("✅")
        import time
        time.sleep(1)  # 1 second pause between attempts
    except Exception as e:
        print(f"❌ {e}")

print("\n👀 Did Squawkers respond to ANY of those?")
response = input("   (y/n): ").lower()

if response == 'y':
    print("\n🎉 SUCCESS! The codes work, just need more repeats or timing!")
else:
    print("\n❌ Still nothing. The codes might be wrong or for wrong model.")
    print("\nNext steps:")
    print("1. Double-check you have a Hasbro FurReal Squawkers McGraw")
    print("2. Check if it's the same model as the GitHub repo")
    print("3. The conversion math might need adjustment")
    print("4. May need to try the light sensor approach instead")
