#!/usr/bin/env python3
"""Test end-to-end road trip integration with intent parser."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from dotenv import load_dotenv
from saga_assistant.intent_parser import IntentParser

# Load environment
load_dotenv()

def test_road_trip_intents():
    """Test various road trip queries through the intent parser."""

    print("🧪 Testing Road Trip Intent Parsing & Execution")
    print("=" * 60)
    print()

    # Initialize parser (without real HA client)
    parser = IntentParser(ha_client=None)

    # Test queries (the ones from your logs)
    test_queries = [
        ("What's the drive time to Big Sur?", "road_trip_time"),
        ("Quick question, what's the drive time to Big Sur?", "road_trip_time"),
        ("best time to leave for Big Sur tomorrow.", "road_trip_best_time"),
        ("How far is it to Sacramento?", "road_trip_distance"),
        ("When should I leave for Lake Tahoe?", "road_trip_best_time"),
    ]

    for query, expected_action in test_queries:
        print(f"📝 Query: \"{query}\"")
        print(f"   Expected action: {expected_action}")

        try:
            # Parse intent
            intent = parser.parse(query)

            print(f"   ✅ Parsed: action={intent.action}, confidence={intent.confidence:.2f}")

            if intent.data and 'destination' in intent.data:
                print(f"   🎯 Destination: {intent.data['destination']}")

            # Execute intent
            result = parser.execute(intent)

            # Check for message or response
            response = result.get('message') or result.get('response')
            if response:
                # Truncate long responses
                if len(response) > 120:
                    response = response[:117] + "..."
                print(f"   💬 Response: {response}")
            else:
                print(f"   ⚠️  No response in result: {result}")

            print()

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            print()

    print("=" * 60)
    print("✅ Test complete!")


if __name__ == '__main__':
    test_road_trip_intents()
