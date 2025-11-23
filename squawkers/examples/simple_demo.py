#!/usr/bin/env python3
"""
Simple Squawkers demo - 3 commands with 5 second pauses.

Easy to modify - just change the commands in the DEMO_SEQUENCE list!
"""

import sys
import time
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from squawkers.squawkers_full import SquawkersFull
from saga_assistant.ha_client import HomeAssistantClient


# ============================================================================
# MODIFY THIS SECTION
# ============================================================================

# Pause between commands (seconds)
PAUSE_DURATION = 5

# Demo sequence - modify these to test different commands!
# Use any method from SquawkersFull - see MY_COMMANDS.md for full list
DEMO_SEQUENCE = [
    "dance",       # Make it dance
    "gag_a",       # Gag A
    "button_b",    # Button B
]

# ============================================================================
# END CUSTOMIZATION SECTION
# ============================================================================


def run_demo():
    """Run the demo sequence"""
    load_dotenv()

    print("=" * 70)
    print("SQUAWKERS SIMPLE DEMO")
    print("=" * 70)
    print()
    print(f"Sequence: {len(DEMO_SEQUENCE)} commands")
    print(f"Pause: {PAUSE_DURATION} seconds between commands")
    print()

    for i, cmd in enumerate(DEMO_SEQUENCE, 1):
        print(f"  {i}. {cmd}()")
    print()
    print("=" * 70)

    # Initialize
    print("\n🔌 Connecting to Home Assistant...")
    client = HomeAssistantClient()
    squawkers = SquawkersFull(client)
    print("✓ Connected!")

    # Run sequence
    print(f"\n▶ Starting sequence...\n")

    for i, command_name in enumerate(DEMO_SEQUENCE, 1):
        print(f"[{i}/{len(DEMO_SEQUENCE)}] Sending: {command_name}()")

        # Get the method and call it
        method = getattr(squawkers, command_name)
        method()

        print(f"✓ Sent!")

        # Pause between commands (but not after the last one)
        if i < len(DEMO_SEQUENCE):
            print(f"   Waiting {PAUSE_DURATION} seconds...\n")
            time.sleep(PAUSE_DURATION)

    print("\n" + "=" * 70)
    print("✓ Demo complete!")
    print("=" * 70)
    print()
    print("To modify:")
    print("  1. Edit DEMO_SEQUENCE list at top of this file")
    print("  2. Change PAUSE_DURATION for different timing")
    print("  3. Run again!")
    print()
    print("Available commands: see MY_COMMANDS.md or run:")
    print("  pipenv run python squawkers/squawkers_full.py")
    print()


if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import logging
        logging.exception("Demo failed")
        exit(1)
