#!/usr/bin/env python3
"""
Check what Broadlink devices exist and what commands they have
"""

import logging
import requests
from ha_core import load_credentials

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def check_broadlink_devices():
    """Check Broadlink integration status and available devices"""
    url, token = load_credentials()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    logger.info("🔍 Checking Broadlink integration...")
    logger.info("=" * 60)

    # Get all states to find remote entities
    try:
        response = requests.get(
            f"{url}/api/states",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        states = response.json()

        # Find remote entities
        remotes = [s for s in states if s['entity_id'].startswith('remote.')]

        for remote in remotes:
            entity_id = remote['entity_id']
            logger.info(f"\n{'='*60}")
            logger.info(f"🔌 {entity_id}")
            logger.info(f"   State: {remote['state']}")
            logger.info(f"   Friendly name: {remote['attributes'].get('friendly_name', 'N/A')}")

            # Check for any command-related attributes
            attrs = remote['attributes']

            # Look for activity list
            if 'activity_list' in attrs:
                logger.info(f"\n   📋 Activities available:")
                for activity in attrs['activity_list']:
                    logger.info(f"      • {activity}")

            # Check for other relevant attributes
            logger.info(f"\n   🏷️  All attributes:")
            for key in sorted(attrs.keys()):
                if key not in ['friendly_name']:
                    value = attrs[key]
                    if isinstance(value, list) and len(value) > 5:
                        logger.info(f"      {key}: [{len(value)} items]")
                    else:
                        logger.info(f"      {key}: {value}")

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed: {e}")

    logger.info("\n" + "=" * 60)
    logger.info("🧪 NEXT STEP: Test if learned codes exist")
    logger.info("")
    logger.info("Try learning a NEW command to verify Broadlink is working:")
    logger.info("  1. Go to HA → Developer Tools → Services")
    logger.info("  2. Service: remote.learn_command")
    logger.info("  3. Target: remote.office_ir")
    logger.info("  4. Service Data:")
    logger.info("     device: Office Lights")
    logger.info("     command: TestButton")
    logger.info("     command_type: ir")
    logger.info("     timeout: 20")
    logger.info("  5. Click Call Service")
    logger.info("  6. Point your physical LED remote at Broadlink")
    logger.info("  7. Press any button within 20 seconds")
    logger.info("")
    logger.info("If learning WORKS → Old codes are gone, need to re-learn")
    logger.info("If learning FAILS → Broadlink device communication problem")


if __name__ == "__main__":
    check_broadlink_devices()
