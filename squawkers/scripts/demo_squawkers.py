#!/usr/bin/env python3
"""
Demo script for Squawkers McCaw control.

Shows various ways to use the Squawkers class.
"""

import sys
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from squawkers.squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient


def main():
    """Run Squawkers demos"""

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    # Load environment
    load_dotenv()

    print("🦜 Squawkers McCaw Demo")
    print("=" * 70)
    print()

    try:
        # Initialize
        print("Connecting to Home Assistant...")
        client = HomeAssistantClient()

        print("Initializing Squawkers controller...")
        squawkers = Squawkers(client, device_name="squawkers")

        print("✓ Ready!\n")

        # Demo menu
        while True:
            print("\n" + "=" * 70)
            print("SQUAWKERS DEMO MENU")
            print("=" * 70)
            print()
            print("1. Make Squawkers dance")
            print("2. Reset Squawkers")
            print("3. Test sequence (dance → wait 5s → reset)")
            print("4. Custom dance duration test")
            print("5. Send custom command")
            print("6. Exit")
            print()

            choice = input("Choose option (1-6): ").strip()

            if choice == "1":
                print("\n🎉 Making Squawkers dance...")
                squawkers.dance()
                print("✓ Dance command sent!")

            elif choice == "2":
                print("\n🛑 Resetting Squawkers...")
                squawkers.reset()
                print("✓ Reset command sent!")

            elif choice == "3":
                print("\n🎬 Running test sequence...")
                squawkers.test_sequence()
                print("✓ Test sequence complete!")

            elif choice == "4":
                duration = input("How many seconds should it dance? (default 5): ").strip()
                try:
                    duration = float(duration) if duration else 5.0
                    print(f"\n🎬 Test sequence with {duration}s dance...")
                    squawkers.test_sequence(dance_duration=duration)
                    print("✓ Test sequence complete!")
                except ValueError:
                    print("❌ Invalid duration")

            elif choice == "5":
                command = input("Enter command name: ").strip().upper()
                if command:
                    repeats_str = input("Number of repeats (default 3): ").strip()
                    try:
                        repeats = int(repeats_str) if repeats_str else None
                        print(f"\n📡 Sending '{command}' command...")
                        squawkers.command(command, num_repeats=repeats)
                        print("✓ Command sent!")
                    except ValueError:
                        print("❌ Invalid repeat count")
                else:
                    print("❌ No command entered")

            elif choice == "6":
                print("\n👋 Goodbye!")
                break

            else:
                print("\n❌ Invalid choice")

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.exception("Error in demo")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
