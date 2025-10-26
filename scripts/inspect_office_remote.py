#!/usr/bin/env python3
"""
Inspect the office_lights remote entity and its learned commands
"""

import logging
from ha_core import HomeAssistantInspector, load_credentials

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def inspect_remote():
    """Inspect the remote.office_lights entity"""
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=40)

    logger.info("🔍 Inspecting remote.office_lights...")
    logger.info("=" * 60)

    # Get the entity
    entity = inspector.client.get_entity(entity_id="remote.office_lights")

    if not entity:
        logger.error("❌ remote.office_lights not found!")
        return

    logger.info(f"\n📊 ENTITY STATE:")
    logger.info(f"   State: {entity.state.state}")
    logger.info(f"   Last changed: {entity.state.last_changed}")
    logger.info(f"   Last updated: {entity.state.last_updated}")

    # Check attributes for learned commands
    if hasattr(entity.state, 'attributes'):
        attrs = entity.state.attributes

        logger.info(f"\n🏷️  ATTRIBUTES:")
        for key, value in sorted(attrs.items()):
            logger.info(f"   {key}: {value}")

        # Look for activity list or command list
        if 'activity_list' in attrs:
            logger.info(f"\n🎮 ACTIVITIES:")
            for activity in attrs['activity_list']:
                logger.info(f"   • {activity}")

        if 'command_list' in attrs:
            logger.info(f"\n📋 LEARNED COMMANDS:")
            for command in attrs['command_list']:
                logger.info(f"   • {command}")

    logger.info("\n" + "=" * 60)
    logger.info("💡 NEXT STEPS:")
    logger.info("")
    logger.info("If you see learned commands above, test them with:")
    logger.info("  python test_office_command.py <command_name>")
    logger.info("")
    logger.info("For example:")
    logger.info("  python test_office_command.py Off")
    logger.info("  python test_office_command.py On")
    logger.info("  python test_office_command.py Light+")
    logger.info("")
    logger.info("If NO commands are listed, check your HA configuration for")
    logger.info("where the Broadlink learned commands are stored.")


if __name__ == "__main__":
    inspect_remote()
