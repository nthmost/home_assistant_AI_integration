#!/usr/bin/env python3
"""
Find scripts, automations, or scenes related to office lights
"""

import logging
import requests
from ha_core import load_credentials

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def find_office_scripts():
    """Search for scripts and automations related to office lights"""
    url, token = load_credentials()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    logger.info("🔍 Searching for office-related scripts and automations...")
    logger.info("=" * 60)

    # Check for scripts
    logger.info("\n📜 CHECKING SCRIPTS...")
    try:
        response = requests.get(
            f"{url}/api/states",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        states = response.json()

        scripts = [s for s in states if s['entity_id'].startswith('script.')]
        logger.info(f"   Found {len(scripts)} total scripts")

        office_scripts = [s for s in scripts if 'office' in s['entity_id'].lower() or
                         'office' in s['attributes'].get('friendly_name', '').lower()]

        if office_scripts:
            logger.info(f"\n   🎯 Office-related scripts:")
            for script in office_scripts:
                logger.info(f"\n   • {script['entity_id']}")
                logger.info(f"     Name: {script['attributes'].get('friendly_name', 'N/A')}")
                logger.info(f"     Last changed: {script.get('last_changed', 'N/A')}")
        else:
            logger.info("   ❌ No office-related scripts found")

    except requests.exceptions.RequestException as e:
        logger.error(f"   ❌ Failed to fetch scripts: {e}")

    # Check for automations
    logger.info("\n🤖 CHECKING AUTOMATIONS...")
    try:
        automations = [s for s in states if s['entity_id'].startswith('automation.')]
        logger.info(f"   Found {len(automations)} total automations")

        office_automations = [a for a in automations if 'office' in a['entity_id'].lower() or
                             'office' in a['attributes'].get('friendly_name', '').lower()]

        if office_automations:
            logger.info(f"\n   🎯 Office-related automations:")
            for auto in office_automations:
                logger.info(f"\n   • {auto['entity_id']}")
                logger.info(f"     Name: {auto['attributes'].get('friendly_name', 'N/A')}")
                logger.info(f"     State: {auto['state']}")
        else:
            logger.info("   ❌ No office-related automations found")

    except Exception as e:
        logger.error(f"   ❌ Failed to check automations: {e}")

    # Check for switches that might control the lights
    logger.info("\n🔌 CHECKING SWITCHES...")
    switches = [s for s in states if s['entity_id'].startswith('switch.')]
    office_switches = [s for s in switches if 'office' in s['entity_id'].lower() or
                      'office' in s['attributes'].get('friendly_name', '').lower()]

    if office_switches:
        logger.info(f"   🎯 Office-related switches:")
        for switch in office_switches:
            logger.info(f"\n   • {switch['entity_id']}")
            logger.info(f"     Name: {switch['attributes'].get('friendly_name', 'N/A')}")
            logger.info(f"     State: {switch['state']}")
    else:
        logger.info("   ❌ No office-related switches found")

    logger.info("\n" + "=" * 60)
    logger.info("💡 If you found scripts/automations:")
    logger.info("   Those might be what Alexa is calling!")
    logger.info("   We should update the dashboard to call those instead of remote.turn_on/off")


if __name__ == "__main__":
    find_office_scripts()
