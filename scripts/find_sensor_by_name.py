#!/usr/bin/env python3
"""
Find and display all entities matching a search term (case-insensitive).
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ha_core.client import HomeAssistantInspector
from ha_core.config import load_credentials

# Configure logging
logging.basicConfig(level=logging.WARNING)


def find_entities_by_name(inspector, search_term: str):
    """Find all entities containing the search term in ID or friendly name."""
    search_lower = search_term.lower()
    found = []

    all_entities_dict = inspector.entities

    for domain, group in all_entities_dict.items():
        for entity_id, entity in group.entities.items():
            attrs = entity.state.attributes if entity.state else {}
            friendly_name = attrs.get('friendly_name', '')

            # Check if search term is in entity_id or friendly_name
            if search_lower in entity_id.lower() or search_lower in friendly_name.lower():
                found.append({
                    'entity_id': entity_id,
                    'domain': domain,
                    'friendly_name': friendly_name,
                    'state': entity.state.state if entity.state else 'unknown',
                    'attributes': attrs
                })

    return found


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_sensor_by_name.py <search_term>")
        print("Example: python find_sensor_by_name.py abigail")
        sys.exit(1)

    search_term = sys.argv[1]
    print(f"\n🔍 Searching for entities containing '{search_term}'...\n")

    # Load credentials and connect
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=logging.WARNING)

    # Find matching entities
    matches = find_entities_by_name(inspector, search_term)

    if not matches:
        print(f"❌ No entities found matching '{search_term}'\n")
        return

    print(f"✅ Found {len(matches)} matching entit{'y' if len(matches) == 1 else 'ies'}:\n")
    print("=" * 80)

    for match in matches:
        print(f"\n📍 {match['entity_id']}")
        print(f"   Domain: {match['domain']}")
        print(f"   Name: {match['friendly_name']}")
        print(f"   State: {match['state']}")

        # Show key attributes
        attrs = match['attributes']
        important_keys = [
            'device_class', 'unit_of_measurement', 'state_class',
            'battery', 'temperature', 'humidity', 'moisture',
            'illuminance', 'pressure', 'conductivity',
            'voltage', 'last_seen', 'linkquality'
        ]

        attr_shown = False
        for key in important_keys:
            if key in attrs:
                print(f"   {key.replace('_', ' ').title()}: {attrs[key]}")
                attr_shown = True

        # Show all other attributes
        other_attrs = {k: v for k, v in attrs.items()
                      if k not in important_keys
                      and k not in ['friendly_name', 'icon', 'entity_picture']
                      and not k.startswith('_')}

        if other_attrs:
            print(f"   Other attributes:")
            for k, v in sorted(other_attrs.items()):
                # Truncate long values
                v_str = str(v)
                if len(v_str) > 100:
                    v_str = v_str[:100] + "..."
                print(f"      • {k}: {v_str}")

    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    main()
