#!/usr/bin/env python3
"""Test LLM-based intent extraction vs regex."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from saga_assistant.modules.road_trip.llm_extractor import LLMIntentExtractor


def test_llm_extraction():
    """Test LLM extraction on problematic queries."""

    print("🧠 Testing LLM-Based Intent Extraction")
    print("=" * 60)
    print()

    extractor = LLMIntentExtractor()

    # Test cases that BROKE with regex
    test_queries = [
        ("What's the distance to Big Sur from here?", "Should extract 'Big Sur'"),
        ("time to pick sir.", "Transcription error: 'pick sir' → 'Big Sur'"),
        ("Let's the drive time to Big Sur.", "Weird transcription"),
        ("How far to Sacramento?", "Simple query"),
        ("When should I leave for Lake Tahoe tomorrow?", "With time constraint"),
        ("What's interesting between here and Yosemite?", "POI query"),
    ]

    for query, description in test_queries:
        print(f"📝 Query: \"{query}\"")
        print(f"   Context: {description}")

        result = extractor.extract_road_trip_intent(query)

        print(f"   ✅ Action: {result['action']}")
        print(f"   🎯 Destination: {result['destination']}")
        if result['departure_time']:
            print(f"   ⏰ Time: {result['departure_time']}")
        print(f"   📊 Confidence: {result['confidence']:.2f}")
        print()

    print("=" * 60)
    print()
    print("🎯 Benefits of LLM Extraction:")
    print("  • Handles transcription errors naturally")
    print("  • No regex pattern maintenance")
    print("  • Works with any natural language variation")
    print("  • Self-correcting (can fix 'pick sir' → 'Big Sur')")
    print("  • Fast with small models (qwen2.5:1.5b)")


if __name__ == '__main__':
    test_llm_extraction()
