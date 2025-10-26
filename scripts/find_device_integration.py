#!/usr/bin/env python3
"""
Find the integration for a device by inspecting state and context

This uses the HA REST API directly to get state information.
"""

import sys
import logging
import requests
from ha_core import load_credentials

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def find_integration(entity_id: str):
    """Find the integration controlling an entity"""
    url, token = load_credentials()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    logger.info(f"🔍 Finding integration for: {entity_id}")
    logger.info("=" * 60)

    # Get state to see all available attributes
    logger.info(f"\n📊 Querying state API...")
    try:
        response = requests.get(
            f"{url}/api/states/{entity_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        state_data = response.json()

        logger.info(f"✅ Got state data")
        logger.info(f"\n📋 FULL STATE OBJECT:")
        logger.info(f"   Entity ID: {state_data.get('entity_id')}")
        logger.info(f"   State: {state_data.get('state')}")
        logger.info(f"   Last changed: {state_data.get('last_changed')}")
        logger.info(f"   Last updated: {state_data.get('last_updated')}")

        context = state_data.get('context', {})
        logger.info(f"\n🔍 CONTEXT:")
        for key, value in context.items():
            logger.info(f"   {key}: {value}")

        attributes = state_data.get('attributes', {})
        logger.info(f"\n🏷️  ATTRIBUTES:")
        for key, value in sorted(attributes.items()):
            logger.info(f"   {key}: {value}")

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ State API request failed: {e}")
        return

    # Try to infer integration from entity_id pattern
    logger.info(f"\n🔍 ENTITY ID ANALYSIS:")
    entity_parts = entity_id.split('.')
    domain = entity_parts[0]
    name = '.'.join(entity_parts[1:])

    logger.info(f"   Domain: {domain}")
    logger.info(f"   Name: {name}")

    # Common integration patterns
    if 'govee' in name.lower():
        logger.info(f"   💡 Likely integration: Govee")
    elif 'tuya' in name.lower() or 'smart_life' in name.lower():
        logger.info(f"   💡 Likely integration: Tuya/Smart Life")
    elif 'hue' in name.lower():
        logger.info(f"   💡 Likely integration: Philips Hue")
    elif 'zigbee' in name.lower():
        logger.info(f"   💡 Likely integration: Zigbee")
    else:
        logger.info(f"   ❓ Cannot infer integration from name")

    logger.info("\n" + "=" * 60)
    logger.info("🏁 Complete")
    logger.info("\n💡 TIP: Check Home Assistant UI → Settings → Devices & Services")
    logger.info("   Search for 'Tube Lamp' to see which integration it belongs to")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 find_device_integration.py <entity_id>")
        print("Example: python3 find_device_integration.py light.tube_lamp")
        sys.exit(1)

    entity_id = sys.argv[1]
    find_integration(entity_id)
