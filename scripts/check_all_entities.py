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

    print("\n🔍 Searching ALL entities for temperature/humidity/climate...\n")

    # Get all entities
    all_entities = inspector.client.get_entities()

    temp_related = []
    humid_related = []
    climate_related = []
    zigbee_devices = []

    for entity in all_entities:
        entity_id = entity.entity_id
        entity_lower = entity_id.lower()

        # Check for temperature
        if 'temp' in entity_lower:
            temp_related.append(entity)

        # Check for humidity
        if 'humid' in entity_lower:
            humid_related.append(entity)

        # Check for climate domain
        if entity_id.startswith('climate.'):
            climate_related.append(entity)

        # Check for zigbee
        if 'zigbee' in entity_lower or 'third_reality' in entity_lower:
            zigbee_devices.append(entity)

    print("🌡️  TEMPERATURE-RELATED ENTITIES:")
    print("=" * 80)
    if temp_related:
        for entity in temp_related:
            state = entity.state.state if hasattr(entity.state, 'state') else 'unknown'
            attrs = entity.state.attributes if hasattr(entity.state, 'attributes') else {}
            friendly = attrs.get('friendly_name', entity.entity_id)
            print(f"  {friendly}")
            print(f"    ID: {entity.entity_id}")
            print(f"    State: {state}")
            print()
    else:
        print("  ❌ None found\n")

    print("💧 HUMIDITY-RELATED ENTITIES:")
    print("=" * 80)
    if humid_related:
        for entity in humid_related:
            state = entity.state.state if hasattr(entity.state, 'state') else 'unknown'
            attrs = entity.state.attributes if hasattr(entity.state, 'attributes') else {}
            friendly = attrs.get('friendly_name', entity.entity_id)
            print(f"  {friendly}")
            print(f"    ID: {entity.entity_id}")
            print(f"    State: {state}")
            print()
    else:
        print("  ❌ None found\n")

    print("🌡️  CLIMATE ENTITIES:")
    print("=" * 80)
    if climate_related:
        for entity in climate_related:
            state = entity.state.state if hasattr(entity.state, 'state') else 'unknown'
            attrs = entity.state.attributes if hasattr(entity.state, 'attributes') else {}
            friendly = attrs.get('friendly_name', entity.entity_id)
            print(f"  {friendly}")
            print(f"    ID: {entity.entity_id}")
            print(f"    State: {state}")
            print()
    else:
        print("  ❌ None found\n")

    print("🔗 ZIGBEE DEVICES:")
    print("=" * 80)
    if zigbee_devices:
        for entity in zigbee_devices:
            state = entity.state.state if hasattr(entity.state, 'state') else 'unknown'
            attrs = entity.state.attributes if hasattr(entity.state, 'attributes') else {}
            friendly = attrs.get('friendly_name', entity.entity_id)
            device_class = attrs.get('device_class', '')
            unit = attrs.get('unit_of_measurement', '')

            print(f"  {friendly}")
            print(f"    ID: {entity.entity_id}")
            print(f"    State: {state} {unit}")
            if device_class:
                print(f"    Device Class: {device_class}")
            print()
    else:
        print("  ❌ None found\n")

    print(f"\n📊 SUMMARY:")
    print("=" * 80)
    print(f"  Total entities in HA: {len(all_entities)}")
    print(f"  Temperature-related: {len(temp_related)}")
    print(f"  Humidity-related: {len(humid_related)}")
    print(f"  Climate entities: {len(climate_related)}")
    print(f"  Zigbee devices: {len(zigbee_devices)}")
    print()

if __name__ == '__main__':
    main()
