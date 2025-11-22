#!/usr/bin/env python3
"""
Example usage of the Squawkers class.

Shows how to import and use Squawkers in your own code.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient


def example_basic():
    """Basic usage example"""
    print("Example 1: Basic Usage")
    print("-" * 50)

    # Initialize
    client = HomeAssistantClient()
    squawkers = Squawkers(client)

    # Simple commands
    print("Making Squawkers dance...")
    squawkers.dance()

    print("Resetting Squawkers...")
    squawkers.reset()

    print()


def example_custom_repeats():
    """Example with custom repeat settings"""
    print("Example 2: Custom Repeats")
    print("-" * 50)

    client = HomeAssistantClient()

    # More repeats for better reliability
    squawkers = Squawkers(
        client,
        num_repeats=5,
        delay_between_repeats=1.0
    )

    print("Sending DANCE with 5 repeats...")
    squawkers.dance()

    print()


def example_test_sequence():
    """Example using the test sequence"""
    print("Example 3: Test Sequence")
    print("-" * 50)

    client = HomeAssistantClient()
    squawkers = Squawkers(client)

    # Run the built-in test
    print("Running test sequence (dance 3 seconds, then reset)...")
    squawkers.test_sequence(dance_duration=3.0)

    print()


def example_custom_commands():
    """Example with custom commands"""
    print("Example 4: Custom Commands")
    print("-" * 50)

    client = HomeAssistantClient()
    squawkers = Squawkers(client)

    # You can send any command learned in HA
    print("Sending custom command...")
    squawkers.command("RESPONSE_A")  # If you have this learned

    print()


def example_error_handling():
    """Example with error handling"""
    print("Example 5: Error Handling")
    print("-" * 50)

    from squawkers import CommandError

    client = HomeAssistantClient()
    squawkers = Squawkers(client)

    try:
        print("Sending command...")
        squawkers.dance()
        print("✓ Success!")

    except CommandError as e:
        print(f"✗ Failed: {e}")

    print()


def main():
    """Run all examples"""
    load_dotenv()

    print("=" * 50)
    print("SQUAWKERS USAGE EXAMPLES")
    print("=" * 50)
    print()

    # Run examples
    example_basic()
    example_test_sequence()
    example_custom_repeats()
    example_error_handling()

    print("All examples complete!")


if __name__ == "__main__":
    main()
