#!/usr/bin/env python3
"""Test actual voice queries from logs."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from dotenv import load_dotenv
from saga_assistant.intent_parser import IntentParser

load_dotenv()

def test_voice_queries():
    """Test the exact queries from your voice tests."""

    print("🎙️  Testing Actual Voice Queries")
    print("=" * 60)
    print()

    parser = IntentParser(ha_client=None)

    # These are the ACTUAL queries from your logs
    test_queries = [
        "What's the distance to Big Sur from here?",
        "time to pick sir.",  # Transcription error for "Big Sur"
        "Let's the drive time to Big Sur.",  # Weird transcription
    ]

    for query in test_queries:
        print(f"📝 Query: \"{query}\"")

        try:
            intent = parser.parse(query)
            print(f"   Action: {intent.action}")
            print(f"   Confidence: {intent.confidence:.2f}")

            if intent.data and 'destination' in intent.data:
                print(f"   🎯 Destination: {intent.data['destination']}")
            else:
                print(f"   ⚠️  No destination extracted")

            # Try to execute
            result = parser.execute(intent)
            response = result.get('message') or result.get('response')

            if response:
                # Truncate
                if len(response) > 100:
                    response = response[:97] + "..."
                print(f"   💬 Response: {response}")
            else:
                print(f"   ❌ No response")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()

    print("=" * 60)


if __name__ == '__main__':
    test_voice_queries()
