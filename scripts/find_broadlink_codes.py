#!/usr/bin/env python3
"""
Search for Broadlink learned codes in HA storage
"""

import logging
import subprocess
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def find_broadlink_codes():
    """Search for Broadlink code storage files"""
    logger.info("🔍 Searching for Broadlink learned codes...")
    logger.info("=" * 60)

    # Common locations for Broadlink codes
    search_paths = [
        "/config/.storage/broadlink*",
        "/config/broadlink_remote_*",
        "/config/custom_components/broadlink/codes/*",
    ]

    logger.info("\n📂 Checking common Broadlink storage locations...")

    all_files = []

    for pattern in search_paths:
        logger.info(f"\n🔍 Searching: {pattern}")
        try:
            result = subprocess.run(
                ["ssh", "homeassistant.local", f"ls -la {pattern} 2>/dev/null"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.stdout:
                logger.info(f"   ✅ Found files:")
                for line in result.stdout.strip().split('\n'):
                    logger.info(f"      {line}")
                    # Extract filename
                    parts = line.split()
                    if len(parts) >= 9:
                        filename = ' '.join(parts[8:])
                        if filename.startswith('/'):
                            all_files.append(filename)
            else:
                logger.info(f"   ❌ No files found")

        except subprocess.TimeoutExpired:
            logger.error(f"   ❌ SSH timeout")
        except Exception as e:
            logger.warning(f"   ⚠️  Error: {e}")

    # Also search for any files containing "Office Lights"
    logger.info("\n🔍 Searching for files mentioning 'Office Lights'...")
    try:
        result = subprocess.run(
            ["ssh", "homeassistant.local",
             "grep -r 'Office Lights' /config/.storage/ /config/broadlink* 2>/dev/null | head -20"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=True
        )

        if result.stdout:
            logger.info(f"   ✅ Found references:")
            for line in result.stdout.strip().split('\n'):
                logger.info(f"      {line[:120]}")  # Truncate long lines
                # Extract the filename
                if ':' in line:
                    filepath = line.split(':')[0]
                    if filepath not in all_files:
                        all_files.append(filepath)

    except Exception as e:
        logger.warning(f"   ⚠️  Error: {e}")

    # Read the contents of found files
    if all_files:
        logger.info(f"\n📄 Reading found files...")
        for filepath in all_files:
            logger.info(f"\n{'='*60}")
            logger.info(f"📄 {filepath}")
            logger.info(f"{'='*60}")

            try:
                result = subprocess.run(
                    ["ssh", "homeassistant.local", f"cat {filepath}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.stdout:
                    # Try to parse as JSON for prettier display
                    try:
                        data = json.loads(result.stdout)
                        logger.info(json.dumps(data, indent=2)[:2000])  # First 2000 chars
                    except json.JSONDecodeError:
                        # Not JSON, show raw
                        logger.info(result.stdout[:2000])  # First 2000 chars
                else:
                    logger.warning(f"   ⚠️  File is empty")

            except Exception as e:
                logger.error(f"   ❌ Error reading file: {e}")

    else:
        logger.warning("\n❌ No Broadlink code files found!")

    logger.info("\n" + "=" * 60)
    logger.info("💡 WHAT TO LOOK FOR:")
    logger.info("")
    logger.info("Files like:")
    logger.info("  - /config/.storage/broadlink_remote_*")
    logger.info("  - /config/broadlink_remote_MACADDRESS_codes")
    logger.info("")
    logger.info("Inside should be JSON with learned commands like:")
    logger.info('  "Office Lights": {')
    logger.info('    "Red": "base64encodedIRcode...",')
    logger.info('    "Blue": "base64encodedIRcode...",')
    logger.info("    ...")
    logger.info("  }")


if __name__ == "__main__":
    find_broadlink_codes()
