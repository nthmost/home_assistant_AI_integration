#!/usr/bin/env python3
"""Demo script for Home Assistant device control.

Tests the HA client with real device commands.
"""

import logging
import time
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from saga_assistant.ha_client import (
    HomeAssistantClient,
    HomeAssistantError,
    EntityNotFoundError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_basic_info(client: HomeAssistantClient):
    """Show basic Home Assistant info."""
    print_section("🏠 Home Assistant Info")

    config = client.get_config()
    print(f"Location: {config.get('location_name', 'Unknown')}")
    print(f"Version:  {config.get('version', 'Unknown')}")
    print(f"URL:      {client.url}")

    states = client.get_states()
    print(f"Entities: {len(states)} total")


def demo_lights(client: HomeAssistantClient):
    """Demo light control."""
    print_section("💡 Lights")

    lights = client.get_entities_by_domain("light")
    print(f"Found {len(lights)} lights:\n")

    for light in lights:
        entity_id = light["entity_id"]
        name = light.get("attributes", {}).get("friendly_name", entity_id)
        state = light["state"]

        # Show state with color coding
        if state == "on":
            state_display = "🟢 ON"
        elif state == "off":
            state_display = "⚫ OFF"
        else:
            state_display = f"⚪ {state.upper()}"

        print(f"  {state_display:12s} {name}")
        print(f"             └─ {entity_id}")


def demo_switches(client: HomeAssistantClient):
    """Demo switch control."""
    print_section("🔌 Switches")

    switches = client.get_entities_by_domain("switch")
    print(f"Found {len(switches)} switches:\n")

    for switch in switches:
        entity_id = switch["entity_id"]
        name = switch.get("attributes", {}).get("friendly_name", entity_id)
        state = switch["state"]

        # Show state with color coding
        if state == "on":
            state_display = "🟢 ON"
        elif state == "off":
            state_display = "⚫ OFF"
        else:
            state_display = f"⚪ {state.upper()}"

        print(f"  {state_display:12s} {name}")
        print(f"             └─ {entity_id}")


def demo_search(client: HomeAssistantClient):
    """Demo entity search."""
    print_section("🔍 Search Examples")

    test_queries = ["light", "aqua", "tv", "strip"]

    for query in test_queries:
        results = client.search_entities(query)
        print(f"Search '{query}': {len(results)} results")

        for result in results[:3]:  # Show first 3
            name = result.get("attributes", {}).get("friendly_name", result["entity_id"])
            state = result["state"]
            print(f"  • {name} [{state}]")

        if len(results) > 3:
            print(f"  ... and {len(results) - 3} more")
        print()


def demo_control_interactive(client: HomeAssistantClient):
    """Interactive device control demo."""
    print_section("🎮 Interactive Control")

    # Get available lights and switches
    lights = client.get_entities_by_domain("light")
    switches = client.get_entities_by_domain("switch")

    # Filter to available devices only
    available_lights = [l for l in lights if l["state"] != "unavailable"]
    available_switches = [s for s in switches if s["state"] != "unavailable"]

    if not available_lights and not available_switches:
        print("⚠️  No available devices to control")
        return

    print("Choose a device to control:\n")

    devices = []

    if available_lights:
        print("💡 Lights:")
        for i, light in enumerate(available_lights, 1):
            name = light.get("attributes", {}).get("friendly_name", light["entity_id"])
            state = light["state"]
            print(f"  {i}. {name} [{state}]")
            devices.append(light)

    if available_switches:
        print("\n🔌 Switches:")
        start_num = len(devices) + 1
        for i, switch in enumerate(available_switches, start_num):
            name = switch.get("attributes", {}).get("friendly_name", switch["entity_id"])
            state = switch["state"]
            print(f"  {i}. {name} [{state}]")
            devices.append(switch)

    print(f"\n  0. Skip control demo")

    try:
        choice = input("\nEnter device number: ").strip()

        if choice == "0":
            print("Skipping control demo")
            return

        device_num = int(choice) - 1

        if device_num < 0 or device_num >= len(devices):
            print("❌ Invalid choice")
            return

        device = devices[device_num]
        entity_id = device["entity_id"]
        name = device.get("attributes", {}).get("friendly_name", entity_id)
        current_state = device["state"]

        print(f"\n📍 Selected: {name}")
        print(f"   Current state: {current_state}")
        print("\nActions:")
        print("  1. Turn ON")
        print("  2. Turn OFF")
        print("  3. Toggle")
        print("  0. Cancel")

        action = input("\nChoose action: ").strip()

        if action == "0":
            print("Cancelled")
            return

        print(f"\n⚙️  Sending command...")

        if action == "1":
            result = client.turn_on(entity_id)
            print(f"✅ Turned ON: {name}")
        elif action == "2":
            result = client.turn_off(entity_id)
            print(f"✅ Turned OFF: {name}")
        elif action == "3":
            result = client.toggle(entity_id)
            print(f"✅ Toggled: {name}")
        else:
            print("❌ Invalid action")
            return

        # Show new state
        time.sleep(0.5)  # Give HA time to update
        new_state = client.get_state(entity_id)
        print(f"   New state: {new_state['state']}")

    except ValueError:
        print("❌ Invalid input")
    except EntityNotFoundError as e:
        print(f"❌ {e}")
    except HomeAssistantError as e:
        print(f"❌ Error: {e}")
    except KeyboardInterrupt:
        print("\n\nCancelled")


def main():
    """Run the demo."""
    print("\n" + "="*60)
    print("  🏠 Home Assistant Control Demo")
    print("="*60)

    try:
        # Initialize client
        client = HomeAssistantClient()

        # Run demos
        demo_basic_info(client)
        demo_lights(client)
        demo_switches(client)
        demo_search(client)
        demo_control_interactive(client)

        print_section("✅ Demo Complete")
        print("Home Assistant integration is working!\n")

    except HomeAssistantError as e:
        logger.exception(f"Home Assistant error: {e}")
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted\n")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
