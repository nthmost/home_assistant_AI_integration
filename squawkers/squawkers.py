"""
Squawkers McCaw Control Object

A simple, reusable Python class for controlling a Squawkers McCaw
animatronic parrot via Home Assistant IR commands.

Usage:
    from squawkers import Squawkers
    from saga_assistant.ha_client import HomeAssistantClient

    client = HomeAssistantClient()
    squawkers = Squawkers(client, device_name="squawkers")

    # Basic commands
    squawkers.dance()
    squawkers.reset()

    # Test sequence
    squawkers.dance()
    time.sleep(5)
    squawkers.reset()
"""

import logging
import time
from typing import Optional

from saga_assistant.ha_client import HomeAssistantClient, ServiceCallError

logger = logging.getLogger(__name__)


class SquawkersError(Exception):
    """Base exception for Squawkers control errors"""
    pass


class CommandError(SquawkersError):
    """Failed to send IR command"""
    pass


class Squawkers:
    """
    Simple control interface for Squawkers McCaw animatronic parrot.

    Sends IR commands through Home Assistant's remote.send_command service.
    """

    def __init__(
        self,
        ha_client: HomeAssistantClient,
        entity_id: str = "remote.office_lights",
        device_name: str = "squawkers",
        num_repeats: int = 3,
        delay_between_repeats: float = 0.5
    ):
        """
        Initialize Squawkers controller.

        Args:
            ha_client: Home Assistant client instance
            entity_id: Remote entity ID in Home Assistant (default: "remote.office_lights")
            device_name: Name of the IR device in Home Assistant (default: "squawkers")
            num_repeats: Default number of times to repeat each command (default: 3)
            delay_between_repeats: Seconds to wait between repeats (default: 0.5)

        Note:
            The device_name should match the device configured in Home Assistant.
            Commands are repeated multiple times with delays because the IR receiver
            is more reliable with repeated signals (per GitHub playfultechnology/SquawkersMcGraw#2).
        """
        self.client = ha_client
        self.entity_id = entity_id
        self.device_name = device_name
        self.num_repeats = num_repeats
        self.delay_between_repeats = delay_between_repeats

        logger.info(
            f"Initialized Squawkers controller: entity={entity_id}, device={device_name}, "
            f"repeats={num_repeats}, delay={delay_between_repeats}s"
        )

    def _send_command(
        self,
        command: str,
        num_repeats: Optional[int] = None,
        delay: Optional[float] = None
    ) -> bool:
        """
        Send an IR command to Squawkers via Home Assistant.

        Args:
            command: Command name (e.g., "DANCE", "RESET")
            num_repeats: Number of times to repeat (None = use default)
            delay: Delay between repeats in seconds (None = use default)

        Returns:
            True if command was sent successfully

        Raises:
            CommandError: If command fails to send
        """
        repeats = num_repeats if num_repeats is not None else self.num_repeats
        delay_secs = delay if delay is not None else self.delay_between_repeats

        logger.info(f"Sending command '{command}' to {self.device_name} ({repeats}x)")

        try:
            # Send command using Broadlink format
            self.client.call_service(
                domain="remote",
                service="send_command",
                entity_id=self.entity_id,
                device=self.device_name,
                command=[command],  # Must be a list
                num_repeats=repeats,
                delay_secs=delay_secs
            )

            logger.info(f"✓ Command '{command}' sent successfully")
            return True

        except ServiceCallError as e:
            error_msg = f"Failed to send command '{command}': {e}"
            logger.error(error_msg)
            raise CommandError(error_msg) from e

    def dance(self, num_repeats: Optional[int] = None) -> bool:
        """
        Make Squawkers dance!

        This is the most reliable command - works in any mode.

        Args:
            num_repeats: Override default repeat count

        Returns:
            True if successful
        """
        return self._send_command("DANCE", num_repeats=num_repeats)

    def reset(self, num_repeats: Optional[int] = None) -> bool:
        """
        Reset Squawkers (stop current action).

        Reliable command that works in any mode.

        Args:
            num_repeats: Override default repeat count

        Returns:
            True if successful
        """
        return self._send_command("RESET", num_repeats=num_repeats)

    def test_sequence(self, dance_duration: float = 5.0) -> bool:
        """
        Run a test sequence: DANCE, wait, RESET.

        Useful for verifying the controller is working.

        Args:
            dance_duration: Seconds to let it dance before resetting

        Returns:
            True if successful
        """
        logger.info(f"Starting test sequence (dance for {dance_duration}s)")

        self.dance()
        logger.info(f"Waiting {dance_duration} seconds...")
        time.sleep(dance_duration)
        self.reset()

        logger.info("Test sequence complete")
        return True

    def command(
        self,
        command_name: str,
        num_repeats: Optional[int] = None
    ) -> bool:
        """
        Send any arbitrary command to Squawkers.

        Use this for commands not wrapped by convenience methods.

        Args:
            command_name: IR command name (e.g., "RESPONSE_A", "GAGS_B")
            num_repeats: Override default repeat count

        Returns:
            True if successful

        Example:
            squawkers.command("RESPONSE_A")
            squawkers.command("CUSTOM_COMMAND", num_repeats=5)
        """
        return self._send_command(command_name, num_repeats=num_repeats)


def main():
    """Demo/test script"""
    import os
    from dotenv import load_dotenv

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load environment
    load_dotenv()

    print("🦜 Squawkers McCaw Control Demo")
    print("=" * 70)

    try:
        # Initialize
        client = HomeAssistantClient()
        squawkers = Squawkers(client, device_name="squawkers")

        print("\n✓ Connected to Home Assistant")
        print(f"✓ Controlling device: squawkers")

        # Run test sequence
        print("\n▶ Running test sequence...")
        print("  1. DANCE command")
        print("  2. Wait 5 seconds")
        print("  3. RESET command")
        print()

        squawkers.test_sequence(dance_duration=5.0)

        print("\n✓ Test complete!")

    except Exception as e:
        logger.exception("Error in demo")
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
