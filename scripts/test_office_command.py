#!/usr/bin/env python3
"""
Test sending a specific learned command to office_lights
"""

import sys
import logging
from ha_core import HomeAssistantInspector, load_credentials
from homeassistant_api.errors import HomeassistantAPIError

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def test_command(command_name: str):
    """
    Test sending a specific command to office_lights

    Args:
        command_name: The learned command name (e.g., "Off", "On", "Light+")
    """
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=40)

    logger.info(f"🧪 Testing command: '{command_name}' on remote.office_lights")
    logger.info("=" * 60)

    # Send command with DEVICE parameter (critical for Broadlink!)
    # Entity = the IR blaster device (remote.office_ir)
    # Device = the logical grouping name used when learning ("Office Lights")
    # Command = the specific IR code learned (e.g., "Red", "Blue", "Light+")

    logger.info(f"\n📡 Sending remote.send_command")
    logger.info(f"   Entity (IR blaster): remote.office_ir")
    logger.info(f"   Device (learned group): Office Lights")
    logger.info(f"   Command: {command_name}")

    try:
        inspector.client.trigger_service(
            domain="remote",
            service="send_command",
            entity_id="remote.office_ir",  # ← The Broadlink IR blaster
            device="Office Lights",         # ← Device name used when learning commands
            command=[command_name]          # ← The specific IR code (must be a list)
        )
        logger.info(f"   ✅ Command sent successfully!")
    except HomeassistantAPIError as e:
        logger.error(f"   ❌ Failed: {e}")

    # Wait for user feedback
    logger.info("")
    logger.info("⏱️  Waiting 2 seconds...")
    import time
    time.sleep(2)

    # Check state
    entity = inspector.client.get_entity(entity_id="remote.office_lights")
    logger.info(f"📊 Current state: {entity.state.state}")

    logger.info("")
    logger.info("=" * 60)
    logger.info("❓ Did the physical office lights respond?")
    logger.info("")
    logger.info("If YES:")
    logger.info("  - The learned command works!")
    logger.info("  - We need to update the dashboard to use remote.send_command")
    logger.info("  - Instead of remote.turn_on/turn_off")
    logger.info("")
    logger.info("If NO:")
    logger.info("  - Check if Broadlink device is powered and in range")
    logger.info("  - Try re-learning the command in HA")
    logger.info("  - Check HA logs for Broadlink errors")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_office_command.py <command_name>")
        print("")
        print("Examples:")
        print("  python3 test_office_command.py Off")
        print("  python3 test_office_command.py On")
        print("  python3 test_office_command.py 'Light+'")
        print("  python3 test_office_command.py Red")
        sys.exit(1)

    command_name = sys.argv[1]
    test_command(command_name)
