#!/usr/bin/env python3
"""
Turn on the office remote entity so it can send commands
"""

import logging
from ha_core import HomeAssistantInspector, load_credentials
from homeassistant_api.errors import HomeassistantAPIError

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def turn_on_remote():
    """Turn on the office remote entity"""
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=40)

    logger.info("🔌 Turning on remote entities...")
    logger.info("=" * 60)

    # Try both possible names
    entity_ids = ["remote.office_ir", "remote.office_lights"]

    for entity_id in entity_ids:
        logger.info(f"\n🔍 Trying: {entity_id}")
        try:
            # First check if it exists
            entity = inspector.client.get_entity(entity_id=entity_id)

            if entity:
                logger.info(f"   ✅ Entity exists")
                logger.info(f"   Current state: {entity.state.state}")

                # Turn it on
                logger.info(f"   📡 Calling remote.turn_on...")
                inspector.client.trigger_service(
                    domain="remote",
                    service="turn_on",
                    entity_id=entity_id
                )
                logger.info(f"   ✅ Turn on command sent!")

                # Check new state
                import time
                time.sleep(1)
                entity = inspector.client.get_entity(entity_id=entity_id)
                logger.info(f"   New state: {entity.state.state}")

        except HomeassistantAPIError as e:
            logger.warning(f"   ⚠️  Entity not found or error: {e}")
            continue
        except Exception as e:
            logger.error(f"   ❌ Unexpected error: {e}")
            continue

    logger.info("\n" + "=" * 60)
    logger.info("💡 Now try sending a command again:")
    logger.info("   python test_office_command.py Red")


if __name__ == "__main__":
    turn_on_remote()
