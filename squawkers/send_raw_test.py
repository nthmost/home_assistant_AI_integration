#!/usr/bin/env python3
"""
Test sending raw Broadlink base64 codes to Squawkers
NO LEARNING REQUIRED!
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from saga_assistant.ha_client import HomeAssistantClient

# Load environment
load_dotenv()
HA_URL = os.getenv("HA_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.getenv("HA_TOKEN")

# Base64 codes (from convert_to_broadlink.py)
CODES = {
    "dance": "JgAiAFsAWwAeAD0APQAeAB4APQA9AB4APQAeAB4APQA9AB4AHgA=",
    "reset": "JgAiAFsAWwAeAD0APQAeAD0AHgAeAD0AHgA9AD0AHgAeAD0AHgA=",
    "response_a": "JgAiAFsAWwAeAD0AHgA9AB4APQAeAD0APQAeAB4APQA9AB4AHgA=",
    "response_b": "JgAiAFsAWwAeAD0AHgA9AB4APQA9AB4AHgA9AD0AHgAeAD0AHgA=",
}

def send_raw_code(client, code_b64, repeat=3):
    """
    Send raw base64 code to Broadlink

    Args:
        client: HomeAssistantClient
        code_b64: Base64 encoded Broadlink code
        repeat: Number of times to send (GitHub suggests multiple sends)
    """
    import time

    # Broadlink needs "b64:" prefix for raw codes
    command = f"b64:{code_b64}"

    for i in range(repeat):
        print(f"  Attempt {i+1}/{repeat}...", end=" ")
        try:
            # For base64 codes, we send directly to the entity
            # entity_id is a positional arg, command goes in service_data
            result = client.call_service(
                "remote",
                "send_command",
                entity_id="remote.office_lights",
                command=[command]  # Pass as keyword arg
            )
            print("✅ Sent")
            time.sleep(0.5)  # Gentle pause between sends
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    return True


def main():
    if not HA_TOKEN:
        print("❌ Error: HA_TOKEN not found in .env")
        return

    print("\n" + "="*70)
    print("🦜 SQUAWKERS MCGRAW - RAW CODE TEST")
    print("="*70)
    print(f"\nHome Assistant: {HA_URL}")
    print("Broadlink: remote.office_lights")
    print("\n⚠️  Make sure Squawkers is:")
    print("   - Powered on")
    print("   - In line of sight of Office Broadlink")
    print("   - IR sensor on chest is visible")
    print()

    client = HomeAssistantClient(HA_URL, HA_TOKEN)

    # Test menu
    while True:
        print("\n" + "="*70)
        print("Which command do you want to test?")
        print("="*70)
        print("1. Dance (should make Squawkers dance)")
        print("2. Reset (should stop/reset)")
        print("3. Response Mode - Button A (unknown behavior)")
        print("4. Response Mode - Button B (unknown behavior)")
        print("5. Exit")
        print()

        choice = input("Choose (1-5): ").strip()

        if choice == "1":
            print("\n🔊 Sending DANCE command...")
            success = send_raw_code(client, CODES["dance"])
            if success:
                print("\n📝 Did Squawkers dance? (observe and note)")
        elif choice == "2":
            print("\n🔊 Sending RESET command...")
            success = send_raw_code(client, CODES["reset"])
            if success:
                print("\n📝 Did Squawkers stop/reset? (observe and note)")
        elif choice == "3":
            print("\n🔊 Sending RESPONSE A command...")
            success = send_raw_code(client, CODES["response_a"])
            if success:
                print("\n📝 What did Squawkers do? (observe and note)")
        elif choice == "4":
            print("\n🔊 Sending RESPONSE B command...")
            success = send_raw_code(client, CODES["response_b"])
            if success:
                print("\n📝 What did Squawkers do? (observe and note)")
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()
