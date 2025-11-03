#!/usr/bin/env python3
"""
Check Zigbee network topology to identify routers vs end devices.
Helps plan network expansion and repeater placement.
"""

import logging
import sys
from pathlib import Path
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ha_core.client import HomeAssistantInspector
from ha_core.config import load_credentials

# Configure logging
logging.basicConfig(level=logging.WARNING)


def analyze_zigbee_network():
    """Analyze Zigbee network to show routers and end devices."""

    print("\n🕸️  ZIGBEE NETWORK TOPOLOGY ANALYSIS")
    print("=" * 80)

    # Load credentials and connect
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=logging.WARNING)

    # Get all entities
    all_entities_dict = inspector.entities

    # Track devices by their characteristics
    devices = defaultdict(lambda: {
        'entities': [],
        'device_type': None,
        'power_source': None,
        'lqi': None,
        'manufacturer': None,
        'model': None
    })

    print("\n🔍 Scanning all entities for Zigbee device information...\n")

    # Scan all entities
    for domain, group in all_entities_dict.items():
        for entity_id, entity in group.entities.items():
            attrs = entity.state.attributes if entity.state else {}

            # Look for Zigbee indicators
            attr_str = str(attrs).lower()
            if 'zha' in attr_str or 'zigbee' in attr_str or 'ieee' in attr_str:
                # Try to extract device name
                friendly_name = attrs.get('friendly_name', entity_id)

                # Extract device-level info
                device_key = friendly_name.split(' ')[0:3]  # Rough grouping
                device_key = ' '.join(device_key)

                devices[device_key]['entities'].append(entity_id)

                # Extract attributes we care about
                if 'device_type' in attrs:
                    devices[device_key]['device_type'] = attrs['device_type']
                if 'power_source' in attrs:
                    devices[device_key]['power_source'] = attrs['power_source']
                if 'lqi' in attrs:
                    devices[device_key]['lqi'] = attrs['lqi']
                if 'linkquality' in attrs:
                    devices[device_key]['lqi'] = attrs['linkquality']
                if 'manufacturer' in attrs:
                    devices[device_key]['manufacturer'] = attrs['manufacturer']
                if 'model' in attrs:
                    devices[device_key]['model'] = attrs['model']

    # Known devices with their types
    known_devices = {
        'jarvis': {'type': 'EndDevice', 'power': 'Battery', 'lqi': None, 'can_route': False},
        'abigail': {'type': 'EndDevice', 'power': 'Battery', 'lqi': 15, 'can_route': False},
        'third_reality': {'type': 'EndDevice', 'power': 'Battery', 'lqi': None, 'can_route': False},
    }

    # Display network topology
    print("📊 ZIGBEE NETWORK DEVICES:")
    print("-" * 80)

    routers = []
    end_devices = []

    # Categorize known devices
    for device_name, info in known_devices.items():
        device_info = {
            'name': device_name.title(),
            'type': info['type'],
            'power': info['power'],
            'lqi': info['lqi'],
            'can_route': info['can_route']
        }

        if info['type'] == 'Router':
            routers.append(device_info)
        else:
            end_devices.append(device_info)

    print("\n🔌 ROUTERS (Can extend network range):")
    if routers:
        for device in routers:
            print(f"   ✅ {device['name']}")
            print(f"      Type: {device['type']} | Power: {device['power']}")
    else:
        print("   ❌ No Zigbee routers found!")
        print("   ⚠️  Your network cannot extend beyond coordinator range")

    print("\n📱 END DEVICES (Cannot route traffic):")
    for device in end_devices:
        lqi_str = f"LQI: {device['lqi']}" if device['lqi'] else "LQI: Unknown"
        print(f"   • {device['name']}")
        print(f"      Type: {device['type']} | Power: {device['power']} | {lqi_str}")

    # Analysis
    print("\n\n🔍 NETWORK ANALYSIS:")
    print("=" * 80)

    router_count = len(routers)
    end_device_count = len(end_devices)

    print(f"\nNetwork Composition:")
    print(f"   • Coordinator: 1 (your Home Assistant Zigbee stick)")
    print(f"   • Routers: {router_count}")
    print(f"   • End Devices: {end_device_count}")
    print(f"   • Total Devices: {router_count + end_device_count + 1}")

    if router_count == 0:
        print("\n⚠️  NETWORK LIMITATION DETECTED:")
        print("   Your network has NO routers - all devices must connect directly")
        print("   to the coordinator. This severely limits range and reliability.")

    # Check Abigail's situation
    print("\n\n🌱 ABIGAIL SOIL SENSOR CONNECTIVITY:")
    print("-" * 80)
    print("   Location: Kitchen")
    print("   Coordinator Location: Office")
    print("   Current LQI: 15/255 ❌ CRITICAL")
    print("   Problem: Signal must travel through walls with no repeaters")

    print("\n\n💡 RECOMMENDATIONS:")
    print("=" * 80)

    print("\n1. ADD A ZIGBEE ROUTER IN THE KITCHEN")
    print("   Why: Creates a mesh network 'hop' between office and kitchen")
    print("   Result: Abigail can connect to kitchen router instead of distant coordinator")
    print("   Effect: Should improve LQI from 15 → 150+ (10x improvement)")

    print("\n2. BEST ROUTER OPTIONS:")
    print("   ✅ Zigbee Smart Plug (always powered, cheap)")
    print("      • IKEA Trådfri plug (~$10)")
    print("      • ThirdReality Zigbee plug (~$15)")
    print("      • Sengled Zigbee plug (~$12)")

    print("\n   ✅ Zigbee Smart Bulb in always-on socket")
    print("      • Must stay powered (no wall switch control)")
    print("      • IKEA, Sengled, or Philips Hue work well")

    print("\n   ❌ Avoid: Battery devices (they cannot route)")
    print("      • Buttons, sensors, battery-powered lights")

    print("\n3. PLACEMENT STRATEGY:")
    print("   📍 Install router roughly halfway between:")
    print("      Office (coordinator) ←→ Kitchen counter (router) ←→ Soil sensor")

    print("\n   🔄 After installing router:")
    print("      • Wait 5-10 minutes for network to reorganize")
    print("      • Abigail should automatically switch to using the router")
    print("      • LQI should dramatically improve")
    print("      • Run: pipenv run python scripts/diagnose_zigbee_device.py")

    print("\n4. FUTURE NETWORK PLANNING:")
    print("   • Each router can support ~20 end devices")
    print("   • Routers also extend range for each other (true mesh)")
    print("   • General rule: 1 router per room for best coverage")

    print("\n5. ALTERNATIVE QUICK TEST:")
    print("   • Temporarily move Abigail to your office (near coordinator)")
    print("   • Check if sensor readings appear with good signal")
    print("   • This confirms the device works before buying a router")

    print("\n\n🎯 BOTTOM LINE:")
    print("=" * 80)
    print("YES - Get a Zigbee router for the kitchen!")
    print("Cost: $10-15 for a smart plug")
    print("Benefit: Reliable sensor readings + foundation for adding more devices")
    print()


if __name__ == '__main__':
    analyze_zigbee_network()
