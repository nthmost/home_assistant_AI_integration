#!/usr/bin/env python3
"""
Demo script for parking and street sweeping features

Shows how to:
- Parse natural language parking locations
- Look up street sweeping schedules
- Save and retrieve parking state
- Check when you need to move your car
"""

import logging
from parking import StreetSweepingLookup, ParkingManager

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def main():
    print("\n" + "="*70)
    print("Saga Assistant - Parking & Street Sweeping Demo")
    print("="*70)

    # Initialize
    lookup = StreetSweepingLookup()
    manager = ParkingManager(lookup)

    print(f"\nLoaded {len(lookup.data)} street sweeping records")
    print(f"Covering {len(lookup.street_index)} streets in San Francisco\n")

    # Demo 1: Parse location and save parking
    print("\n" + "-"*70)
    print("DEMO 1: Tell Saga where you parked")
    print("-"*70)

    location_input = "north side of Anza between 7th and 8th ave"
    print(f"\nYou say: \"I parked on the {location_input}\"")

    location = manager.parser.parse(location_input)
    if location:
        print(f"\n  ✓ Saga understood:")
        print(f"    Street: {location.street}")
        print(f"    Block: {location.block_limits}")
        print(f"    Side: {location.side}")

        manager.save_parking_location(location)
        print(f"\n  ✓ Parking location saved")
    else:
        print(f"\n  ✗ Failed to parse location")
        return

    # Demo 2: Check current parking status
    print("\n" + "-"*70)
    print("DEMO 2: Ask Saga about your parking")
    print("-"*70)

    print(f"\nYou ask: \"Where did I park?\"")
    print(f"\nSaga responds:")
    print(f"  {manager.get_human_readable_status()}")

    # Demo 3: Get next sweeping date
    print("\n" + "-"*70)
    print("DEMO 3: Check when you need to move your car")
    print("-"*70)

    print(f"\nYou ask: \"When do I need to move my car?\"")

    from datetime import datetime

    next_sweep = manager.get_next_sweeping(days_ahead=30)
    if next_sweep:
        schedule = next_sweep['schedule']
        start = next_sweep['start_time']
        delta = start - datetime.now()

        if delta.days == 0:
            when = "TODAY"
        elif delta.days == 1:
            when = "TOMORROW"
        else:
            when = start.strftime('%A, %B %d')

        from_time = f"{schedule.fromhour % 12 or 12}{'am' if schedule.fromhour < 12 else 'pm'}"
        to_time = f"{schedule.tohour % 12 or 12}{'am' if schedule.tohour < 12 else 'pm'}"

        print(f"\nSaga responds:")
        print(f"  Street sweeping is {when}")
        print(f"  {from_time} to {to_time}")
        print(f"  Make sure to move your car by {from_time}!")

        hours_until = delta.total_seconds() / 3600
        if hours_until < 24:
            print(f"\n  ⚠️  That's in {hours_until:.1f} hours!")
    else:
        print(f"\nSaga responds:")
        print(f"  No street sweeping scheduled in the next 30 days")

    # Demo 4: Try different locations
    print("\n" + "-"*70)
    print("DEMO 4: Try other locations")
    print("-"*70)

    test_locations = [
        "Valencia between 18th and 19th",
        "on Mission near 24th street",
    ]

    for loc in test_locations:
        print(f"\n\"{loc}\"")
        parsed = manager.parser.parse(loc)
        if parsed:
            print(f"  ✓ {parsed.street}")
            if parsed.block_limits:
                print(f"    Block: {parsed.block_limits}")
        else:
            print(f"  ✗ Could not parse")

    print("\n" + "="*70)
    print("Demo complete!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
