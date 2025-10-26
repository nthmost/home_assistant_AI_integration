#!/usr/bin/env python3
"""
Check recent Home Assistant logs for errors
"""

import logging
import requests
from ha_core import load_credentials

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def check_ha_logs():
    """Check recent HA logs for errors"""
    url, token = load_credentials()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    logger.info("📋 Fetching recent Home Assistant logs...")
    logger.info("=" * 60)

    try:
        # Get error logs
        response = requests.get(
            f"{url}/api/error_log",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        logs = response.text

        # Get last 50 lines
        log_lines = logs.split('\n')
        recent_logs = log_lines[-50:]

        logger.info(f"\n📊 Last 50 log entries:\n")
        for line in recent_logs:
            if line.strip():
                # Highlight errors and warnings
                if 'ERROR' in line:
                    logger.error(f"   ❌ {line}")
                elif 'WARNING' in line:
                    logger.warning(f"   ⚠️  {line}")
                elif 'broadlink' in line.lower() or 'remote' in line.lower() or 'office' in line.lower():
                    logger.info(f"   🔍 {line}")
                else:
                    print(f"       {line}")

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to fetch logs: {e}")
        return

    logger.info("\n" + "=" * 60)
    logger.info("💡 Look for errors related to:")
    logger.info("   - 'broadlink'")
    logger.info("   - 'remote.office_ir'")
    logger.info("   - 'Office Lights'")
    logger.info("   - Connection errors, timeouts, or 'device not found'")


if __name__ == "__main__":
    check_ha_logs()
