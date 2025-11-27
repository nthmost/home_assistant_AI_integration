#!/usr/bin/env python3
"""
Demo script for Road Trip Planning Module

Shows basic usage of routing, traffic, and POI features.
"""

import logging
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from saga_assistant.modules.road_trip.handler import RoadTripHandler
from saga_assistant.modules.road_trip.routing import Location

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def demo_basic_queries():
    """Demo basic road trip queries."""
    print_header("🚗 Road Trip Planning Module Demo")

    # Create handler with SF as home location
    home = Location(
        latitude=37.7749,
        longitude=-122.4194,
        address="San Francisco, CA"
    )

    handler = RoadTripHandler(home, unit_system='imperial')

    # Test queries
    queries = [
        ("Distance Query", "how far is the drive to Sacramento?", False),
        ("Quick Distance", "how far to LA?", True),
        ("Travel Time", "how long will it take to get to San Jose?", False),
        ("Quick Time", "how long to Oakland?", True),
        ("Best Departure", "when should I leave for Lake Tahoe?", False),
        ("POI Query", "what landmarks are between here and Big Sur?", False),
    ]

    for title, query, quick_mode in queries:
        print(f"\n{'🔸' if quick_mode else '📍'} {title}")
        print(f"Query: \"{query}\"")
        print(f"Mode: {'Quick' if quick_mode else 'Detailed'}")
        print("-" * 70)

        try:
            response = handler.handle_query(query, quick_mode=quick_mode)
            print(f"Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.debug(f"Full error: {e}", exc_info=True)

        print()


def demo_quick_mode_comparison():
    """Demo quick mode vs detailed mode side-by-side."""
    print_header("⚡ Quick Mode vs Detailed Mode Comparison")

    home = Location(latitude=37.7749, longitude=-122.4194, address="San Francisco")
    handler = RoadTripHandler(home, unit_system='imperial')

    test_cases = [
        "how far is the drive to Sacramento?",
        "when should I leave for Lake Tahoe?",
        "how long will it take to get to San Jose?",
    ]

    for query in test_cases:
        print(f"\n📝 Query: \"{query}\"")
        print("-" * 70)

        try:
            # Detailed mode
            detailed = handler.handle_query(query, quick_mode=False)
            print(f"Detailed: {detailed}")

            # Quick mode
            quick = handler.handle_query(query, quick_mode=True)
            print(f"Quick:    {quick}")

        except Exception as e:
            print(f"❌ Error: {e}")

        print()


def demo_constraint_parsing():
    """Demo time constraint parsing."""
    print_header("⏰ Time Constraint Examples")

    home = Location(latitude=37.7749, longitude=-122.4194, address="San Francisco")
    handler = RoadTripHandler(home, unit_system='imperial')

    queries = [
        "when should I leave for Sacramento after 5pm?",
        "best time to leave for Tahoe before noon?",
        "what are the 3 best times to leave for San Jose tomorrow?",
    ]

    for query in queries:
        print(f"\n📍 Query: \"{query}\"")
        print("-" * 70)

        try:
            response = handler.handle_query(query, quick_mode=False)
            print(f"Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")

        print()


def main():
    """Run all demos."""
    try:
        demo_basic_queries()
        demo_quick_mode_comparison()
        demo_constraint_parsing()

        print("\n" + "=" * 70)
        print("  ✅ Demo Complete!")
        print("=" * 70 + "\n")

        print("💡 Tips:")
        print("  - Set API keys in .env for traffic data (TomTom, HERE)")
        print("  - Use 'quick question' prefix for brief responses")
        print("  - All queries use your Home Assistant home location")
        print()

    except KeyboardInterrupt:
        print("\n\n⏸️  Demo interrupted\n")
    except Exception as e:
        print(f"\n\n❌ Error: {e}\n")
        logger.error("Demo failed", exc_info=True)


if __name__ == '__main__':
    main()
