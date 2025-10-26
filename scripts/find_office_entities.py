#!/usr/bin/env python3
"""
Search for office-related entities across all domains
"""

import logging
from ha_core import HomeAssistantInspector, load_credentials

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def find_office_entities():
    """Search for office-related entities"""
    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token, log_level=40)

    logger.info("🔍 Searching for office-related entities...")
    logger.info("=" * 60)

    # Get all entities from all domains
    all_entities = []
    entity_groups = inspector.entities  # Returns dict of domain -> EntityGroup

    for domain, group in entity_groups.items():
        # group.entities is a dict of entity_id -> Entity
        all_entities.extend(group.entities.values())

    logger.info(f"\n📊 Total entities: {len(all_entities)}")

    # Search for office/LED related entities
    search_terms = ['office', 'led', 'broadlink']

    matches = []
    for entity in all_entities:
        entity_id = entity.entity_id.lower()
        friendly_name = ""

        if hasattr(entity.state, 'attributes') and 'friendly_name' in entity.state.attributes:
            friendly_name = entity.state.attributes['friendly_name'].lower()

        for term in search_terms:
            if term in entity_id or term in friendly_name:
                matches.append(entity)
                break

    logger.info(f"\n🎯 Found {len(matches)} matching entities:")
    logger.info("")

    # Group by domain
    by_domain = {}
    for entity in matches:
        domain = entity.entity_id.split('.')[0]
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(entity)

    # Display grouped results
    for domain in sorted(by_domain.keys()):
        entities = by_domain[domain]
        logger.info(f"📁 {domain.upper()} ({len(entities)} entities):")

        for entity in entities:
            state = entity.state.state
            friendly_name = entity.entity_id

            if hasattr(entity.state, 'attributes') and 'friendly_name' in entity.state.attributes:
                friendly_name = entity.state.attributes['friendly_name']

            # Show last changed if available
            last_changed = "unknown"
            if hasattr(entity.state, 'last_changed'):
                last_changed = entity.state.last_changed

            logger.info(f"   • {entity.entity_id}")
            logger.info(f"     Name: {friendly_name}")
            logger.info(f"     State: {state}")
            logger.info(f"     Last changed: {last_changed}")
            logger.info("")

    logger.info("=" * 60)
    logger.info("💡 If office lights are switches, they won't appear in the light dashboard")
    logger.info("   You can either:")
    logger.info("   1. Create a separate switch dashboard")
    logger.info("   2. Expose switches as lights via HA template or switch_as_x integration")
    logger.info("   3. Add switch support to the existing dashboard")


if __name__ == "__main__":
    find_office_entities()
