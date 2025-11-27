#!/usr/bin/env python3
"""Test location name formatting for voice output."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from saga_assistant.modules.road_trip.routing import Location


def test_format_concise():
    """Test Location.format_concise() method."""

    test_cases = [
        {
            'address': 'Big Sur, Monterey County, California, United States of America',
            'expected': 'Big Sur in Monterey County, California',
            'description': 'Full US address with county'
        },
        {
            'address': 'San Francisco, California, United States',
            'expected': 'San Francisco, California',
            'description': 'City and state only'
        },
        {
            'address': 'Los Angeles, Los Angeles County, California, USA',
            'expected': 'Los Angeles in Los Angeles County, California',
            'description': 'Full US address with USA abbreviation'
        },
        {
            'address': 'Yosemite Valley, Mariposa County, California',
            'expected': 'Yosemite Valley in Mariposa County, California',
            'description': 'No country specified'
        },
        {
            'address': 'Paris, Île-de-France, France',
            'expected': 'Paris in Île-de-France, France',
            'description': 'International location'
        },
        {
            'address': '',
            'expected': 'your destination',
            'description': 'Empty address'
        },
    ]

    print("🧪 Testing Location.format_concise()")
    print("=" * 70)

    passed = 0
    failed = 0

    for test in test_cases:
        location = Location(
            latitude=0.0,
            longitude=0.0,
            address=test['address']
        )

        result = location.format_concise()

        if result == test['expected']:
            print(f"✅ {test['description']}")
            print(f"   Input:    {test['address']}")
            print(f"   Output:   {result}")
            passed += 1
        else:
            print(f"❌ {test['description']}")
            print(f"   Input:    {test['address']}")
            print(f"   Expected: {test['expected']}")
            print(f"   Got:      {result}")
            failed += 1
        print()

    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")

    return failed == 0


if __name__ == '__main__':
    success = test_format_concise()
    sys.exit(0 if success else 1)
