#!/usr/bin/env python3
"""
Comprehensive Zigbee device inventory.
Identifies ZHA devices by looking for device-level groupings.
"""

import logging
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ha_core.client import HomeAssistantInspector
from ha_core.config import load_credentials

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def extract_device_name(entity_id: str, friendly_name: str) -> str:
    """
    Extract device name from entity_id or friendly_name.
    ZHA entities often follow patterns like: manufacturer_model_function
    """
    # Remove domain prefix
    base_name = entity_id.split('.')[1] if '.' in entity_id else entity_id

    # If it ends with _firmware, _battery, _motion, etc., strip that
    suffixes = ['_firmware', '_battery', '_motion', '_temperature', '_humidity',
                '_pressure', '_illuminance', '_power', '_energy', '_voltage',
                '_current', '_status', '_level', '_alarm', '_tamper']

    for suffix in suffixes:
        if base_name.endswith(suffix):
            return base_name[:-len(suffix)]

    return base_name


def main():
    """Discover and inventory all Zigbee devices."""

    logger.info("🔍 Discovering Zigbee devices on Home Assistant...\n")

    # Load credentials and connect
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=logging.WARNING)

    # Get all entities
    all_entities_dict = inspector.entities

    # First pass: find entities with ZHA indicators
    zha_indicator_entities = set()
    for domain, group in all_entities_dict.items():
        for entity_id, entity in group.entities.items():
            attrs = entity.state.attributes if entity.state else {}
            # Check for ZHA in entity_picture or other attributes
            attr_str = str(attrs).lower()
            if 'zha' in attr_str or 'zigbee' in attr_str:
                zha_indicator_entities.add(entity_id)

    # Second pass: group entities by potential device name
    device_entities = defaultdict(list)

    for domain, group in all_entities_dict.items():
        for entity_id, entity in group.entities.items():
            attrs = entity.state.attributes if entity.state else {}
            friendly_name = attrs.get('friendly_name', entity_id)

            # Extract device name
            device_name = extract_device_name(entity_id, friendly_name)

            # Check if this entity or its device group has ZHA indicators
            is_zha = False

            # Direct ZHA indicator
            if entity_id in zha_indicator_entities:
                is_zha = True

            # Check if any entity with same device name has ZHA indicator
            for zha_entity_id in zha_indicator_entities:
                zha_device_name = extract_device_name(zha_entity_id, '')
                if device_name == zha_device_name:
                    is_zha = True
                    break

            if is_zha:
                device_entities[device_name].append((entity_id, domain, entity, attrs))

    if not device_entities:
        logger.warning("⚠️  No Zigbee devices found.")
        logger.info("\n💡 Tip: Zigbee devices are typically managed by:")
        logger.info("   - ZHA (Zigbee Home Automation) integration")
        logger.info("   - Zigbee2MQTT addon")
        return

    # Display inventory
    total_entities = sum(len(entities) for entities in device_entities.values())
    logger.info(f"📋 Found {len(device_entities)} Zigbee device(s) with {total_entities} entities:\n")
    logger.info("=" * 80)

    for device_name, entities in sorted(device_entities.items()):
        # Use the friendly name from the first entity as device display name
        display_name = entities[0][3].get('friendly_name', device_name)
        # If friendly name has the same pattern, clean it up
        for suffix in ['Firmware', 'Battery', 'Motion']:
            if display_name.endswith(f' {suffix}'):
                display_name = display_name[:-len(suffix)-1]
                break

        logger.info(f"\n🔌 {display_name}")
        logger.info("-" * 80)

        # Show device-level info if available
        has_battery = False
        battery_level = None
        has_firmware = False
        firmware_version = None

        for entity_id, domain, entity, attrs in entities:
            if domain == 'sensor' and 'battery' in entity_id.lower():
                has_battery = True
                battery_level = entity.state.state if entity.state else 'N/A'
            if domain == 'update' and 'firmware' in entity_id.lower():
                has_firmware = True
                firmware_version = attrs.get('installed_version', 'N/A')

        if has_battery:
            logger.info(f"   🔋 Battery: {battery_level}%")
        if has_firmware:
            logger.info(f"   📦 Firmware: {firmware_version}")

        logger.info(f"\n   📍 Entities ({len(entities)}):")

        for entity_id, domain, entity, attrs in sorted(entities, key=lambda x: x[0]):
            state = entity.state.state if entity.state else 'N/A'
            friendly_name = attrs.get('friendly_name', entity_id)
            device_class = attrs.get('device_class', '')

            logger.info(f"      • {entity_id}")
            logger.info(f"        └─ Type: {domain}")
            logger.info(f"        └─ Name: {friendly_name}")
            logger.info(f"        └─ State: {state}")

            if device_class:
                logger.info(f"        └─ Device Class: {device_class}")

            # Show specific attributes based on domain
            if domain == 'sensor':
                unit = attrs.get('unit_of_measurement')
                if unit:
                    logger.info(f"        └─ Unit: {unit}")
                if 'battery_voltage' in attrs:
                    logger.info(f"        └─ Voltage: {attrs['battery_voltage']} V")
            elif domain == 'update':
                if 'latest_version' in attrs:
                    logger.info(f"        └─ Latest: {attrs['latest_version']}")
                if 'auto_update' in attrs:
                    logger.info(f"        └─ Auto-update: {attrs['auto_update']}")

        logger.info("")

    logger.info("=" * 80)
    logger.info(f"\n✅ Inventory complete: {len(device_entities)} device(s), {total_entities} entities\n")


if __name__ == '__main__':
    main()
