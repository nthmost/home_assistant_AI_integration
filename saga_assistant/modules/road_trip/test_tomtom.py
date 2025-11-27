#!/usr/bin/env python3
"""Quick test of TomTom API integration."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from dotenv import load_dotenv
from saga_assistant.modules.road_trip.routing import Location, Route
from saga_assistant.modules.road_trip.traffic import get_traffic_conditions
from datetime import datetime

# Load environment
load_dotenv()

def test_traffic_api():
    """Test TomTom traffic API with a real route."""

    print("🔍 Testing TomTom Traffic API...")
    print(f"   API Key configured: {bool(os.getenv('TOMTOM_API_KEY'))}")
    print()

    # Create a test route (SF to Sacramento via I-80)
    home = Location(latitude=37.7749, longitude=-122.4194, address="San Francisco")
    sacramento = Location(latitude=38.5816, longitude=-121.4944, address="Sacramento")

    # Create mock route
    route = Route(
        distance_miles=87,
        duration_seconds=5400,  # 1.5 hours
        route_name="via I-80",
        geometry=[
            (37.7749, -122.4194),  # SF
            (37.8044, -122.2711),  # Berkeley
            (37.9577, -122.0568),  # Concord
            (38.0293, -121.8053),  # Pittsburg
            (38.2544, -121.9368),  # Fairfield
            (38.4405, -121.6698),  # Dixon
            (38.5816, -121.4944),  # Sacramento
        ],
        start=home,
        end=sacramento,
    )

    print(f"📍 Test Route: {route.start.address} → {route.end.address}")
    print(f"   Distance: {route.distance_miles} miles")
    print(f"   Base time: {route.format_duration()}")
    print()

    # Get traffic conditions
    try:
        traffic = get_traffic_conditions(route, datetime.now())

        print("✅ Traffic API Response:")
        print(f"   Severity: {traffic.severity}")
        print(f"   Delay: {traffic.delay_seconds} seconds ({traffic.delay_seconds // 60} min)")
        print(f"   Description: {traffic.description}")
        print(f"   Incidents: {len(traffic.incidents)}")

        if traffic.incidents:
            print()
            print("🚨 Traffic Incidents:")
            for i, incident in enumerate(traffic.incidents[:3], 1):
                print(f"   {i}. {incident.type}: {incident.description} ({incident.severity})")

        return True

    except Exception as e:
        print(f"❌ Traffic API Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_traffic_api()
    sys.exit(0 if success else 1)
