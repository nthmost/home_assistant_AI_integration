#!/usr/bin/env python3
"""
Monitor Jarvis button and Abigail soil sensor.

Shows current status and readings from newly added Zigbee devices.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ha_core.client import HomeAssistantInspector
from ha_core.config import load_credentials
from ha_core.exceptions import EntityNotFoundError, APIError

# Configure logging
logging.basicConfig(level=logging.WARNING)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def find_device_entities(inspector, search_term: str):
    """Find all entities related to a device."""
    search_lower = search_term.lower()
    entities = []

    all_entities_dict = inspector.entities

    for domain, group in all_entities_dict.items():
        for entity_id, entity in group.entities.items():
            attrs = entity.state.attributes if entity.state else {}
            friendly_name = attrs.get('friendly_name', '')

            if search_lower in entity_id.lower() or search_lower in friendly_name.lower():
                entities.append({
                    'entity_id': entity_id,
                    'domain': domain,
                    'friendly_name': friendly_name,
                    'state': entity.state.state if entity.state else 'unknown',
                    'attributes': attrs,
                    'entity': entity
                })

    return entities


def display_device_status(device_name: str, entities: list):
    """Display formatted status for a device."""
    if not entities:
        print(f"❌ No entities found for '{device_name}'\n")
        print("💡 Possible reasons:")
        print("   • Device not yet paired with Home Assistant")
        print("   • Device paired but not fully configured")
        print("   • Device uses different naming")
        print("   • Device needs to be woken up or reset\n")
        return

    print(f"🔌 {device_name} - {len(entities)} entit{'y' if len(entities) == 1 else 'ies'} found")
    print("-" * 80)

    # Group by domain
    by_domain = {}
    for e in entities:
        domain = e['domain']
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(e)

    # Display by domain
    for domain in sorted(by_domain.keys()):
        domain_entities = by_domain[domain]
        print(f"\n📂 {domain.upper()} ({len(domain_entities)})")

        for e in domain_entities:
            print(f"\n   • {e['entity_id']}")
            print(f"     Name: {e['friendly_name']}")
            print(f"     State: {e['state']}")

            # Show important attributes
            attrs = e['attributes']
            important = [
                'device_class', 'unit_of_measurement', 'state_class',
                'battery', 'battery_voltage', 'temperature',
                'moisture', 'humidity', 'conductivity',
                'illuminance', 'linkquality', 'last_seen'
            ]

            for key in important:
                if key in attrs and attrs[key] is not None:
                    value = attrs[key]
                    print(f"     {key.replace('_', ' ').title()}: {value}")

            # Show options for select entities
            if 'options' in attrs:
                print(f"     Options: {attrs['options']}")

    print()


def check_sensor_health(entities: list):
    """Analyze sensor health and provide diagnostics."""
    print("\n🔍 DIAGNOSTICS:")
    print("-" * 80)

    # Check for battery
    battery_entities = [e for e in entities if 'battery' in e['entity_id'] and e['domain'] == 'sensor']
    if battery_entities:
        for e in battery_entities:
            battery_level = float(e['state']) if e['state'] != 'unknown' else None
            if battery_level is not None:
                if battery_level > 20:
                    status = "✅ GOOD"
                elif battery_level > 10:
                    status = "⚠️  LOW"
                else:
                    status = "❌ CRITICAL"
                print(f"Battery: {battery_level}% {status}")
            else:
                print("Battery: Unknown")

    # Check for actual sensors (not battery, not firmware, not button/select)
    sensor_entities = [e for e in entities
                      if e['domain'] == 'sensor'
                      and 'battery' not in e['entity_id']
                      and 'firmware' not in e['entity_id']]

    if sensor_entities:
        print(f"Active Sensors: {len(sensor_entities)}")
        for e in sensor_entities:
            device_class = e['attributes'].get('device_class', 'unknown')
            print(f"  • {device_class}: {e['state']} {e['attributes'].get('unit_of_measurement', '')}")
    else:
        print("Active Sensors: None found")
        print("⚠️  This device might:")
        print("   • Need to wake up and send initial readings")
        print("   • Require configuration in ZHA settings")
        print("   • Take time to initialize after pairing")

    # Check link quality
    linkquality_found = False
    for e in entities:
        lq = e['attributes'].get('linkquality')
        if lq is not None:
            linkquality_found = True
            if lq > 200:
                status = "✅ EXCELLENT"
            elif lq > 150:
                status = "✅ GOOD"
            elif lq > 100:
                status = "⚠️  FAIR"
            else:
                status = "❌ POOR"
            print(f"Link Quality: {lq} {status}")
            break

    if not linkquality_found:
        print("Link Quality: Not available")

    print()


def main():
    """Main monitoring function."""
    print(f"\n🏠 New Zigbee Sensor Monitor")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load credentials and connect
    try:
        url, token = load_credentials()
        inspector = HomeAssistantInspector(url, token, log_level=logging.WARNING)
    except Exception as e:
        print(f"\n❌ Failed to connect to Home Assistant: {e}\n")
        sys.exit(1)

    # Monitor Jarvis Button
    print_section("JARVIS BUTTON")
    jarvis_entities = find_device_entities(inspector, "jarvis")
    display_device_status("Jarvis Button", jarvis_entities)
    if jarvis_entities:
        check_sensor_health(jarvis_entities)

    # Monitor Abigail Soil Sensor
    print_section("ABIGAIL SOIL SENSOR")
    abigail_entities = find_device_entities(inspector, "abigail")
    if not abigail_entities:
        # Try searching for "soil" more broadly
        print("🔍 Searching more broadly for 'soil' entities...")
        abigail_entities = find_device_entities(inspector, "soil")

    display_device_status("Abigail Soil Sensor", abigail_entities)
    if abigail_entities:
        check_sensor_health(abigail_entities)

    # Summary
    print_section("SUMMARY")
    total_entities = len(jarvis_entities) + len(abigail_entities)
    print(f"📊 Total entities monitored: {total_entities}")
    print(f"   • Jarvis Button: {len(jarvis_entities)} entities")
    print(f"   • Abigail Soil Sensor: {len(abigail_entities)} entities")
    print()

    if not abigail_entities or len(abigail_entities) == 1:
        print("💡 TROUBLESHOOTING ABIGAIL:")
        print("   1. Check if device is awake (soil sensors often sleep to save battery)")
        print("   2. In Home Assistant: Configuration → Devices → Find 'Soil quality Abigail'")
        print("   3. Click 'Reconfigure' or check device page for sensor entities")
        print("   4. The device may need time to send first readings after pairing")
        print("   5. Try triggering a reading by touching/moving the sensor")
        print()


if __name__ == '__main__':
    main()
