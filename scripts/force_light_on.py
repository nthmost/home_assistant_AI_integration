#!/usr/bin/env python3
"""
Force a light on and monitor state changes

This script explicitly calls turn_on and monitors whether
the physical device responds and HA state updates.
"""

import sys
import time
import logging
from ha_core import HomeAssistantInspector, load_credentials
from homeassistant_api.errors import HomeassistantAPIError

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def force_light_on(entity_id: str):
    """
    Force a light ON and monitor state

    Args:
        entity_id: Entity ID (e.g., light.tube_lamp)
    """
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=40)

    logger.info(f"🔦 Testing ON command for: {entity_id}")
    logger.info("=" * 60)

    # Get initial state
    entity = inspector.client.get_entity(entity_id=entity_id)
    initial_state = entity.state.state
    logger.info(f"📊 Initial HA state: {initial_state}")
    logger.info("")

    # Ask user to confirm physical state
    logger.info("❓ Before we send the command:")
    logger.info(f"   What is the PHYSICAL state of the light right now?")
    logger.info(f"   (Just observe - don't touch anything yet)")
    input("   Press Enter to continue...")

    # Send turn_on command
    logger.info(f"\n🎚️  Sending light.turn_on to {entity_id}...")
    try:
        inspector.client.trigger_service(
            domain="light",
            service="turn_on",
            entity_id=entity_id,
            brightness=255  # Full brightness to make it obvious
        )
        logger.info(f"✅ Service call successful")
    except HomeassistantAPIError as e:
        logger.error(f"❌ Service call FAILED: {e}")
        return

    # Monitor state changes
    logger.info(f"\n👀 Monitoring state for 5 seconds...")
    logger.info(f"   Watch the physical light - does it turn ON?")

    for i in range(5):
        time.sleep(1)
        entity = inspector.client.get_entity(entity_id=entity_id)
        ha_state = entity.state.state
        brightness = entity.state.attributes.get('brightness', 'N/A')
        logger.info(f"   [{i+1}s] HA state: {ha_state}, brightness: {brightness}")

    # Final check
    entity = inspector.client.get_entity(entity_id=entity_id)
    final_state = entity.state.state
    final_brightness = entity.state.attributes.get('brightness', 'N/A')

    logger.info("")
    logger.info("=" * 60)
    logger.info("📊 RESULTS:")
    logger.info(f"   Initial HA state: {initial_state}")
    logger.info(f"   Final HA state: {final_state}")
    logger.info(f"   Final brightness: {final_brightness}")
    logger.info("")
    logger.info("❓ Did the PHYSICAL light turn on?")
    response = input("   (yes/no): ").strip().lower()

    if response == 'yes' and final_state == 'on':
        logger.info("✅ SUCCESS: Physical light ON, HA state is 'on'")
    elif response == 'yes' and final_state != 'on':
        logger.warning("⚠️  PARTIAL: Physical light ON, but HA state is still '{final_state}'")
    elif response == 'no' and final_state == 'on':
        logger.error("❌ DESYNC: Physical light OFF, but HA state is 'on'")
    elif response == 'no' and final_state != 'on':
        logger.info("⚠️  Physical light didn't turn on, HA state is '{final_state}'")

    logger.info("")
    logger.info("💡 Next steps:")
    logger.info("   - If physical light didn't respond: integration/device issue")
    logger.info("   - If physical light works but HA state wrong: state reporting issue")
    logger.info("   - Check Home Assistant logs for errors")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 force_light_on.py <entity_id>")
        print("Example: python3 force_light_on.py light.tube_lamp")
        sys.exit(1)

    entity_id = sys.argv[1]
    force_light_on(entity_id)
