#!/usr/bin/env python3
"""
Inventory all Zigbee devices found on Home Assistant.
Lists device details, entities, and current states.
"""

import logging
import sys
from pathlib import Path

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


def main():
    """Discover and inventory all Zigbee devices."""

    logger.info("🔍 Discovering Zigbee devices on Home Assistant...\n")

    # Load credentials and connect
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=logging.WARNING)

    # Get all entities organized by domain
    all_entities_dict = inspector.entities

    # Find Zigbee entities (usually have 'zha' integration or zigbee-related attributes)
    zigbee_entities = []

    for domain, group in all_entities_dict.items():
        # group.entities is a dict of entity_id -> Entity
        for entity_id, entity in group.entities.items():
            attributes = entity.state.attributes if entity.state else {}

            # Check if entity is Zigbee-related
            # Common indicators: integration='zha' or platform containing zha/zigbee
            is_zigbee = False

            # Check attributes for Zigbee indicators
            if attributes:
                # Check for ZHA integration - most reliable indicator
                if attributes.get('attribution') and 'zha' in attributes.get('attribution', '').lower():
                    is_zigbee = True

                # Check for device info that might indicate Zigbee
                if 'via_device' in attributes:
                    via_device = str(attributes['via_device'])
                    if 'zha' in via_device.lower() or 'zigbee' in via_device.lower():
                        is_zigbee = True

            # Also check for ZHA in entity_id patterns
            if '_zha_' in entity_id or entity_id.startswith('zha_'):
                is_zigbee = True

            if is_zigbee:
                zigbee_entities.append(entity)

    if not zigbee_entities:
        logger.warning("⚠️  No Zigbee entities found.")
        logger.info("\n💡 Tip: Zigbee devices are typically managed by:")
        logger.info("   - ZHA (Zigbee Home Automation) integration")
        logger.info("   - Zigbee2MQTT addon")
        return

    # Group by device
    devices = {}
    for entity in zigbee_entities:
        # Try to extract device name from friendly_name or entity_id
        friendly_name = entity.state.attributes.get('friendly_name', entity.entity_id)
        device_name = friendly_name.split(' ')[0] if ' ' in friendly_name else friendly_name

        if device_name not in devices:
            devices[device_name] = []
        devices[device_name].append(entity)

    # Display inventory
    logger.info(f"📋 Found {len(zigbee_entities)} Zigbee entities across {len(devices)} devices:\n")
    logger.info("=" * 80)

    for device_name, entities in sorted(devices.items()):
        logger.info(f"\n🔌 {device_name}")
        logger.info("-" * 80)

        for entity in entities:
            state = entity.state
            entity_id = entity.entity_id
            domain = entity_id.split('.')[0]

            # Get relevant attributes
            attrs = state.attributes or {}
            friendly_name = attrs.get('friendly_name', entity_id)
            current_state = state.state

            logger.info(f"   • {entity_id}")
            logger.info(f"     └─ Type: {domain}")
            logger.info(f"     └─ Name: {friendly_name}")
            logger.info(f"     └─ State: {current_state}")

            # Show some useful attributes based on domain
            if domain == 'sensor':
                unit = attrs.get('unit_of_measurement')
                if unit:
                    logger.info(f"     └─ Unit: {unit}")
            elif domain == 'light':
                brightness = attrs.get('brightness')
                if brightness:
                    logger.info(f"     └─ Brightness: {brightness}")
            elif domain == 'binary_sensor':
                device_class = attrs.get('device_class')
                if device_class:
                    logger.info(f"     └─ Device Class: {device_class}")

            # Show battery level if available
            battery = attrs.get('battery_level') or attrs.get('battery')
            if battery:
                logger.info(f"     └─ Battery: {battery}%")

            logger.info("")

    logger.info("=" * 80)
    logger.info(f"\n✅ Inventory complete: {len(zigbee_entities)} entities from {len(devices)} devices\n")


if __name__ == '__main__':
    main()
