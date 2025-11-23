#!/usr/bin/env python3
"""
Check Home Assistant Broadlink storage for learned commands.

This script attempts to find and read the Broadlink codes storage file
to show exactly what commands are learned for the 'squawkers' device.
"""

import json
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from saga_assistant.ha_client import HomeAssistantClient


def find_broadlink_storage_files():
    """
    Try to find Broadlink storage files.

    Note: This requires SSH access to the Home Assistant server
    or mounting the HA config directory locally.
    """

    # Common locations for HA config
    possible_paths = [
        Path("/config/.storage"),  # Running on HA server
        Path.home() / "homeassistant" / ".storage",  # Local HA install
        Path("/usr/share/hassio/homeassistant/.storage"),  # HassOS
    ]

    found_files = []

    for base_path in possible_paths:
        if base_path.exists():
            # Look for broadlink_remote_*_codes files
            pattern = "broadlink_remote_*_codes"
            matches = list(base_path.glob(pattern))
            found_files.extend(matches)

    return found_files


def read_broadlink_codes(file_path):
    """Read and parse Broadlink codes file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def show_squawkers_commands(data):
    """Extract and show commands for 'squawkers' device"""

    if not data or 'data' not in data:
        print("No data found in file")
        return

    # The structure is usually: data -> commands -> device_name -> command_name
    commands_data = data.get('data', {})

    # Look for squawkers device
    squawkers_commands = None

    # Try different possible structures
    if 'squawkers' in commands_data:
        squawkers_commands = commands_data['squawkers']
    elif 'commands' in commands_data and 'squawkers' in commands_data['commands']:
        squawkers_commands = commands_data['commands']['squawkers']
    else:
        # Search through all keys
        for key, value in commands_data.items():
            if isinstance(value, dict) and 'squawkers' in value:
                squawkers_commands = value['squawkers']
                break

    if squawkers_commands:
        print("\n✓ Found Squawkers commands:")
        print("-" * 70)

        if isinstance(squawkers_commands, dict):
            for cmd_name in sorted(squawkers_commands.keys()):
                print(f"  • {cmd_name}")
        elif isinstance(squawkers_commands, list):
            for cmd_name in sorted(squawkers_commands):
                print(f"  • {cmd_name}")
        else:
            print(f"  Unknown structure: {type(squawkers_commands)}")
    else:
        print("\n✗ No 'squawkers' device found in this file")
        print("\nAvailable devices:")
        if isinstance(commands_data, dict):
            for key in commands_data.keys():
                print(f"  • {key}")


def main():
    """Main function"""

    print("=" * 70)
    print("BROADLINK CODES STORAGE CHECK")
    print("=" * 70)
    print()

    # Try to find storage files
    print("Searching for Broadlink storage files...")
    files = find_broadlink_storage_files()

    if files:
        print(f"\n✓ Found {len(files)} file(s):")
        for f in files:
            print(f"  • {f}")
        print()

        # Read each file
        for file_path in files:
            print("\n" + "=" * 70)
            print(f"Reading: {file_path.name}")
            print("=" * 70)

            data = read_broadlink_codes(file_path)
            if data:
                show_squawkers_commands(data)
    else:
        print("\n✗ No Broadlink storage files found locally")
        print()
        print("This is expected if you're not running on the HA server.")
        print()
        print("To access these files, you need to:")
        print()
        print("Option 1: SSH to Home Assistant")
        print("  ssh root@homeassistant.local")
        print("  cat /config/.storage/broadlink_remote_*_codes | jq '.data'")
        print()
        print("Option 2: Use File Editor Add-on")
        print("  1. Install 'File Editor' add-on in HA")
        print("  2. Navigate to /.storage/")
        print("  3. Open broadlink_remote_*_codes files")
        print("  4. Search for 'squawkers'")
        print()
        print("Option 3: Use API (limited)")
        print("  The commands you've learned should work even without")
        print("  seeing the storage file. Try:")
        print("    pipenv run python squawkers/try_all_commands.py")
        print()
        print("=" * 70)
        print()
        print("ALTERNATIVE: Check in Home Assistant UI")
        print()
        print("1. Go to: Developer Tools > Services")
        print("2. Service: remote.send_command")
        print("3. Entity: remote.office_lights")
        print("4. Device: squawkers")
        print("5. Click in 'command' field - should show dropdown")
        print()

    print("\n" + "=" * 70)
    print()


if __name__ == "__main__":
    main()
