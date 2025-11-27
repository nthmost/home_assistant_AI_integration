#!/usr/bin/env python3
"""Test Big Basin geocoding - should pick California, not Kansas/Canada."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from saga_assistant.modules.road_trip.routing import geocode

def test_big_basin():
    """Test that Big Basin geocodes to California."""
    print("🧪 Testing Big Basin Geocoding")
    print("=" * 70)

    location = geocode("Big Basin")

    print(f"📍 Geocoded to: {location.address}")
    print(f"   Latitude:  {location.latitude}")
    print(f"   Longitude: {location.longitude}")
    print()

    # Check if it's California (rough lat/lon check)
    # California is roughly 32-42°N, -124 to -114°W
    is_california = (32 <= location.latitude <= 42 and
                     -124 <= location.longitude <= -114)

    if is_california and "California" in location.address:
        print("✅ Correctly chose California location!")
        return True
    else:
        print(f"❌ Wrong location - should be California, got: {location.address}")
        return False


if __name__ == '__main__':
    success = test_big_basin()
    sys.exit(0 if success else 1)
