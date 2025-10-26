#!/usr/bin/env python3
"""
Explore all entities to understand their structure and find Zigbee indicators.
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


def main():
    """Explore entities and their attributes."""

    logger.info("🔍 Exploring all Home Assistant entities...\n")

    # Load credentials and connect
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=logging.WARNING)

    # Get all entities
    all_entities_dict = inspector.entities

    # Show domain summary first
    logger.info("📊 Domain Summary:")
    logger.info("=" * 80)
    for domain, group in sorted(all_entities_dict.items()):
        count = len(group.entities)
        logger.info(f"  {domain:20s}: {count:4d} entities")
    logger.info("=" * 80)

    # Sample a few entities from each domain to see their attributes
    logger.info("\n🔬 Sample entity attributes (first 2 per domain):\n")

    for domain, group in sorted(all_entities_dict.items()):
        logger.info(f"\n{'='*80}")
        logger.info(f"Domain: {domain}")
        logger.info(f"{'='*80}")

        # Look at first 2 entities in this domain
        for i, (entity_id, entity) in enumerate(group.entities.items()):
            if i >= 2:  # Only show first 2
                break

            logger.info(f"\n  Entity: {entity_id}")
            logger.info(f"  State: {entity.state.state if entity.state else 'N/A'}")

            if entity.state and entity.state.attributes:
                attrs = entity.state.attributes
                logger.info(f"  Attributes:")

                # Show key attributes that might indicate Zigbee
                key_attrs = [
                    'friendly_name',
                    'attribution',
                    'via_device',
                    'device_id',
                    'integration',
                    'platform',
                    'device_class',
                    'supported_features',
                ]

                for key in key_attrs:
                    if key in attrs:
                        value = attrs[key]
                        logger.info(f"    {key}: {value}")

                # Show all attributes if there aren't too many
                if len(attrs) <= 15:
                    logger.info(f"  All attributes:")
                    for key, value in sorted(attrs.items()):
                        if key not in key_attrs:
                            # Truncate long values
                            value_str = str(value)
                            if len(value_str) > 100:
                                value_str = value_str[:100] + "..."
                            logger.info(f"    {key}: {value_str}")

    logger.info("\n" + "=" * 80)
    logger.info("✅ Exploration complete\n")


if __name__ == '__main__':
    main()
