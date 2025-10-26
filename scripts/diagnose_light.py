#!/usr/bin/env python3
"""
Diagnose light state synchronization issues

This script helps identify why a light's state in Home Assistant
doesn't match the physical device state.
"""

import sys
import json
import logging
from ha_core import HomeAssistantInspector, load_credentials

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def diagnose_light(entity_id: str):
    """
    Comprehensive diagnostics for a light entity

    Args:
        entity_id: Entity ID to diagnose (e.g., light.tube_lamp)
    """
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=40)

    logger.info(f"🔍 Diagnosing: {entity_id}")
    logger.info("=" * 60)

    # Get entity details - let import errors and connection errors propagate naturally
    entity = inspector.client.get_entity(entity_id=entity_id)

    if not entity:
        logger.error(f"❌ Entity not found: {entity_id}")
        return

    # Basic state
    logger.info(f"\n📊 CURRENT STATE")
    logger.info(f"   Entity ID: {entity.entity_id}")
    logger.info(f"   Domain: {entity.entity_id.split('.')[0]}")
    logger.info(f"   State: {entity.state.state}")

    # Attributes
    if hasattr(entity.state, 'attributes'):
        attrs = entity.state.attributes

        logger.info(f"\n🏷️  ATTRIBUTES")
        logger.info(f"   Friendly name: {attrs.get('friendly_name', 'N/A')}")
        logger.info(f"   Supported features: {attrs.get('supported_features', 'N/A')}")
        logger.info(f"   Supported color modes: {attrs.get('supported_color_modes', 'N/A')}")

        # Integration info
        logger.info(f"\n🔌 INTEGRATION INFO")
        logger.info(f"   Device class: {attrs.get('device_class', 'N/A')}")
        logger.info(f"   Attribution: {attrs.get('attribution', 'N/A')}")
        logger.info(f"   Integration: {attrs.get('integration', 'N/A')}")

        # State tracking
        logger.info(f"\n⏰ STATE TRACKING")
        logger.info(f"   Last changed: {entity.state.last_changed}")
        logger.info(f"   Last updated: {entity.state.last_updated}")
        logger.info(f"   Assumed state: {attrs.get('assumed_state', False)}")

        # Full attributes dump
        logger.info(f"\n📋 FULL ATTRIBUTES")
        for key, value in sorted(attrs.items()):
            logger.info(f"   {key}: {value}")

    # Test state refresh
    logger.info(f"\n🔄 TESTING STATE REFRESH")
    logger.info(f"   Current state: {entity.state.state}")

    # Call homeassistant.update_entity service to force state refresh
    import time
    from homeassistant_api.errors import HomeassistantAPIError

    logger.info(f"   Calling homeassistant.update_entity...")
    try:
        inspector.client.trigger_service(
            domain="homeassistant",
            service="update_entity",
            entity_id=entity_id
        )
        logger.info(f"   ✅ Update entity called successfully")
    except HomeassistantAPIError as e:
        logger.error(f"   ❌ Failed to call update_entity service: {e}")
        logger.info(f"   Continuing with diagnostics...")

    # Wait and check again
    time.sleep(2)

    updated_entity = inspector.client.get_entity(entity_id=entity_id)
    logger.info(f"   State after refresh: {updated_entity.state.state}")

    if updated_entity.state.state != entity.state.state:
        logger.info(f"   🎉 State changed: {entity.state.state} → {updated_entity.state.state}")
    else:
        logger.warning(f"   ⚠️  State unchanged after refresh")

    # Available services for this entity
    logger.info(f"\n🛠️  AVAILABLE SERVICES")
    from homeassistant_api.errors import HomeassistantAPIError

    try:
        services = inspector.get_domain_services('light')
        logger.info(f"   Light domain services: {', '.join(services)}")
    except (HomeassistantAPIError, AttributeError) as e:
        logger.warning(f"   Could not retrieve services: {e}")

    logger.info("\n" + "=" * 60)
    logger.info("🏁 Diagnosis complete")
    logger.info("\n💡 RECOMMENDATIONS:")
    logger.info("   1. Check if 'assumed_state' is True (device doesn't report state)")
    logger.info("   2. Look at 'integration' to identify the device type")
    logger.info("   3. Check Home Assistant logs for communication errors")
    logger.info("   4. Try controlling the device in HA UI to see if state updates")
    logger.info("   5. Consider reloading the integration or restarting HA")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 diagnose_light.py <entity_id>")
        print("Example: python3 diagnose_light.py light.tube_lamp")
        sys.exit(1)

    entity_id = sys.argv[1]
    diagnose_light(entity_id)
