#!/usr/bin/env python3
"""Check ALL entities for anything related to temperature or humidity"""

import logging
from ha_core.client import HomeAssistantInspector
from ha_core.config import load_credentials

# Suppress logs for cleaner output
logging.basicConfig(level=logging.WARNING)

def main():
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token)

    print("\n🔍 Searching ALL entity domains for temperature/humidity...\n")

    # Get all domains
    all_domains = inspector.list_domains()

    temp_related = []
    humid_related = []
    zigbee_devices = []

    # Check every domain
    for domain in all_domains:
        entities = inspector.get_entities_by_domain(domain)

        for entity in entities:
            entity_id = entity.entity_id
            entity_lower = entity_id.lower()
            attrs = entity.state.attributes if hasattr(entity.state, 'attributes') else {}

            # Check for temperature
            if 'temp' in entity_lower or attrs.get('device_class') == 'temperature':
                temp_related.append(entity)

            # Check for humidity
            if 'humid' in entity_lower or attrs.get('device_class') == 'humidity':
                humid_related.append(entity)

            # Check for zigbee
            if 'zigbee' in entity_lower or 'third_reality' in entity_lower:
                zigbee_devices.append(entity)

    print("🌡️  TEMPERATURE SENSORS:")
    print("=" * 80)
    if temp_related:
        for entity in temp_related:
            state = entity.state.state if hasattr(entity.state, 'state') else 'unknown'
            attrs = entity.state.attributes if hasattr(entity.state, 'attributes') else {}
            friendly = attrs.get('friendly_name', entity.entity_id)
            unit = attrs.get('unit_of_measurement', '')
            device_class = attrs.get('device_class', '')

            print(f"  {friendly}")
            print(f"    ID: {entity.entity_id}")
            print(f"    State: {state} {unit}")
            if device_class:
                print(f"    Device Class: {device_class}")
            print()
    else:
        print("  ❌ None found\n")

    print("💧 HUMIDITY SENSORS:")
    print("=" * 80)
    if humid_related:
        for entity in humid_related:
            state = entity.state.state if hasattr(entity.state, 'state') else 'unknown'
            attrs = entity.state.attributes if hasattr(entity.state, 'attributes') else {}
            friendly = attrs.get('friendly_name', entity.entity_id)
            unit = attrs.get('unit_of_measurement', '')
            device_class = attrs.get('device_class', '')

            print(f"  {friendly}")
            print(f"    ID: {entity.entity_id}")
            print(f"    State: {state} {unit}")
            if device_class:
                print(f"    Device Class: {device_class}")
            print()
    else:
        print("  ❌ None found\n")

    print("🔗 ZIGBEE DEVICES (all types):")
    print("=" * 80)
    if zigbee_devices:
        for entity in zigbee_devices:
            state = entity.state.state if hasattr(entity.state, 'state') else 'unknown'
            attrs = entity.state.attributes if hasattr(entity.state, 'attributes') else {}
            friendly = attrs.get('friendly_name', entity.entity_id)
            unit = attrs.get('unit_of_measurement', '')
            device_class = attrs.get('device_class', '')

            print(f"  {friendly}")
            print(f"    ID: {entity.entity_id}")
            print(f"    Domain: {entity.entity_id.split('.')[0]}")
            print(f"    State: {state} {unit}")
            if device_class:
                print(f"    Device Class: {device_class}")
            print()
    else:
        print("  ❌ None found\n")

    print(f"\n📊 SUMMARY:")
    print("=" * 80)
    print(f"  Total domains: {len(all_domains)}")
    print(f"  Temperature sensors: {len(temp_related)}")
    print(f"  Humidity sensors: {len(humid_related)}")
    print(f"  Zigbee devices: {len(zigbee_devices)}")
    print()

if __name__ == '__main__':
    main()
