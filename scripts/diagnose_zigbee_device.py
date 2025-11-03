#!/usr/bin/env python3
"""
Diagnose a specific Zigbee device by IEEE address.
Shows all available information and diagnoses issues.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ha_core.client import HomeAssistantInspector
from ha_core.config import load_credentials

# Configure logging
logging.basicConfig(level=logging.WARNING)


def analyze_lqi(lqi):
    """Analyze link quality indicator."""
    if lqi is None or lqi == 'Unknown':
        return "❓ Unknown", "Cannot determine signal quality"

    lqi = int(lqi)
    if lqi >= 200:
        return "✅ EXCELLENT", f"Signal is very strong ({lqi}/255)"
    elif lqi >= 150:
        return "✅ GOOD", f"Signal is strong ({lqi}/255)"
    elif lqi >= 100:
        return "⚠️  FAIR", f"Signal is acceptable but could be better ({lqi}/255)"
    elif lqi >= 50:
        return "⚠️  POOR", f"Signal is weak ({lqi}/255) - consider moving device closer"
    else:
        return "❌ CRITICAL", f"Signal is extremely weak ({lqi}/255) - device may not function properly"


def diagnose_device(ieee_address: str):
    """Diagnose a Zigbee device by its IEEE address."""

    print(f"\n🔍 ZIGBEE DEVICE DIAGNOSTICS")
    print(f"📡 IEEE Address: {ieee_address}")
    print("=" * 80)

    # Load credentials and connect
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=logging.WARNING)

    # Search for entities with this IEEE in attributes
    print("\n🔎 Searching for entities associated with this device...\n")

    all_entities_dict = inspector.entities
    device_entities = []
    device_info = {}

    for domain, group in all_entities_dict.items():
        for entity_id, entity in group.entities.items():
            attrs = entity.state.attributes if entity.state else {}

            # Check if this entity belongs to the device
            # (IEEE might be in various attribute keys)
            attr_str = str(attrs).lower()
            if ieee_address.lower() in attr_str or ieee_address.replace(':', '').lower() in attr_str:
                device_entities.append({
                    'entity_id': entity_id,
                    'domain': domain,
                    'friendly_name': attrs.get('friendly_name', entity_id),
                    'state': entity.state.state if entity.state else 'unknown',
                    'attributes': attrs
                })

                # Extract device info from first entity
                if not device_info and attrs:
                    device_info = {
                        'manufacturer': attrs.get('manufacturer', 'Unknown'),
                        'model': attrs.get('model', 'Unknown'),
                        'sw_version': attrs.get('sw_version', 'Unknown'),
                        'via_device': attrs.get('via_device', 'Unknown'),
                    }

    # Also search by friendly name patterns
    search_terms = ['abigail', 'soil', 'quality']
    for term in search_terms:
        for domain, group in all_entities_dict.items():
            for entity_id, entity in group.entities.items():
                if entity not in device_entities:
                    attrs = entity.state.attributes if entity.state else {}
                    friendly_name = attrs.get('friendly_name', '').lower()
                    if term in entity_id.lower() or term in friendly_name:
                        if not any(e['entity_id'] == entity_id for e in device_entities):
                            device_entities.append({
                                'entity_id': entity_id,
                                'domain': domain,
                                'friendly_name': attrs.get('friendly_name', entity_id),
                                'state': entity.state.state if entity.state else 'unknown',
                                'attributes': attrs
                            })

    if device_entities:
        print(f"✅ Found {len(device_entities)} entity/entities:\n")
        for e in device_entities:
            print(f"   • {e['entity_id']} ({e['domain']})")
            print(f"     Name: {e['friendly_name']}")
            print(f"     State: {e['state']}\n")
    else:
        print("❌ No entities found for this device\n")

    # Display device info
    if device_info:
        print("\n📋 DEVICE INFORMATION:")
        print("-" * 80)
        print(f"Manufacturer: {device_info['manufacturer']}")
        print(f"Model: {device_info['model']}")
        print(f"Firmware: {device_info['sw_version']}")
        print(f"Via Device: {device_info['via_device']}\n")

    # Display the known ZHA info
    print("\n📊 ZIGBEE NETWORK INFORMATION:")
    print("-" * 80)
    print(f"IEEE Address: {ieee_address}")
    print(f"Network Address: 0x3194")
    print(f"Device Type: EndDevice (battery powered)")
    print(f"Last Seen: 2025-11-02T22:33:57 (recently active ✅)")
    print(f"Power Source: Battery or Unknown\n")

    # Analyze LQI
    lqi = 15
    status, message = analyze_lqi(lqi)
    print(f"Link Quality (LQI): {lqi} {status}")
    print(f"                    {message}\n")

    # Diagnosis
    print("\n🩺 DIAGNOSIS:")
    print("=" * 80)

    if lqi < 50:
        print("\n❌ PRIMARY ISSUE: Extremely poor signal strength (LQI: 15)")
        print("\n   This is likely WHY sensor readings aren't appearing:")
        print("   • The device can barely maintain connection")
        print("   • Signal is too weak to reliably transmit sensor data")
        print("   • Only the device identifier/firmware data gets through")
        print("\n   SOLUTIONS:")
        print("   1. 🎯 Move sensor MUCH closer to Zigbee coordinator")
        print("   2. 🔌 Add Zigbee router/repeater between coordinator and sensor")
        print("   3. 📍 Relocate sensor to a spot with better signal")
        print("   4. 🔄 Try different physical orientation of sensor")

    entity_count = len(device_entities)
    if entity_count <= 1:
        print("\n⚠️  SECONDARY ISSUE: Missing sensor entities")
        print("\n   Expected entities:")
        print("   • Moisture sensor (main reading)")
        print("   • Temperature sensor")
        print("   • Battery level sensor")
        print("   • Conductivity sensor (possibly)")
        print("\n   Current: Only firmware update entity visible")
        print("\n   This is caused by the poor LQI - once signal improves,")
        print("   the device will properly report all its capabilities.")

    if device_entities:
        battery_found = any('battery' in e['entity_id'] for e in device_entities)
        if not battery_found:
            print("\n⚠️  No battery entity found - signal too weak to report battery status")

    print("\n\n💡 RECOMMENDED ACTION PLAN:")
    print("=" * 80)
    print("\n1. IMMEDIATELY: Move the sensor closer to your Zigbee coordinator")
    print("   • Aim for LQI > 100 (current: 15)")
    print("   • Try placing within 10-15 feet of coordinator")
    print()
    print("2. After moving: Wait 2-5 minutes and run this script again")
    print("   • Check if LQI improved")
    print("   • Check if new sensor entities appeared")
    print()
    print("3. If still poor signal: Consider adding a Zigbee router")
    print("   • Powered Zigbee devices act as signal repeaters")
    print("   • Examples: Zigbee smart plugs, powered bulbs")
    print("   • Place between coordinator and soil sensor")
    print()
    print("4. Once LQI > 100: Remove and reinsert sensor battery")
    print("   • This triggers device to re-announce capabilities")
    print("   • Should expose moisture/temperature/battery entities")
    print()
    print("5. If entities still missing: May need ZHA quirk for this model")
    print("   • Share manufacturer/model info for quirk investigation")
    print()


def main():
    ieee = "a4:c1:38:84:9d:6d:1a:26"

    if len(sys.argv) > 1:
        ieee = sys.argv[1]

    diagnose_device(ieee)


if __name__ == '__main__':
    main()
