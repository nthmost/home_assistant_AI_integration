#!/usr/bin/env python3
"""Check for Zigbee temperature and humidity sensors in Home Assistant"""

import logging
from ha_core.client import HomeAssistantInspector
from ha_core.config import load_credentials

# Set up colorful logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

def main():
    # Load credentials and create inspector
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token)

    print("\n🔍 Searching for temperature and humidity sensors...\n")

    # Get all sensor entities
    all_sensors = inspector.get_entities_by_domain('sensor')

    # Filter for temperature sensors
    temp_sensors = [s for s in all_sensors if 'temperature' in s.entity_id.lower()]
    humidity_sensors = [s for s in all_sensors if 'humidity' in s.entity_id.lower()]

    # Look specifically for zigbee-related sensors
    print("🌡️  TEMPERATURE SENSORS:")
    print("=" * 70)
    if temp_sensors:
        for sensor in temp_sensors:
            state = sensor.state.state if hasattr(sensor.state, 'state') else 'unknown'
            attrs = sensor.state.attributes if hasattr(sensor.state, 'attributes') else {}
            device_class = attrs.get('device_class', 'N/A')
            unit = attrs.get('unit_of_measurement', '')
            friendly_name = attrs.get('friendly_name', sensor.entity_id)

            # Check if it's zigbee related
            is_zigbee = 'zigbee' in sensor.entity_id.lower() or 'zigbee' in str(attrs).lower()
            zigbee_marker = "🔗 ZIGBEE" if is_zigbee else ""

            print(f"  {friendly_name} {zigbee_marker}")
            print(f"    ID: {sensor.entity_id}")
            print(f"    State: {state} {unit}")
            print(f"    Device Class: {device_class}")
            print(f"    Last Updated: {attrs.get('last_updated', 'N/A')}")
            print()
    else:
        print("  ❌ No temperature sensors found\n")

    print("\n💧 HUMIDITY SENSORS:")
    print("=" * 70)
    if humidity_sensors:
        for sensor in humidity_sensors:
            state = sensor.state.state if hasattr(sensor.state, 'state') else 'unknown'
            attrs = sensor.state.attributes if hasattr(sensor.state, 'attributes') else {}
            device_class = attrs.get('device_class', 'N/A')
            unit = attrs.get('unit_of_measurement', '')
            friendly_name = attrs.get('friendly_name', sensor.entity_id)

            # Check if it's zigbee related
            is_zigbee = 'zigbee' in sensor.entity_id.lower() or 'zigbee' in str(attrs).lower()
            zigbee_marker = "🔗 ZIGBEE" if is_zigbee else ""

            print(f"  {friendly_name} {zigbee_marker}")
            print(f"    ID: {sensor.entity_id}")
            print(f"    State: {state} {unit}")
            print(f"    Device Class: {device_class}")
            print(f"    Last Updated: {attrs.get('last_updated', 'N/A')}")
            print()
    else:
        print("  ❌ No humidity sensors found\n")

    # Summary
    print("\n📊 SUMMARY:")
    print("=" * 70)
    zigbee_temps = [s for s in temp_sensors if 'zigbee' in s.entity_id.lower()]
    zigbee_humidity = [s for s in humidity_sensors if 'zigbee' in s.entity_id.lower()]

    print(f"  Total temperature sensors: {len(temp_sensors)}")
    print(f"  Zigbee temperature sensors: {len(zigbee_temps)}")
    print(f"  Total humidity sensors: {len(humidity_sensors)}")
    print(f"  Zigbee humidity sensors: {len(zigbee_humidity)}")
    print()

if __name__ == '__main__':
    main()
