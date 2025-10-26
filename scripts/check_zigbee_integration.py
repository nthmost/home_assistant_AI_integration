#!/usr/bin/env python3
"""
Check if Zigbee integrations are installed and configured.
"""

import logging
import sys
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
    """Check for Zigbee integrations."""

    logger.info("🔍 Checking for Zigbee integrations...\n")

    # Load credentials and connect
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=logging.WARNING)

    # Check components
    components = inspector.components

    logger.info(f"📦 Total components installed: {len(components)}\n")

    # Look for Zigbee-related components
    zigbee_components = [c for c in components if 'zigbee' in c.lower() or 'zha' in c.lower()]

    if zigbee_components:
        logger.info("✅ Found Zigbee-related components:")
        for comp in zigbee_components:
            logger.info(f"  - {comp}")
    else:
        logger.info("⚠️  No Zigbee components found (searched for 'zigbee' or 'zha')")

    # Check service domains for ZHA
    logger.info("\n🔧 Checking service domains...")
    domains = inspector.list_domains()

    zha_related = [d for d in domains if 'zha' in d.lower() or 'zigbee' in d.lower()]
    if zha_related:
        logger.info("✅ Found Zigbee-related service domains:")
        for domain in zha_related:
            logger.info(f"  - {domain}")
            services = inspector.get_services_for_domain(domain)
            if services:
                logger.info(f"    Services: {list(services.services.keys())}")
    else:
        logger.info("⚠️  No Zigbee service domains found")

    # Show all components (in case we're missing something)
    logger.info("\n📋 All installed components (showing zigbee/zha related):")
    for comp in sorted(components):
        if any(keyword in comp.lower() for keyword in ['zigbee', 'zha', 'z2m', 'mqtt']):
            logger.info(f"  • {comp}")

    logger.info("\n" + "=" * 80)
    logger.info("💡 If no Zigbee components found, you may need to:")
    logger.info("   1. Add the ZHA integration in Home Assistant")
    logger.info("   2. Install Zigbee2MQTT addon")
    logger.info("   3. Check if your Zigbee coordinator is connected")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
