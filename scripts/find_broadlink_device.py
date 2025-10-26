#!/usr/bin/env python3
"""
Find the Broadlink device in Home Assistant's device registry
"""

import logging
import requests
from ha_core import load_credentials

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def find_broadlink_device():
    """Search for Broadlink devices and check their connection status"""
    url, token = load_credentials()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    logger.info("🔍 Searching for Broadlink devices in Home Assistant...")
    logger.info("=" * 60)

    # Get all states
    try:
        response = requests.get(
            f"{url}/api/states",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        states = response.json()

        # Find all remote entities
        remotes = [s for s in states if s['entity_id'].startswith('remote.')]
        logger.info(f"\n📡 Found {len(remotes)} remote entities:")

        for remote in remotes:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔌 {remote['entity_id']}")
            logger.info(f"   Name: {remote['attributes'].get('friendly_name', 'N/A')}")
            logger.info(f"   State: {remote['state']}")
            logger.info(f"   Last changed: {remote.get('last_changed', 'N/A')}")
            logger.info(f"   Last updated: {remote.get('last_updated', 'N/A')}")

            # Check for device-related attributes
            attrs = remote['attributes']

            if 'supported_features' in attrs:
                logger.info(f"   Supported features: {attrs['supported_features']}")

            # Look for activity list or any commands
            if 'activity_list' in attrs:
                logger.info(f"   Activities: {attrs['activity_list']}")

            # Check all attributes for clues
            logger.info(f"\n   All attributes:")
            for key, value in sorted(attrs.items()):
                if key not in ['friendly_name']:
                    logger.info(f"      {key}: {value}")

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to fetch states: {e}")
        return

    # Check for Broadlink integration
    logger.info("\n" + "=" * 60)
    logger.info("🔍 Checking for Broadlink integration...")

    # Look for any entities with 'broadlink' in the name
    broadlink_entities = [s for s in states if 'broadlink' in s['entity_id'].lower() or
                         'broadlink' in s['attributes'].get('friendly_name', '').lower()]

    if broadlink_entities:
        logger.info(f"\n   Found {len(broadlink_entities)} Broadlink-related entities:")
        for entity in broadlink_entities:
            logger.info(f"   • {entity['entity_id']} - {entity['attributes'].get('friendly_name', 'N/A')}")
    else:
        logger.info("   ❌ No entities with 'broadlink' in the name found")

    logger.info("\n" + "=" * 60)
    logger.info("💡 DIAGNOSIS:")
    logger.info("")
    logger.info("If remote.office_lights exists but has NO learned commands visible:")
    logger.info("   → The HA Broadlink integration is disconnected from the device")
    logger.info("")
    logger.info("To fix:")
    logger.info("   1. Go to HA → Settings → Devices & Services")
    logger.info("   2. Look for 'Broadlink' integration")
    logger.info("   3. Check if the device is showing as 'Unavailable' or 'Not responding'")
    logger.info("   4. Try 'Reload' or 'Reconfigure' the integration")
    logger.info("   5. You may need to re-discover the Broadlink device on your network")
    logger.info("")
    logger.info("Alternative: If Alexa works but HA doesn't:")
    logger.info("   → The Broadlink may have changed IP addresses")
    logger.info("   → Check your router and assign a static IP to the Broadlink")
    logger.info("   → Re-add the Broadlink integration with the correct IP")


if __name__ == "__main__":
    find_broadlink_device()
