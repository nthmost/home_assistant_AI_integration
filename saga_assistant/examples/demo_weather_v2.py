#!/usr/bin/env python3
"""
Weather V2 Demo - Multi-Location, Fuzzy Matching, 5-Day Forecasts

Shows off all the new V2 capabilities for bike ride planning!
"""

from saga_assistant.weather_v2 import (
    get_weather,
    get_week_summary,
    compare_locations,
    will_it_rain,
    get_wind_info
)

def demo():
    print("=" * 60)
    print("🌤️  WEATHER V2 DEMO - BIKE RIDE PLANNING")
    print("=" * 60)

    # 1. Fuzzy Location Matching
    print("\n📍 FUZZY LOCATION MATCHING")
    print("-" * 60)
    print("You can now query locations in many ways:\n")

    test_variations = [
        ("San Francisco", "tomorrow"),
        ("SF", "tomorrow"),
        ("san francisco", "tomorrow"),
        ("francisco", "tomorrow"),
    ]

    for location, when in test_variations:
        result = get_weather(location, when)
        print(f"  '{location:20}' → {result}")

    # 2. Multi-Day Forecasts
    print("\n📅 5-DAY FORECASTS")
    print("-" * 60)
    days = ["today", "tomorrow", "wednesday", "thursday", "friday"]
    for day in days:
        result = get_weather("San Francisco", day)
        print(f"  {result}")

    # 3. Week Summary
    print("\n📊 WEEK SUMMARIES")
    print("-" * 60)
    for location in ["San Francisco", "Marin City", "Sausalito", "Daly City"]:
        summary = get_week_summary(location)
        print(f"  {summary}")

    # 4. Location Comparison (Perfect for Bike Planning!)
    print("\n🚴 BIKE RIDE COMPARISON")
    print("-" * 60)
    comparison = compare_locations(
        ["San Francisco", "Marin City", "Sausalito", "Daly City"],
        "tomorrow"
    )
    print(comparison)

    # 5. Rain Check
    print("\n☔ RAIN FORECASTS")
    print("-" * 60)
    for location in ["San Francisco", "Marin City", "Sausalito"]:
        rain = will_it_rain(location, "tomorrow")
        print(f"  {location}: {rain}")

    # 6. Wind Info
    print("\n💨 WIND CONDITIONS")
    print("-" * 60)
    for location in ["San Francisco", "Marin City", "Daly City"]:
        wind = get_wind_info(location)
        print(f"  {location}: {wind}")

    print("\n" + "=" * 60)
    print("✅ All queries are instant - reading from local cache!")
    print("=" * 60)

if __name__ == "__main__":
    demo()
