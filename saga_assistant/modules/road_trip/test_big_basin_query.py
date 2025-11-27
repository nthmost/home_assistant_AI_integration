#!/usr/bin/env python3
"""Test Big Basin voice query end-to-end."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from saga_assistant.modules.road_trip.llm_extractor import LLMIntentExtractor
from saga_assistant.modules.road_trip.handler import RoadTripHandler
from saga_assistant.modules.road_trip.routing import Location

def test_big_basin_query():
    """Test 'How long is the drive to Big Basin?' query."""
    print("🧪 Testing Big Basin Voice Query")
    print("=" * 70)

    # Create handler with mock home location (San Francisco)
    home = Location(latitude=37.7749, longitude=-122.4194, address="San Francisco")
    handler = RoadTripHandler(home, unit_system='imperial')

    # Use LLM extractor
    extractor = LLMIntentExtractor()

    query = "How long is the drive to Big Basin?"
    print(f"📝 Query: {query}")
    print()

    # Extract intent with LLM
    llm_result = extractor.extract_road_trip_intent(query)
    print(f"LLM extracted: {llm_result}")
    print()

    destination = llm_result['destination']
    action_type = 'road_trip_time'  # "How long" = time query

    # Call handler
    response = handler.handle_query_with_destination(
        destination=destination,
        action_type=action_type,
        quick_mode=False,
        original_query=query
    )

    print(f"💬 Response: {response}")
    print()

    # Check if response mentions California (not Canada)
    if "California" in response and "Canada" not in response:
        print("✅ Correctly chose California location!")
        return True
    else:
        print(f"❌ Wrong location in response")
        return False


if __name__ == '__main__':
    success = test_big_basin_query()
    sys.exit(0 if success else 1)
