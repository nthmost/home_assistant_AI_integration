#!/usr/bin/env python3
"""
List all learned IR commands for the Squawkers device.

This script attempts to discover what commands have been learned
in the Broadlink remote for the "squawkers" device.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from saga_assistant.ha_client import HomeAssistantClient


def list_learned_commands():
    """
    List commands learned in Home Assistant Broadlink.

    Note: Unfortunately, Home Assistant doesn't expose a direct API
    to list learned commands. They are stored in the Broadlink
    integration's storage files.

    To see your learned commands, you need to:
    1. Check HA Developer Tools > Services > remote.send_command
    2. Look at the "command" dropdown for your device
    3. Or check: /config/.storage/broadlink_remote_*_codes
    """

    load_dotenv()
    client = HomeAssistantClient()

    print("=" * 70)
    print("SQUAWKERS IR COMMANDS - DISCOVERY")
    print("=" * 70)
    print()

    # Get remote state
    try:
        state = client.get_state("remote.office_lights")
        print("✓ Remote found: remote.office_lights")
        print(f"  State: {state['state']}")
        print(f"  Name: {state['attributes'].get('friendly_name', 'N/A')}")
        print()
    except Exception as e:
        print(f"✗ Could not get remote state: {e}")
        print()

    print("YOUR LEARNED COMMANDS:")
    print("-" * 70)
    print()

    # Universal commands
    print("✓ Universal (most reliable):")
    print("  • DANCE")
    print("  • RESET")
    print()

    # Your actual learned commands
    print("✓ Your learned commands:")
    print()
    print("  Response Mode (A-F):")
    for letter in "ABCDEF":
        print(f"    • Response Button {letter}")
    print()
    print("  Command Mode (A-F):")
    for letter in "ABCDEF":
        print(f"    • Command Button {letter}")
    print()
    print("  Plain Buttons (A-F):")
    for letter in "ABCDEF":
        print(f"    • Button {letter}")
    print()
    print("  Gags Mode (A-F):")
    for letter in "ABCDEF":
        print(f"    • Gags {letter}")
    print()

    # Behaviors from manual
    print("Response Mode behaviors (from manual):")
    manual_behaviors = {
        "Response Button A": "Startled squawk",
        "Response Button B": "Laugh",
        "Response Button C": "Laugh hilariously",
        "Response Button D": "Warble",
        "Response Button E": "Say 'Whatever!!'",
        "Response Button F": "Play along"
    }
    for cmd, behavior in manual_behaviors.items():
        print(f"  • {cmd}: {behavior}")
    print()

    print("DISCOVERING YOUR COMMANDS:")
    print("-" * 70)
    print()
    print("Unfortunately, Home Assistant doesn't expose a direct API")
    print("to list learned Broadlink commands.")
    print()
    print("To find your learned commands, you can:")
    print()
    print("1. Open Home Assistant web interface")
    print("2. Go to: Developer Tools > Services")
    print("3. Select service: remote.send_command")
    print("4. Select entity: remote.office_lights")
    print("5. In the 'device' field, enter: squawkers")
    print("6. The 'command' field should show a dropdown of learned commands")
    print()
    print("OR")
    print()
    print("1. SSH into your Home Assistant server")
    print("2. Look at: /config/.storage/broadlink_remote_*_codes")
    print("3. Search for entries with device: 'squawkers'")
    print()
    print("=" * 70)
    print()
    print("USAGE:")
    print()
    print("Option 1: Use the base class with command names:")
    print("  from squawkers import Squawkers")
    print("  squawkers = Squawkers(client)")
    print("  squawkers.command('Response Button A')")
    print("  squawkers.command('Gags B')")
    print()
    print("Option 2: Use the full class with convenience methods:")
    print("  from squawkers.squawkers_full import SquawkersFull")
    print("  squawkers = SquawkersFull(client)")
    print("  squawkers.response_a()  # Response Button A")
    print("  squawkers.gag_b()       # Gags B")
    print()
    print("See MY_COMMANDS.md for complete usage examples.")
    print()


if __name__ == "__main__":
    list_learned_commands()
