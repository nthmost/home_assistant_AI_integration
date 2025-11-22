#!/usr/bin/env python3
"""
Demo script to test Minnie blame integration with intent parser.

This simulates what happens when you ask Saga "whose fault is it?"
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from saga_assistant.intent_parser import IntentParser

logging.basicConfig(level=logging.INFO, format="%(message)s")


def main():
    print("\n" + "="*60)
    print("  🐱 Minnie Blame Integration Demo")
    print("  Testing intent parser with Minnie queries")
    print("="*60 + "\n")

    # Initialize intent parser (without HA client for this demo)
    parser = IntentParser(ha_client=None)

    # Test queries
    test_queries = [
        "Whose fault is it?",
        "Who did this?",
        "Who made this mess?",
        "What happened here?",
        "Who broke this?",
        "Who kicked Spartacus out of bed?",
        "Why is there cat puke on the floor?",
        "Was it Minnie?",
        "Did Minnie do this?",
        "Who's running this fascist government?",
    ]

    print("Testing Minnie blame queries:\n")
    for query in test_queries:
        print(f"You: \"{query}\"")
        try:
            # Parse the query
            intent = parser.parse(query)

            # Execute the intent
            result = parser.execute(intent)

            # Show the response
            response = result.get("message", "No response")
            print(f"Saga: {response}")
            print()

        except Exception as e:
            print(f"Error: {e}\n")

    print("="*60)
    print("  ✅ Minnie lives on in Saga's memory!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
