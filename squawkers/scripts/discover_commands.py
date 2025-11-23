#!/usr/bin/env python3
"""
Discover all learned IR commands for Squawkers from Home Assistant.

This script automatically fetches the actual learned commands from
the Broadlink storage file via SSH and displays them.
"""

import json
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def fetch_broadlink_codes(ha_host="homeassistant.local"):
    """
    Fetch Broadlink codes from Home Assistant via SSH.

    Args:
        ha_host: Home Assistant hostname

    Returns:
        dict: Parsed JSON data from storage file, or None if failed
    """
    print(f"🔍 Connecting to {ha_host}...")

    try:
        # SSH to HA and get the codes
        cmd = [
            "ssh",
            f"root@{ha_host}",
            "cat /config/.storage/broadlink_remote_*_codes"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print(f"❌ SSH command failed: {result.stderr}")
            return None

        # Parse JSON
        data = json.loads(result.stdout)
        print("✓ Successfully fetched Broadlink codes")
        return data

    except subprocess.TimeoutExpired:
        print("❌ SSH connection timed out")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def extract_squawkers_commands(data):
    """
    Extract command names for 'squawkers' device.

    Args:
        data: Parsed JSON from storage file

    Returns:
        list: Command names, or None if not found
    """
    if not data or 'data' not in data:
        return None

    commands_data = data['data']

    # Look for squawkers device
    if 'squawkers' in commands_data:
        squawkers_data = commands_data['squawkers']
        if isinstance(squawkers_data, dict):
            return sorted(squawkers_data.keys())
        elif isinstance(squawkers_data, list):
            return sorted(squawkers_data)

    return None


def categorize_commands(commands):
    """
    Categorize commands by type.

    Args:
        commands: List of command names

    Returns:
        dict: Commands organized by category
    """
    categories = {
        'universal': [],
        'response': [],
        'command': [],
        'button': [],
        'gags': [],
        'other': []
    }

    for cmd in commands:
        cmd_lower = cmd.lower()

        if cmd in ['DANCE', 'RESET']:
            categories['universal'].append(cmd)
        elif cmd.startswith('Response Button '):
            categories['response'].append(cmd)
        elif cmd.startswith('Command Button '):
            categories['command'].append(cmd)
        elif cmd.startswith('Button '):
            categories['button'].append(cmd)
        elif cmd.startswith('Gags '):
            categories['gags'].append(cmd)
        else:
            categories['other'].append(cmd)

    return categories


def show_commands(commands):
    """Display commands in organized format"""

    print("\n" + "=" * 70)
    print("DISCOVERED SQUAWKERS COMMANDS")
    print("=" * 70)
    print()

    categories = categorize_commands(commands)

    # Universal
    if categories['universal']:
        print("✓ Universal Commands (most reliable):")
        for cmd in categories['universal']:
            print(f"  • {cmd}")
        print()

    # Response mode
    if categories['response']:
        print("✓ Response Mode (A-F):")
        for cmd in categories['response']:
            # Extract letter and add behavior if known
            letter = cmd.split()[-1] if ' ' in cmd else ''
            behaviors = {
                'A': 'Startled squawk',
                'B': 'Laugh',
                'C': 'Laugh hilariously',
                'D': 'Warble',
                'E': 'Say "Whatever!!"',
                'F': 'Play along'
            }
            behavior = f" - {behaviors.get(letter, '')}" if letter in behaviors else ""
            print(f"  • {cmd}{behavior}")
        print()

    # Command mode
    if categories['command']:
        print("✓ Command Mode (A-F):")
        for cmd in categories['command']:
            print(f"  • {cmd}")
        print()

    # Plain buttons
    if categories['button']:
        print("✓ Plain Buttons (A-F):")
        for cmd in categories['button']:
            print(f"  • {cmd}")
        print()

    # Gags mode
    if categories['gags']:
        print("✓ Gags Mode (A-F):")
        for cmd in categories['gags']:
            print(f"  • {cmd}")
        print()

    # Other
    if categories['other']:
        print("✓ Other Commands:")
        for cmd in categories['other']:
            print(f"  • {cmd}")
        print()

    print(f"Total: {len(commands)} commands")


def show_usage_examples(commands):
    """Show usage examples with actual command names"""

    print("\n" + "=" * 70)
    print("USAGE EXAMPLES")
    print("=" * 70)
    print()

    print("Option 1: Base class with command names")
    print("-" * 70)
    print("from squawkers import Squawkers")
    print("from saga_assistant.ha_client import HomeAssistantClient")
    print()
    print("client = HomeAssistantClient()")
    print("squawkers = Squawkers(client)")
    print()

    # Show examples with actual commands
    categories = categorize_commands(commands)

    if categories['universal']:
        for cmd in categories['universal'][:2]:
            print(f"squawkers.command('{cmd}')")

    if categories['response'] and len(categories['response']) > 0:
        print(f"squawkers.command('{categories['response'][0]}')")

    if categories['gags'] and len(categories['gags']) > 0:
        print(f"squawkers.command('{categories['gags'][0]}')")

    print()
    print("Option 2: Full class with convenience methods")
    print("-" * 70)
    print("from squawkers.squawkers_full import SquawkersFull")
    print("from saga_assistant.ha_client import HomeAssistantClient")
    print()
    print("client = HomeAssistantClient()")
    print("squawkers = SquawkersFull(client)")
    print()
    print("squawkers.dance()       # DANCE")
    print("squawkers.reset()       # RESET")

    if categories['response']:
        print("squawkers.response_a()  # Response Button A")
        print("squawkers.response_b()  # Response Button B")

    if categories['gags']:
        print("squawkers.gag_a()       # Gags A")

    print()


def main():
    """Main function"""

    load_dotenv()

    print("=" * 70)
    print("SQUAWKERS COMMAND DISCOVERY")
    print("=" * 70)
    print()

    # Fetch codes from HA
    data = fetch_broadlink_codes()

    if not data:
        print("\n❌ Failed to fetch codes from Home Assistant")
        print()
        print("Troubleshooting:")
        print("  1. Check SSH access: ssh root@homeassistant.local")
        print("  2. Verify file exists:")
        print("     ssh root@homeassistant.local 'ls /config/.storage/broadlink_*'")
        print("  3. Check SSH keys are set up correctly")
        print()
        print("Alternative: Use the Web UI method")
        print("  Developer Tools > Services > remote.send_command")
        print()
        return 1

    # Extract squawkers commands
    commands = extract_squawkers_commands(data)

    if not commands:
        print("\n❌ No 'squawkers' device found in Broadlink codes")
        print()
        print("Available devices:")
        if 'data' in data:
            for device_name in data['data'].keys():
                print(f"  • {device_name}")
        print()
        print("Make sure you've learned commands with device name 'squawkers'")
        return 1

    # Show discovered commands
    show_commands(commands)

    # Show usage examples
    show_usage_examples(commands)

    print("=" * 70)
    print()
    print("✓ Command discovery complete!")
    print()
    print("Next steps:")
    print("  • Test: pipenv run python squawkers/try_squawkers.py")
    print("  • Docs: cat squawkers/MY_COMMANDS.md")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
