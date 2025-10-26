#!/usr/bin/env python3
"""
Inventory Zigbee devices using device registry API.
Since ZHA is installed, we can query the device registry for ZHA devices.
"""

import logging
import sys
import requests
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ha_core.config import load_credentials

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def get_devices(url: str, token: str) -> List[Dict[str, Any]]:
    """Get device registry from Home Assistant API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Device registry endpoint
    devices_url = f"{url.rstrip('/')}/api/config/device_registry/list"

    try:
        response = requests.get(devices_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch device registry: {e}")
        return []


def get_entities_for_device(url: str, token: str, device_id: str) -> List[Dict[str, Any]]:
    """Get all entities associated with a device."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Entity registry endpoint
    entities_url = f"{url.rstrip('/')}/api/config/entity_registry/list"

    try:
        response = requests.get(entities_url, headers=headers)
        response.raise_for_status()
        all_entities = response.json()

        # Filter entities for this device
        device_entities = [e for e in all_entities if e.get('device_id') == device_id]
        return device_entities
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch entities: {e}")
        return []


def get_entity_state(url: str, token: str, entity_id: str) -> Dict[str, Any]:
    """Get current state of an entity."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    state_url = f"{url.rstrip('/')}/api/states/{entity_id}"

    try:
        response = requests.get(state_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {}


def main():
    """Discover and inventory all Zigbee devices."""

    logger.info("🔍 Inventorying Zigbee devices via device registry...\n")

    # Load credentials
    url, token = load_credentials()
    base_url = url.replace('/api', '')

    # Get all devices
    devices = get_devices(base_url, token)

    # Filter for ZHA devices
    zha_devices = [
        d for d in devices
        if any('zha' in entry.lower() for entry in d.get('config_entries', []))
    ]

    if not zha_devices:
        logger.warning("⚠️  No ZHA devices found in device registry.")
        logger.info(f"\n📊 Total devices: {len(devices)}")
        logger.info("💡 ZHA is installed but no devices are configured.")
        logger.info("   Check your Zigbee coordinator connection in Home Assistant.")
        return

    logger.info(f"📋 Found {len(zha_devices)} Zigbee devices:\n")
    logger.info("=" * 80)

    for device in zha_devices:
        device_id = device.get('id')
        name = device.get('name', 'Unknown')
        manufacturer = device.get('manufacturer', 'N/A')
        model = device.get('model', 'N/A')
        sw_version = device.get('sw_version', 'N/A')

        logger.info(f"\n🔌 {name}")
        logger.info("-" * 80)
        logger.info(f"   Manufacturer: {manufacturer}")
        logger.info(f"   Model: {model}")
        if sw_version != 'N/A':
            logger.info(f"   Firmware: {sw_version}")

        # Get entities for this device
        entities = get_entities_for_device(base_url, token, device_id)

        if entities:
            logger.info(f"\n   📍 Entities ({len(entities)}):")
            for entity in entities:
                entity_id = entity.get('entity_id')
                platform = entity.get('platform', 'unknown')
                original_name = entity.get('original_name', entity_id)

                # Get current state
                state_info = get_entity_state(base_url, token, entity_id)
                current_state = state_info.get('state', 'N/A')

                logger.info(f"      • {entity_id}")
                logger.info(f"        └─ Platform: {platform}")
                logger.info(f"        └─ Name: {original_name}")
                logger.info(f"        └─ State: {current_state}")

                # Show useful attributes
                attributes = state_info.get('attributes', {})
                if 'battery_level' in attributes or 'battery' in attributes:
                    battery = attributes.get('battery_level') or attributes.get('battery')
                    logger.info(f"        └─ Battery: {battery}%")

                if 'linkquality' in attributes:
                    logger.info(f"        └─ Link Quality: {attributes['linkquality']}")

        logger.info("")

    logger.info("=" * 80)
    logger.info(f"\n✅ Inventory complete: {len(zha_devices)} Zigbee devices\n")


if __name__ == '__main__':
    main()
