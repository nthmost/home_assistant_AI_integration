#!/usr/bin/env python3
"""
Quick test script for Squawkers McCaw.

Run the standard test sequence: DANCE → wait 5s → RESET
"""

import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from squawkers.squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient


def main():
    """Quick test"""

    # Simple logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

    # Load environment
    load_dotenv()

    print("🦜 Testing Squawkers McCaw")
    print("=" * 50)
    print()

    try:
        # Initialize
        client = HomeAssistantClient()
        squawkers = Squawkers(client, device_name="squawkers")

        # Run test
        print("Running test sequence:")
        print("  1. DANCE command")
        print("  2. Wait 5 seconds")
        print("  3. RESET command")
        print()

        squawkers.test_sequence()

        print()
        print("✓ Test complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
        logging.exception("Test failed")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
