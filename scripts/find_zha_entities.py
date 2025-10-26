#!/usr/bin/env python3
"""
Find ZHA entities by examining all entity attributes for ZHA indicators.
"""

import logging
import sys
import json
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


def has_zha_indicator(attributes: dict) -> bool:
    """Check if entity attributes indicate ZHA/Zigbee."""
    if not attributes:
        return False

    # Convert all values to strings for searching
    attr_str = json.dumps(attributes, default=str).lower()

    # Search for ZHA/Zigbee indicators
    indicators = ['zha', 'zigbee', 'ieee']

    return any(indicator in attr_str for indicator in indicators)


def main():
    """Find all ZHA entities."""

    logger.info("🔍 Searching for ZHA/Zigbee entities in all attributes...\n")

    # Load credentials and connect
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=logging.WARNING)

    # Get all entities
    all_entities_dict = inspector.entities

    # Find entities with ZHA indicators
    zha_entities = []

    for domain, group in all_entities_dict.items():
        for entity_id, entity in group.entities.items():
            attributes = entity.state.attributes if entity.state else {}

            if has_zha_indicator(attributes):
                zha_entities.append((entity_id, entity, attributes))

    if not zha_entities:
        logger.warning("⚠️  No ZHA/Zigbee entities found.")
        logger.info("\n💡 ZHA is installed but no devices seem to be paired.")
        logger.info("   Try pairing a Zigbee device first in Home Assistant.")
        return

    logger.info(f"📋 Found {len(zha_entities)} ZHA/Zigbee entities:\n")
    logger.info("=" * 80)

    # Group by device (based on friendly name prefix)
    devices = {}
    for entity_id, entity, attributes in zha_entities:
        # Try to extract device name
        friendly_name = attributes.get('friendly_name', entity_id)

        # Find ZHA-specific attributes
        zha_attrs = {}
        for key, value in attributes.items():
            key_lower = key.lower()
            value_str = str(value).lower()
            if 'zha' in key_lower or 'zha' in value_str or 'zigbee' in key_lower or 'zigbee' in value_str or 'ieee' in key_lower:
                zha_attrs[key] = value

        device_name = friendly_name.split(' ')[0] if ' ' in friendly_name else friendly_name
        if device_name not in devices:
            devices[device_name] = []
        devices[device_name].append((entity_id, entity, attributes, zha_attrs))

    # Display findings
    for device_name, entities in sorted(devices.items()):
        logger.info(f"\n🔌 {device_name}")
        logger.info("-" * 80)

        for entity_id, entity, attributes, zha_attrs in entities:
            state = entity.state.state if entity.state else 'N/A'
            domain = entity_id.split('.')[0]
            friendly_name = attributes.get('friendly_name', entity_id)

            logger.info(f"   • {entity_id}")
            logger.info(f"     └─ Domain: {domain}")
            logger.info(f"     └─ Name: {friendly_name}")
            logger.info(f"     └─ State: {state}")

            # Show ZHA-specific attributes
            if zha_attrs:
                logger.info(f"     └─ ZHA Attributes:")
                for key, value in zha_attrs.items():
                    # Truncate long values
                    value_str = str(value)
                    if len(value_str) > 80:
                        value_str = value_str[:80] + "..."
                    logger.info(f"        • {key}: {value_str}")

            # Show useful general attributes
            if 'battery_level' in attributes or 'battery' in attributes:
                battery = attributes.get('battery_level') or attributes.get('battery')
                logger.info(f"     └─ Battery: {battery}%")

            logger.info("")

    logger.info("=" * 80)
    logger.info(f"\n✅ Found {len(zha_entities)} ZHA entities across {len(devices)} devices\n")


if __name__ == '__main__':
    main()
