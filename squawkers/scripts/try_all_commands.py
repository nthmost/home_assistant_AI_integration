#!/usr/bin/env python3
"""
Test all Squawkers command types.

This script tests one command from each category to verify they all work.
"""

import sys
import time
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from squawkers.squawkers_full import SquawkersFull
from squawkers.squawkers import CommandError
from saga_assistant.ha_client import HomeAssistantClient


def test_command(squawkers, name, method_name, description):
    """Test a single command"""
    print(f"\n{name}")
    print(f"  Description: {description}")
    print(f"  Command: squawkers.{method_name}()")

    try:
        method = getattr(squawkers, method_name)
        method()
        print(f"  ✓ Success!")
        return True
    except CommandError as e:
        print(f"  ✗ Failed: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Test all command types"""
    load_dotenv()

    print("=" * 70)
    print("TESTING ALL SQUAWKERS COMMAND TYPES")
    print("=" * 70)

    try:
        client = HomeAssistantClient()
        squawkers = SquawkersFull(client)

        print("\n✓ Connected to Home Assistant")

        results = {}

        # Test universal commands
        print("\n" + "─" * 70)
        print("UNIVERSAL COMMANDS")
        print("─" * 70)

        results['dance'] = test_command(
            squawkers, "DANCE", "dance",
            "Most reliable - makes it dance"
        )
        time.sleep(2)

        results['reset'] = test_command(
            squawkers, "RESET", "reset",
            "Most reliable - stops current action"
        )
        time.sleep(2)

        # Test Response mode
        print("\n" + "─" * 70)
        print("RESPONSE MODE (Preset behaviors)")
        print("─" * 70)

        results['response_a'] = test_command(
            squawkers, "Response Button A", "response_a",
            "Startled squawk"
        )
        time.sleep(2)

        # Test Command mode
        print("\n" + "─" * 70)
        print("COMMAND MODE (Custom voice commands)")
        print("─" * 70)

        results['command_c'] = test_command(
            squawkers, "Command Button C", "command_c",
            "Custom command (if programmed)"
        )
        time.sleep(2)

        # Test plain buttons
        print("\n" + "─" * 70)
        print("PLAIN BUTTONS")
        print("─" * 70)

        results['button_b'] = test_command(
            squawkers, "Button B", "button_b",
            "Plain button B"
        )
        time.sleep(2)

        # Test Gags mode
        print("\n" + "─" * 70)
        print("GAGS MODE")
        print("─" * 70)

        results['gag_a'] = test_command(
            squawkers, "Gags A", "gag_a",
            "Gag A"
        )

        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)

        passed = sum(1 for v in results.values() if v)
        total = len(results)

        print(f"\nTests passed: {passed}/{total}")
        print("\nResults:")
        for cmd, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {cmd}")

        if passed == total:
            print("\n🎉 All commands working!")
        elif passed > 0:
            print(f"\n⚠️  Some commands working ({passed}/{total})")
            print("\nNote: Failed commands may not be learned in HA yet.")
        else:
            print("\n❌ No commands working")
            print("\nCheck your Home Assistant setup:")
            print("  1. Is the Broadlink remote working?")
            print("  2. Are commands learned for device 'squawkers'?")
            print("  3. Try: python squawkers/list_commands.py")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
