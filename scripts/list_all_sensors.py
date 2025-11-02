#!/usr/bin/env python3
"""List ALL sensor entities to see what's configured"""

import logging
from ha_core.client import HomeAssistantInspector
from ha_core.config import load_credentials

# Suppress logs for cleaner output
logging.basicConfig(level=logging.WARNING)

def main():
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token)

    print("\n📋 ALL SENSOR ENTITIES:")
    print("=" * 80)

    all_sensors = inspector.get_entities_by_domain('sensor')

    for sensor in sorted(all_sensors, key=lambda s: s.entity_id):
        state = sensor.state.state if hasattr(sensor.state, 'state') else 'unknown'
        attrs = sensor.state.attributes if hasattr(sensor.state, 'attributes') else {}

        device_class = attrs.get('device_class', '')
        unit = attrs.get('unit_of_measurement', '')
        friendly_name = attrs.get('friendly_name', sensor.entity_id)

        # Check for interesting attributes
        is_zigbee = 'zigbee' in str(attrs).lower() or 'zigbee' in sensor.entity_id.lower()

        # Highlight temp/humidity by device class
        markers = []
        if device_class == 'temperature':
            markers.append('🌡️ TEMP')
        if device_class == 'humidity':
            markers.append('💧 HUMID')
        if is_zigbee:
            markers.append('🔗 ZIGBEE')

        marker_str = ' '.join(markers) if markers else ''

        print(f"\n{friendly_name} {marker_str}")
        print(f"  ID: {sensor.entity_id}")
        print(f"  State: {state} {unit}")
        if device_class:
            print(f"  Device Class: {device_class}")

    print(f"\n\n📊 Total sensors: {len(all_sensors)}\n")

if __name__ == '__main__':
    main()
