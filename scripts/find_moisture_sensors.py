#!/usr/bin/env python3
"""
Find all sensors that might be soil/moisture sensors.
Looks for sensors with relevant device classes or units.
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ha_core.client import HomeAssistantInspector
from ha_core.config import load_credentials

# Configure logging
logging.basicConfig(level=logging.WARNING)


def main():
    print("\n🔍 Searching for moisture/soil sensors...\n")

    # Load credentials and connect
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=logging.WARNING)

    # Get all sensor entities
    sensors = inspector.get_entities_by_domain('sensor')

    # Look for moisture-related sensors
    moisture_keywords = ['moisture', 'soil', 'conductivity', 'humidity']
    moisture_sensors = []

    for entity in sensors:
        attrs = entity.state.attributes if entity.state else {}
        device_class = attrs.get('device_class', '')
        unit = attrs.get('unit_of_measurement', '')
        friendly_name = attrs.get('friendly_name', '')
        entity_id = entity.entity_id

        # Check if this looks like a moisture/soil sensor
        is_moisture = any(kw in str(device_class).lower() for kw in moisture_keywords)
        is_moisture = is_moisture or any(kw in friendly_name.lower() for kw in moisture_keywords)
        is_moisture = is_moisture or any(kw in entity_id.lower() for kw in moisture_keywords)
        is_moisture = is_moisture or 'µS/cm' in str(unit)  # conductivity unit

        if is_moisture:
            moisture_sensors.append({
                'entity_id': entity_id,
                'name': friendly_name,
                'state': entity.state.state if entity.state else 'unknown',
                'device_class': device_class,
                'unit': unit,
                'all_attrs': attrs
            })

    if not moisture_sensors:
        print("❌ No moisture/soil sensors found\n")
        print("💡 Tip: The sensor might not be fully configured or might be named differently.")
        print("   Try listing all sensors with: pipenv run python scripts/list_all_sensors.py\n")
        return

    print(f"✅ Found {len(moisture_sensors)} moisture/soil sensor(s):\n")
    print("=" * 80)

    for sensor in moisture_sensors:
        print(f"\n📍 {sensor['entity_id']}")
        print(f"   Name: {sensor['name']}")
        print(f"   State: {sensor['state']}")
        if sensor['device_class']:
            print(f"   Device Class: {sensor['device_class']}")
        if sensor['unit']:
            print(f"   Unit: {sensor['unit']}")

        # Show other interesting attributes
        attrs = sensor['all_attrs']
        interesting = ['battery', 'temperature', 'linkquality', 'last_seen', 'voltage']
        for key in interesting:
            if key in attrs:
                print(f"   {key.title()}: {attrs[key]}")

    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    main()
