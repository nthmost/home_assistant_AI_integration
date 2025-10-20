#!/usr/bin/env python3
"""
Demo script comparing the homegrown HomeAssistantClient
with the new HomeAssistantInspector (using HomeAssistant-API library)

This script demonstrates:
1. Basic connectivity with both clients
2. Fetching entity states
3. Listing entities by domain
4. Inspector-specific features (system info, summaries, active entities)
"""

import logging
import sys
import os

# Add the light_effects directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'light_effects'))

from ha_client import HomeAssistantClient
from ha_inspector import HomeAssistantInspector
from ha_config import load_credentials


def demo_homegrown_client(url: str, token: str) -> None:
    """Demonstrate the homegrown HomeAssistantClient"""
    print("\n" + "="*70)
    print("🔧 HOMEGROWN CLIENT (light_effects/ha_client.py)")
    print("="*70 + "\n")

    client = HomeAssistantClient(url, token)

    # Test basic functionality
    print("📡 Testing basic API call...")
    try:
        all_states = client.get_all_states()
        print(f"✅ Successfully retrieved {len(all_states)} entity states\n")

        # Group by domain
        domains = {}
        for state in all_states:
            entity_id = state.get('entity_id', '')
            domain = entity_id.split('.')[0] if '.' in entity_id else 'unknown'
            domains[domain] = domains.get(domain, 0) + 1

        print("📊 Entities by domain (top 10):")
        for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {domain:20s}: {count:4d}")

        # Show some light entities
        print("\n💡 Sample light entities:")
        lights = [s for s in all_states if s.get('entity_id', '').startswith('light.')][:5]
        for light in lights:
            entity_id = light['entity_id']
            state = light['state']
            print(f"  {entity_id:40s} [{state}]")

        print("\n✨ Homegrown client features:")
        print("  • Low-level REST API access")
        print("  • Direct control over requests")
        print("  • Lightweight with minimal dependencies")
        print("  • Custom light effects included")

    except Exception as e:
        print(f"❌ Error: {e}")


def demo_inspector_client(url: str, token: str) -> None:
    """Demonstrate the new HomeAssistantInspector"""
    print("\n" + "="*70)
    print("🔍 NEW INSPECTOR CLIENT (light_effects/ha_inspector.py)")
    print("="*70 + "\n")

    # Create inspector with INFO logging to show what it's doing
    inspector = HomeAssistantInspector(url, token, log_level=logging.INFO)

    # System info
    print("🏠 System Information:")
    print(f"  Version: {inspector.version}")
    print(f"  Location: {inspector.location_name}")
    print(f"  Status: {'✅ Running' if inspector.is_running else '❌ Not Running'}")
    print(f"  Components: {len(inspector.components)}")
    print(f"  Total Entities: {inspector.get_entity_count()}")

    # Domain summary
    print("\n📊 Domain Summary:")
    summary = inspector.get_domain_summary()
    for domain, count in sorted(summary.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {domain:20s}: {count:4d}")

    # Convenience properties
    print("\n💡 Quick access via properties:")
    print(f"  Lights: {len(inspector.lights)}")
    print(f"  Switches: {len(inspector.switches)}")
    print(f"  Sensors: {len(inspector.sensors)}")
    print(f"  Automations: {len(inspector.automations)}")

    # Active entities
    print("\n⚡ Currently Active Entities:")
    active = inspector.get_active_entities(domains=['light', 'switch', 'media_player'])
    for domain, entities in sorted(active.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {domain}: {len(entities)} active")
        for entity in entities[:3]:  # Show first 3
            print(f"    • {entity.entity_id} [{entity.state.state}]")
        if len(entities) > 3:
            print(f"    ... and {len(entities) - 3} more")

    # Service discovery
    print("\n🔧 Available Services (sample):")
    services = inspector.list_all_services()
    for domain in list(services.keys())[:5]:
        service_list = services[domain]
        print(f"  {domain}: {', '.join(service_list[:4])}")
        if len(service_list) > 4:
            print(f"         (+ {len(service_list) - 4} more)")

    print("\n✨ Inspector client features:")
    print("  • Higher-level abstraction")
    print("  • Built-in caching for performance")
    print("  • Rich logging with colors and emojis")
    print("  • Convenience properties (.lights, .switches, etc.)")
    print("  • Active entity filtering")
    print("  • Service discovery")
    print("  • Comprehensive system summaries")

    # Show the full summary
    print("\n" + "-"*70)
    inspector.print_summary()


def comparison_summary() -> None:
    """Print a comparison summary"""
    print("\n" + "="*70)
    print("📋 COMPARISON SUMMARY")
    print("="*70 + "\n")

    print("HOMEGROWN CLIENT (ha_client.py)")
    print("  Pros:")
    print("    ✓ Simple, direct REST API access")
    print("    ✓ Full control over requests")
    print("    ✓ Minimal dependencies (just requests)")
    print("    ✓ Includes custom light effects")
    print("    ✓ Easy to understand and modify")
    print("  Cons:")
    print("    ✗ Manual parsing of responses")
    print("    ✗ No built-in caching")
    print("    ✗ Limited high-level abstractions")
    print("    ✗ No WebSocket support")

    print("\nINSPECTOR CLIENT (ha_inspector.py)")
    print("  Pros:")
    print("    ✓ Rich, high-level API")
    print("    ✓ Built-in caching for better performance")
    print("    ✓ Comprehensive logging with colors")
    print("    ✓ Easy entity discovery and filtering")
    print("    ✓ Service introspection")
    print("    ✓ Actively maintained upstream library")
    print("    ✓ WebSocket support available (async)")
    print("  Cons:")
    print("    ✗ Additional dependencies")
    print("    ✗ More abstraction layers")
    print("    ✗ May be overkill for simple use cases")

    print("\nRECOMMENDATIONS:")
    print("  • Use HOMEGROWN for simple control scripts")
    print("  • Use INSPECTOR for discovery, monitoring, and complex queries")
    print("  • Consider using both: Inspector for discovery, homegrown for control")
    print("\n" + "="*70 + "\n")


def main():
    """Run the comparison demo"""
    print("\n🏠 Home Assistant Client Comparison Demo")
    print("="*70)

    try:
        url, token = load_credentials()
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    # Demo both clients
    demo_homegrown_client(url, token)
    demo_inspector_client(url, token)

    # Show comparison
    comparison_summary()

    print("✅ Demo complete!\n")


if __name__ == '__main__':
    main()
