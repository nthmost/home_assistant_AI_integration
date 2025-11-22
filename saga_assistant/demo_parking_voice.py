#!/usr/bin/env python3
"""
Demo parking voice commands through intent parser

Shows how parking integrates with Saga's voice interface
"""

import sys
import logging
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from saga_assistant.intent_parser import IntentParser, IntentParseError
from saga_assistant.ha_client import HomeAssistantClient

logging.basicConfig(level=logging.WARNING, format='%(message)s')

def main():
    print("\n" + "="*70)
    print("🚗 Saga Parking Voice Commands Demo")
    print("="*70)

    # Initialize
    print("\nInitializing...")
    ha = HomeAssistantClient()
    parser = IntentParser(ha)
    print("✓ Ready\n")

    # Test parking commands
    test_scenarios = [
        {
            "title": "Tell Saga where you parked",
            "command": "I parked on the north side of Anza between 7th and 8th ave"
        },
        {
            "title": "Ask where you parked",
            "command": "where did I park"
        },
        {
            "title": "Ask when to move your car",
            "command": "when do I need to move my car"
        },
        {
            "title": "Check for street sweeping",
            "command": "is there street sweeping"
        },
        {
            "title": "Try a different location",
            "command": "I parked on Valencia between 18th and 19th"
        },
        {
            "title": "Check the new location",
            "command": "when do I need to move my car"
        },
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print("-" * 70)
        print(f"Scenario {i}: {scenario['title']}")
        print("-" * 70)
        print(f"\n🎤 You: \"{scenario['command']}\"\n")

        try:
            result = parser.parse_and_execute(scenario['command'])
            print(f"🤖 Saga: {result['message']}\n")
        except IntentParseError as e:
            print(f"❌ Error: {e}\n")

    print("=" * 70)
    print("Demo complete!")
    print("=" * 70 + "\n")

    # Interactive mode
    print("\nEnter interactive mode? (y/n): ", end='')
    if input().strip().lower() == 'y':
        print("\n" + "="*70)
        print("Interactive Parking Commands (Ctrl+C to exit)")
        print("="*70)
        print("\nTry commands like:")
        print("  - I parked on Mission between 24th and 25th")
        print("  - where did I park")
        print("  - when do I need to move my car")
        print("  - is there street sweeping\n")

        try:
            while True:
                cmd = input("🎤 You: ").strip()
                if not cmd:
                    continue

                try:
                    result = parser.parse_and_execute(cmd)
                    print(f"🤖 Saga: {result['message']}\n")
                except IntentParseError as e:
                    print(f"❌ {e}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!\n")


if __name__ == '__main__':
    main()
