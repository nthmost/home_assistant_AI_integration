#!/usr/bin/env python3
"""
Check what services are available for the remote domain
"""

import logging
import requests
from ha_core import load_credentials

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def check_remote_services():
    """Check available services for remote domain"""
    url, token = load_credentials()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    logger.info("🔍 Checking services for 'remote' domain...")
    logger.info("=" * 60)

    try:
        # Get all services
        response = requests.get(
            f"{url}/api/services",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        services_data = response.json()

        # Services can be a list or dict depending on HA version
        if isinstance(services_data, list):
            # Convert list to dict
            services = {}
            for item in services_data:
                domain = item.get('domain')
                services[domain] = item.get('services', {})
        else:
            services = services_data

        # Find remote domain
        remote_found = False
        for domain, domain_services in services.items():
            if domain == 'remote':
                remote_found = True
                logger.info(f"\n📋 REMOTE DOMAIN SERVICES:")
                logger.info(f"   Available: {len(domain_services)} services\n")

                for service_name, service_data in domain_services.items():
                    logger.info(f"   • remote.{service_name}")
                    if isinstance(service_data, dict):
                        if 'description' in service_data:
                            logger.info(f"     {service_data['description']}")
                        if 'fields' in service_data:
                            logger.info(f"     Fields: {list(service_data['fields'].keys())}")
                    logger.info("")
                break

        if not remote_found:
            logger.warning("⚠️  'remote' domain not found in services")
            logger.info("\nAvailable domains:")
            for domain in sorted(services.keys()):
                logger.info(f"   • {domain}")

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ API request failed: {e}")
        return

    logger.info("=" * 60)
    logger.info("💡 TIP: If turn_off isn't available, you may need to use send_command")
    logger.info("   with specific IR/RF codes for OFF")


if __name__ == "__main__":
    check_remote_services()
