#!/usr/bin/env python3
"""
List all learned commands for a Broadlink remote
by checking the filesystem where HA stores them
"""

import logging
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def list_learned_commands():
    """
    Check for learned Broadlink commands in HA's storage
    """
    logger.info("🔍 Searching for learned Broadlink commands...")
    logger.info("=" * 60)

    # Broadlink commands are typically stored in:
    # /config/broadlink_remote_MACADDRESS_codes
    # or /config/custom_components/broadlink/codes

    logger.info("\n📂 Checking for Broadlink code storage directories...")

    # Try to find broadlink directories
    try:
        result = subprocess.run(
            ["ssh", "homeassistant.local", "find /config -name '*broadlink*' -type d"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.stdout:
            logger.info(f"\n   Found directories:")
            for line in result.stdout.strip().split('\n'):
                logger.info(f"   📁 {line}")
        else:
            logger.warning("   ❌ No broadlink directories found")

    except subprocess.TimeoutExpired:
        logger.error("   ❌ SSH connection timed out")
    except Exception as e:
        logger.warning(f"   ⚠️  Can't search via SSH: {e}")
        logger.info("   Trying alternate method...")

    # Look for code files
    logger.info("\n📄 Checking for Broadlink code files...")
    try:
        result = subprocess.run(
            ["ssh", "homeassistant.local", "find /config -name '*codes*' -type f | grep -i broadlink"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=True
        )

        if result.stdout:
            logger.info(f"\n   Found code files:")
            for line in result.stdout.strip().split('\n'):
                logger.info(f"   📄 {line}")

                # Try to read the file
                file_path = line.strip()
                cat_result = subprocess.run(
                    ["ssh", "homeassistant.local", f"cat {file_path}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if cat_result.stdout:
                    logger.info(f"\n   Contents of {file_path}:")
                    logger.info("   " + "="*55)
                    for content_line in cat_result.stdout.split('\n')[:20]:  # First 20 lines
                        logger.info(f"   {content_line}")
                    logger.info("   " + "="*55)
        else:
            logger.warning("   ❌ No code files found")

    except Exception as e:
        logger.warning(f"   ⚠️  Can't search for code files: {e}")

    logger.info("\n" + "=" * 60)
    logger.info("💡 ALTERNATIVE: Check in HA directly")
    logger.info("")
    logger.info("Go to: File Editor add-on or SSH into HA")
    logger.info("Look for files like:")
    logger.info("  /config/broadlink_remote_*_codes")
    logger.info("")
    logger.info("If NO files exist → Learned codes are GONE")
    logger.info("If files exist → Codes are there but Broadlink device is offline")


if __name__ == "__main__":
    list_learned_commands()
