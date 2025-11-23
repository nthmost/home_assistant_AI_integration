"""
Squawkers McCaw - Full Command Set

Extended Squawkers class with all learned commands as convenience methods.
Includes all Response, Command, Plain, and Gags buttons.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from squawkers.squawkers import Squawkers as BaseSquawkers

logger = logging.getLogger(__name__)


class SquawkersFull(BaseSquawkers):
    """
    Extended Squawkers with convenience methods for all learned commands.

    Inherits from base Squawkers class and adds methods for:
    - Response Button A-F
    - Command Button A-F
    - Button A-F (plain)
    - Gags A-F

    Usage:
        from squawkers.squawkers_full import SquawkersFull
        from saga_assistant.ha_client import HomeAssistantClient

        client = HomeAssistantClient()
        squawkers = SquawkersFull(client)

        # Universal commands
        squawkers.dance()
        squawkers.reset()

        # Response mode (preset behaviors)
        squawkers.response_a()  # Startled squawk
        squawkers.response_b()  # Laugh
        squawkers.response_c()  # Laugh hilariously

        # Gags mode
        squawkers.gag_a()
        squawkers.gag_b()

        # Or use the base method for any command
        squawkers.command("Response Button A")
    """

    # Response Mode buttons (preset behaviors from manual)

    def response_a(self, num_repeats: Optional[int] = None) -> bool:
        """Response Button A: Startled squawk"""
        return self.command("Response Button A", num_repeats=num_repeats)

    def response_b(self, num_repeats: Optional[int] = None) -> bool:
        """Response Button B: Laugh"""
        return self.command("Response Button B", num_repeats=num_repeats)

    def response_c(self, num_repeats: Optional[int] = None) -> bool:
        """Response Button C: Laugh hilariously"""
        return self.command("Response Button C", num_repeats=num_repeats)

    def response_d(self, num_repeats: Optional[int] = None) -> bool:
        """Response Button D: Warble"""
        return self.command("Response Button D", num_repeats=num_repeats)

    def response_e(self, num_repeats: Optional[int] = None) -> bool:
        """Response Button E: Say 'Whatever!!'"""
        return self.command("Response Button E", num_repeats=num_repeats)

    def response_f(self, num_repeats: Optional[int] = None) -> bool:
        """Response Button F: Play along"""
        return self.command("Response Button F", num_repeats=num_repeats)

    # Command Mode buttons (for custom voice commands)

    def command_a(self, num_repeats: Optional[int] = None) -> bool:
        """Command A"""
        return self.command("Command A", num_repeats=num_repeats)

    def command_b(self, num_repeats: Optional[int] = None) -> bool:
        """Command B"""
        return self.command("Command B", num_repeats=num_repeats)

    def command_c(self, num_repeats: Optional[int] = None) -> bool:
        """Command C"""
        return self.command("Command C", num_repeats=num_repeats)

    def command_d(self, num_repeats: Optional[int] = None) -> bool:
        """Command D"""
        return self.command("Command D", num_repeats=num_repeats)

    def command_e(self, num_repeats: Optional[int] = None) -> bool:
        """Command E"""
        return self.command("Command E", num_repeats=num_repeats)

    def command_f(self, num_repeats: Optional[int] = None) -> bool:
        """Command F"""
        return self.command("Command F", num_repeats=num_repeats)

    # Plain buttons

    def button_a(self, num_repeats: Optional[int] = None) -> bool:
        """Button A"""
        return self.command("Button A", num_repeats=num_repeats)

    def button_b(self, num_repeats: Optional[int] = None) -> bool:
        """Button B"""
        return self.command("Button B", num_repeats=num_repeats)

    def button_c(self, num_repeats: Optional[int] = None) -> bool:
        """Button C"""
        return self.command("Button C", num_repeats=num_repeats)

    def button_d(self, num_repeats: Optional[int] = None) -> bool:
        """Button D"""
        return self.command("Button D", num_repeats=num_repeats)

    def button_e(self, num_repeats: Optional[int] = None) -> bool:
        """Button E"""
        return self.command("Button E", num_repeats=num_repeats)

    def button_f(self, num_repeats: Optional[int] = None) -> bool:
        """Button F"""
        return self.command("Button F", num_repeats=num_repeats)

    # Gags Mode buttons

    def gag_a(self, num_repeats: Optional[int] = None) -> bool:
        """Gags A"""
        return self.command("Gags A", num_repeats=num_repeats)

    def gag_b(self, num_repeats: Optional[int] = None) -> bool:
        """Gags B"""
        return self.command("Gags B", num_repeats=num_repeats)

    def gag_c(self, num_repeats: Optional[int] = None) -> bool:
        """Gags C"""
        return self.command("Gags C", num_repeats=num_repeats)

    def gag_d(self, num_repeats: Optional[int] = None) -> bool:
        """Gags D"""
        return self.command("Gags D", num_repeats=num_repeats)

    def gag_e(self, num_repeats: Optional[int] = None) -> bool:
        """Gags E"""
        return self.command("Gags E", num_repeats=num_repeats)

    def gag_f(self, num_repeats: Optional[int] = None) -> bool:
        """Gags F"""
        return self.command("Gags F", num_repeats=num_repeats)

    # Record Command buttons (for recording custom commands)

    def record_command_a(self, num_repeats: Optional[int] = None) -> bool:
        """Record Command A"""
        return self.command("Record Command A", num_repeats=num_repeats)

    def record_command_b(self, num_repeats: Optional[int] = None) -> bool:
        """Record Command B"""
        return self.command("Record Command B", num_repeats=num_repeats)

    def record_command_c(self, num_repeats: Optional[int] = None) -> bool:
        """Record Command C"""
        return self.command("Record Command C", num_repeats=num_repeats)

    def record_command_d(self, num_repeats: Optional[int] = None) -> bool:
        """Record Command D"""
        return self.command("Record Command D", num_repeats=num_repeats)

    def record_command_e(self, num_repeats: Optional[int] = None) -> bool:
        """Record Command E"""
        return self.command("Record Command E", num_repeats=num_repeats)

    def record_command_f(self, num_repeats: Optional[int] = None) -> bool:
        """Record Command F"""
        return self.command("Record Command F", num_repeats=num_repeats)

    # Record Response buttons (for recording custom responses)

    def record_response_a(self, num_repeats: Optional[int] = None) -> bool:
        """Record Response A"""
        return self.command("Record Response A", num_repeats=num_repeats)

    def record_response_b(self, num_repeats: Optional[int] = None) -> bool:
        """Record Response B"""
        return self.command("Record Response B", num_repeats=num_repeats)

    def record_response_c(self, num_repeats: Optional[int] = None) -> bool:
        """Record Response C"""
        return self.command("Record Response C", num_repeats=num_repeats)

    def record_response_d(self, num_repeats: Optional[int] = None) -> bool:
        """Record Response D"""
        return self.command("Record Response D", num_repeats=num_repeats)

    def record_response_e(self, num_repeats: Optional[int] = None) -> bool:
        """Record Response E"""
        return self.command("Record Response E", num_repeats=num_repeats)

    def record_response_f(self, num_repeats: Optional[int] = None) -> bool:
        """Record Response F"""
        return self.command("Record Response F", num_repeats=num_repeats)

    # Convenience methods for groups

    def list_response_methods(self):
        """List all Response mode methods"""
        return [
            "response_a", "response_b", "response_c",
            "response_d", "response_e", "response_f"
        ]

    def list_command_methods(self):
        """List all Command mode methods"""
        return [
            "command_a", "command_b", "command_c",
            "command_d", "command_e", "command_f"
        ]

    def list_button_methods(self):
        """List all plain button methods"""
        return [
            "button_a", "button_b", "button_c",
            "button_d", "button_e", "button_f"
        ]

    def list_gag_methods(self):
        """List all Gags mode methods"""
        return [
            "gag_a", "gag_b", "gag_c",
            "gag_d", "gag_e", "gag_f"
        ]

    def list_record_command_methods(self):
        """List all Record Command methods"""
        return [
            "record_command_a", "record_command_b", "record_command_c",
            "record_command_d", "record_command_e", "record_command_f"
        ]

    def list_record_response_methods(self):
        """List all Record Response methods"""
        return [
            "record_response_a", "record_response_b", "record_response_c",
            "record_response_d", "record_response_e", "record_response_f"
        ]

    def list_all_methods(self):
        """List all available command methods"""
        return {
            "universal": ["dance", "reset"],
            "response": self.list_response_methods(),
            "command": self.list_command_methods(),
            "button": self.list_button_methods(),
            "gag": self.list_gag_methods(),
            "record_command": self.list_record_command_methods(),
            "record_response": self.list_record_response_methods()
        }


def main():
    """Demo script"""
    import os
    from dotenv import load_dotenv
    from saga_assistant.ha_client import HomeAssistantClient

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    load_dotenv()

    print("🦜 Squawkers Full Command Demo")
    print("=" * 70)

    try:
        client = HomeAssistantClient()
        squawkers = SquawkersFull(client)

        print("\n✓ Connected")
        print("\nAvailable methods:")

        methods = squawkers.list_all_methods()
        for category, method_list in methods.items():
            print(f"\n  {category.upper()}:")
            for method in method_list:
                print(f"    • squawkers.{method}()")

        print("\n" + "=" * 70)
        print("\nExample usage:")
        print("  squawkers.response_b()  # Laugh")
        print("  squawkers.gag_a()       # Gag A")
        print("  squawkers.dance()       # Dance")
        print("\n" + "=" * 70)
        print("\n✓ All methods loaded successfully!")

    except Exception as e:
        logger.exception("Error in demo")
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
