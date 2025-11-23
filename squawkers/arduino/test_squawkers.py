#!/usr/bin/env python3
"""
Interactive test script for Squawkers McGraw IR commands
Helps you learn commands with Broadlink and document behaviors
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from saga_assistant.ha_client import HomeAssistantClient
from squawkers.broadlink_squawkers import SquawkersMcGraw, IR_CODES
import time


def learn_all_commands(squawkers: SquawkersMcGraw):
    """
    Guide user through learning all IR commands

    Since we don't have the original remote, we need to manually program
    the IR codes using the timing arrays from GitHub.

    Broadlink doesn't support raw timing uploads via API, so this will
    guide you through the process.
    """
    print("\n" + "="*70)
    print("IR COMMAND LEARNING GUIDE")
    print("="*70)

    print("\n⚠️  IMPORTANT: Broadlink requires learned codes")
    print("Since you don't have the original remote, we have two options:")
    print()
    print("Option 1: Find someone with a working remote and learn codes")
    print("Option 2: Use an Arduino/ESP32 to transmit the timing codes,")
    print("          then use Broadlink learn mode to capture them")
    print()
    print("The timing codes are already in this script.")
    print()

    response = input("Do you have access to an original remote? (y/n): ").lower()

    if response == 'y':
        print("\n📖 Great! Let's learn the commands from your remote...")
        learn_from_remote(squawkers)
    else:
        print("\n💡 You'll need an IR transmitter to generate these codes first.")
        print("Recommended: ESP32 + IR LED ($8-15)")
        print("See: squawkers/IR_CONTROL_RESEARCH.md for details")
        print()
        print("Alternative: Try the light sensor control method instead")
        print("See: squawkers/SENSOR_CONTROL_METHODS.md")


def learn_from_remote(squawkers: SquawkersMcGraw):
    """Guide user through learning commands from original remote"""

    print("\n" + "="*70)
    print("LEARNING COMMANDS FROM REMOTE")
    print("="*70)

    commands_to_learn = [
        ("dance", "Dance button"),
        ("reset", "Reset button"),
        ("response_a", "Response Mode - Button A"),
        ("response_b", "Response Mode - Button B"),
        ("response_c", "Response Mode - Button C"),
        ("response_d", "Response Mode - Button D"),
        ("response_e", "Response Mode - Button E"),
        ("response_f", "Response Mode - Button F"),
        ("command_a", "Command Mode - Button A"),
        ("command_b", "Command Mode - Button B"),
        ("command_c", "Command Mode - Button C"),
        ("command_d", "Command Mode - Button D"),
        ("command_e", "Command Mode - Button E"),
        ("command_f", "Command Mode - Button F"),
        ("gags_a", "Gags Mode - Button A"),
        ("gags_b", "Gags Mode - Button B"),
        ("gags_c", "Gags Mode - Button C"),
        ("gags_d", "Gags Mode - Button D"),
        ("gags_e", "Gags Mode - Button E"),
        ("gags_f", "Gags Mode - Button F"),
    ]

    print(f"\nWe'll learn {len(commands_to_learn)} commands.")
    print("For each command, you'll have 20 seconds to press the button on the remote.")
    print()

    learned_count = 0

    for cmd_name, description in commands_to_learn:
        print(f"\n📡 Learning: {description}")
        print(f"   Command name: {cmd_name}")

        input("Press ENTER when ready, then press the button on remote...")

        try:
            squawkers.remote.learn_command(cmd_name, timeout=20)
            print(f"✅ Learned: {cmd_name}")
            learned_count += 1
            time.sleep(1)
        except Exception as e:
            print(f"❌ Failed to learn {cmd_name}: {e}")
            retry = input("Try again? (y/n): ").lower()
            if retry == 'y':
                try:
                    squawkers.remote.learn_command(cmd_name, timeout=20)
                    print(f"✅ Learned: {cmd_name}")
                    learned_count += 1
                except Exception as e:
                    print(f"❌ Failed again: {e}")

    print(f"\n" + "="*70)
    print(f"✅ Learned {learned_count}/{len(commands_to_learn)} commands")
    print("="*70)


def test_command(squawkers: SquawkersMcGraw, command_name: str):
    """Test a single command and document the behavior"""

    print(f"\n🔊 Testing: {command_name}")
    print("   Sending command 3 times with pauses...")

    try:
        if command_name == "dance":
            squawkers.dance()
        elif command_name == "reset":
            squawkers.reset()
        elif command_name.startswith("response_"):
            button = command_name.split("_")[1].upper()
            squawkers.response_mode_button(button)
        elif command_name.startswith("command_"):
            button = command_name.split("_")[1].upper()
            squawkers.command_mode_button(button)
        elif command_name.startswith("gags_"):
            button = command_name.split("_")[1].upper()
            squawkers.gags_mode_button(button)
        else:
            print(f"❌ Unknown command: {command_name}")
            return

        print("✅ Command sent")

        # Ask user to document what happened
        print("\n📝 What did Squawkers do?")
        behavior = input("   Description: ")

        if behavior.strip():
            squawkers.document_behavior(command_name, behavior)

            # Save to file
            save_behavior(command_name, behavior)

    except Exception as e:
        print(f"❌ Error sending command: {e}")


def save_behavior(command_name: str, description: str):
    """Save discovered behavior to file"""
    behaviors_file = Path(__file__).parent / "discovered_behaviors.txt"

    with open(behaviors_file, "a") as f:
        f.write(f"{command_name}: {description}\n")

    print(f"💾 Saved to: {behaviors_file}")


def interactive_test(squawkers: SquawkersMcGraw):
    """Interactive testing menu"""

    while True:
        print("\n" + "="*70)
        print("SQUAWKERS MCGRAW INTERACTIVE TEST")
        print("="*70)
        print()
        print("1. Test dance command")
        print("2. Test reset command")
        print("3. Test Response Mode commands (A-F)")
        print("4. Test Command Mode commands (A-F)")
        print("5. Test Gags Mode commands (A-F)")
        print("6. Test specific command by name")
        print("7. List all commands")
        print("8. View discovered behaviors")
        print("9. Exit")
        print()

        choice = input("Choose option (1-9): ").strip()

        if choice == "1":
            test_command(squawkers, "dance")
        elif choice == "2":
            test_command(squawkers, "reset")
        elif choice == "3":
            print("\nResponse Mode buttons:")
            for letter in "ABCDEF":
                print(f"  {letter}: response_{letter.lower()}")
            button = input("Which button? (A-F): ").strip().upper()
            if button in "ABCDEF":
                test_command(squawkers, f"response_{button.lower()}")
        elif choice == "4":
            print("\nCommand Mode buttons:")
            for letter in "ABCDEF":
                print(f"  {letter}: command_{letter.lower()}")
            button = input("Which button? (A-F): ").strip().upper()
            if button in "ABCDEF":
                test_command(squawkers, f"command_{button.lower()}")
        elif choice == "5":
            print("\nGags Mode buttons:")
            for letter in "ABCDEF":
                print(f"  {letter}: gags_{letter.lower()}")
            button = input("Which button? (A-F): ").strip().upper()
            if button in "ABCDEF":
                test_command(squawkers, f"gags_{button.lower()}")
        elif choice == "6":
            cmd = input("Command name: ").strip()
            if cmd in IR_CODES:
                test_command(squawkers, cmd)
            else:
                print(f"❌ Unknown command: {cmd}")
                print(f"Available: {', '.join(IR_CODES.keys())}")
        elif choice == "7":
            squawkers.print_all_codes()
        elif choice == "8":
            view_behaviors()
        elif choice == "9":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")


def view_behaviors():
    """View discovered behaviors"""
    behaviors_file = Path(__file__).parent / "discovered_behaviors.txt"

    if not behaviors_file.exists():
        print("\n📝 No behaviors documented yet")
        return

    print("\n" + "="*70)
    print("DISCOVERED BEHAVIORS")
    print("="*70)

    with open(behaviors_file, "r") as f:
        print(f.read())


def main():
    # Load environment
    load_dotenv()
    HA_URL = os.getenv("HA_URL", "http://homeassistant.local:8123")
    HA_TOKEN = os.getenv("HA_TOKEN")

    if not HA_TOKEN:
        print("❌ Error: HA_TOKEN not found in .env file")
        exit(1)

    print("🦜 Squawkers McGraw IR Testing Tool")
    print("="*70)
    print(f"Home Assistant: {HA_URL}")
    print(f"Broadlink Entity: remote.office_lights")
    print()

    # Initialize
    client = HomeAssistantClient(HA_URL, HA_TOKEN)
    squawkers = SquawkersMcGraw(client, entity_id="remote.office_lights")

    # Main menu
    print("\nWhat would you like to do?")
    print("1. Learn commands from original remote")
    print("2. Test commands (already learned)")
    print("3. View all IR codes")
    print("4. Exit")
    print()

    choice = input("Choose option (1-4): ").strip()

    if choice == "1":
        learn_all_commands(squawkers)
    elif choice == "2":
        interactive_test(squawkers)
    elif choice == "3":
        squawkers.print_all_codes()
    else:
        print("👋 Goodbye!")


if __name__ == "__main__":
    main()
