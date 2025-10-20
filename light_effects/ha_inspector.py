"""
Home Assistant Inspector Module
Uses the HomeAssistant-API library to provide a class-based interface
for discovering and understanding what's on your Home Assistant box.
"""

import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from collections import defaultdict

try:
    from homeassistant_api import Client
    from homeassistant_api.models import Entity, State, Domain, Service
except ImportError as e:
    raise ImportError(
        "HomeAssistant-API library not found. Install with: pip install HomeAssistant-API"
    ) from e


# Configure colorful logging
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and emojis for better readability"""

    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'

    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥',
    }

    def format(self, record):
        emoji = self.EMOJIS.get(record.levelname, '•')
        color = self.COLORS.get(record.levelname, '')
        record.emoji = emoji
        record.color = color
        record.reset = self.RESET
        return super().format(record)


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up a colorful logger for this module"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = ColoredFormatter(
            '%(color)s%(emoji)s [%(levelname)s]%(reset)s %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


class HomeAssistantInspector:
    """
    A class-based interface for inspecting and understanding your Home Assistant setup.

    This wraps the HomeAssistant-API library to provide easy access to:
    - What devices and entities are available
    - What's currently active/on/running
    - What services and domains are configured
    - System configuration and status

    Example:
        inspector = HomeAssistantInspector(
            url="http://homeassistant.local:8123",
            token="your-long-lived-access-token"
        )

        # Get all lights
        lights = inspector.get_entities_by_domain('light')

        # Get only active entities
        active = inspector.get_active_entities()

        # Check system status
        if inspector.is_running:
            print(f"HA version: {inspector.version}")
    """

    def __init__(
        self,
        url: str,
        token: str,
        log_level: int = logging.INFO,
        verify_ssl: bool = True
    ):
        """
        Initialize the Home Assistant Inspector

        Args:
            url: Base URL of Home Assistant (e.g., "http://homeassistant.local:8123")
            token: Long-lived access token from HA
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            verify_ssl: Whether to verify SSL certificates
        """
        self.logger = setup_logger(__name__, log_level)

        # Ensure URL includes /api
        api_url = url.rstrip('/') + '/api' if not url.endswith('/api') else url

        self.logger.info(f"Initializing HA Inspector for {api_url}")

        try:
            self.client = Client(api_url, token, verify_ssl=verify_ssl)
            self._verify_connection()
        except ConnectionError as e:
            self.logger.error(f"Failed to connect to Home Assistant: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during initialization: {e}")
            raise

        # Cache for expensive operations
        self._entities_cache: Optional[Dict[str, Any]] = None
        self._domains_cache: Optional[Dict[str, Domain]] = None
        self._config_cache: Optional[Dict[str, Any]] = None

        self.logger.info("HA Inspector initialized successfully")

    def _verify_connection(self) -> None:
        """Verify we can connect to Home Assistant"""
        try:
            if not self.client.check_api_running():
                raise ConnectionError("Home Assistant API is not responding")
            self.logger.debug("Connection verified - API is running")
        except Exception as e:
            self.logger.error(f"Connection verification failed: {e}")
            raise ConnectionError(f"Cannot connect to Home Assistant: {e}") from e

    def refresh_cache(self) -> None:
        """Clear all caches to force fresh data on next access"""
        self.logger.debug("Clearing all caches")
        self._entities_cache = None
        self._domains_cache = None
        self._config_cache = None

    # ============================================================================
    # System Status & Configuration
    # ============================================================================

    @property
    def is_running(self) -> bool:
        """Check if Home Assistant is currently running"""
        try:
            return self.client.check_api_running()
        except Exception as e:
            self.logger.warning(f"Failed to check running status: {e}")
            return False

    @property
    def config(self) -> Dict[str, Any]:
        """Get Home Assistant configuration"""
        if self._config_cache is None:
            self.logger.debug("Fetching HA configuration")
            try:
                self._config_cache = self.client.get_config()
            except Exception as e:
                self.logger.error(f"Failed to get config: {e}")
                raise
        return self._config_cache

    @property
    def version(self) -> str:
        """Get Home Assistant version"""
        return self.config.get('version', 'unknown')

    @property
    def location_name(self) -> str:
        """Get configured location name"""
        return self.config.get('location_name', 'unknown')

    @property
    def components(self) -> tuple:
        """Get all registered components"""
        try:
            self.logger.debug("Fetching components")
            return self.client.get_components()
        except Exception as e:
            self.logger.error(f"Failed to get components: {e}")
            return tuple()

    # ============================================================================
    # Entity Discovery & Querying
    # ============================================================================

    @property
    def entities(self) -> Dict[str, Any]:
        """Get all entities (cached)"""
        if self._entities_cache is None:
            self.logger.info("Fetching all entities from HA")
            try:
                self._entities_cache = self.client.get_entities()
                entity_count = sum(len(group.entities) for group in self._entities_cache.values())
                self.logger.info(f"Retrieved {entity_count} entities across {len(self._entities_cache)} groups")
            except Exception as e:
                self.logger.error(f"Failed to fetch entities: {e}")
                raise
        return self._entities_cache

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Get a specific entity by ID

        Args:
            entity_id: Full entity ID (e.g., "light.living_room")

        Returns:
            Entity object or None if not found
        """
        self.logger.debug(f"Fetching entity: {entity_id}")
        try:
            return self.client.get_entity(entity_id=entity_id)
        except Exception as e:
            self.logger.warning(f"Failed to get entity {entity_id}: {e}")
            return None

    def get_entities_by_domain(self, domain: str) -> List[Entity]:
        """
        Get all entities for a specific domain (e.g., 'light', 'switch', 'sensor')

        Args:
            domain: Domain name (e.g., 'light', 'switch', 'sensor')

        Returns:
            List of Entity objects
        """
        self.logger.debug(f"Getting entities for domain: {domain}")
        entities = []

        try:
            groups = self.entities
            if domain in groups:
                # entities is a dict, get the values (Entity objects)
                entities = list(groups[domain].entities.values())
                self.logger.info(f"Found {len(entities)} entities in domain '{domain}'")
            else:
                self.logger.warning(f"Domain '{domain}' not found")
        except Exception as e:
            self.logger.error(f"Error fetching entities for domain {domain}: {e}")

        return entities

    def get_active_entities(self, domains: Optional[List[str]] = None) -> Dict[str, List[Entity]]:
        """
        Get all currently active entities (state != 'off' or 'unavailable')

        Args:
            domains: Optional list of domains to filter (e.g., ['light', 'switch'])

        Returns:
            Dictionary mapping domain names to lists of active entities
        """
        self.logger.info("Filtering for active entities")
        active = defaultdict(list)
        inactive_states = {'off', 'unavailable', 'unknown', 'idle'}

        try:
            for domain, group in self.entities.items():
                # Skip if we're filtering domains and this isn't in the list
                if domains and domain not in domains:
                    continue

                # group.entities is a dict, iterate over values (Entity objects)
                for entity in group.entities.values():
                    # Handle cases where entity might not have state
                    if not hasattr(entity, 'state') or entity.state is None:
                        self.logger.debug(f"Skipping entity without state: {entity}")
                        continue

                    # Get state string - entity.state is a State object with .state attribute
                    state = entity.state.state.lower() if hasattr(entity.state, 'state') else 'unknown'

                    if state not in inactive_states:
                        active[domain].append(entity)
        except Exception as e:
            self.logger.error(f"Error filtering active entities: {e}")
            import traceback
            self.logger.debug(f"Traceback: {traceback.format_exc()}")

        total_active = sum(len(entities) for entities in active.values())
        self.logger.info(f"Found {total_active} active entities across {len(active)} domains")

        return dict(active)

    def list_domains(self) -> List[str]:
        """Get a list of all available entity domains"""
        try:
            domains = list(self.entities.keys())
            self.logger.debug(f"Found {len(domains)} domains")
            return sorted(domains)
        except Exception as e:
            self.logger.error(f"Error listing domains: {e}")
            return []

    def get_entity_count(self) -> int:
        """Get total count of all entities"""
        try:
            count = sum(len(group.entities) for group in self.entities.values())
            return count
        except Exception as e:
            self.logger.error(f"Error counting entities: {e}")
            return 0

    def get_domain_summary(self) -> Dict[str, int]:
        """
        Get a summary of entity counts by domain

        Returns:
            Dictionary mapping domain names to entity counts
        """
        self.logger.debug("Generating domain summary")
        summary = {}
        try:
            for domain, group in self.entities.items():
                summary[domain] = len(group.entities)
        except Exception as e:
            self.logger.error(f"Error generating domain summary: {e}")

        return summary

    # ============================================================================
    # Service Discovery
    # ============================================================================

    @property
    def domains(self) -> Dict[str, Domain]:
        """Get all service domains (cached)"""
        if self._domains_cache is None:
            self.logger.info("Fetching service domains")
            try:
                self._domains_cache = self.client.get_domains()
                self.logger.info(f"Retrieved {len(self._domains_cache)} service domains")
            except Exception as e:
                self.logger.error(f"Failed to fetch domains: {e}")
                raise
        return self._domains_cache

    def get_services_for_domain(self, domain: str) -> Optional[Domain]:
        """
        Get all available services for a specific domain

        Args:
            domain: Domain name (e.g., 'light', 'switch')

        Returns:
            Domain object containing services, or None if not found
        """
        self.logger.debug(f"Getting services for domain: {domain}")
        try:
            return self.domains.get(domain)
        except Exception as e:
            self.logger.error(f"Error getting services for domain {domain}: {e}")
            return None

    def list_all_services(self) -> Dict[str, List[str]]:
        """
        Get a mapping of all domains to their available services

        Returns:
            Dictionary mapping domain names to lists of service names
        """
        self.logger.debug("Listing all services")
        services_map = {}
        try:
            for domain_name, domain in self.domains.items():
                services_map[domain_name] = list(domain.services.keys())
        except Exception as e:
            self.logger.error(f"Error listing services: {e}")

        return services_map

    # ============================================================================
    # Convenience Properties
    # ============================================================================

    @property
    def lights(self) -> List[Entity]:
        """Get all light entities"""
        return self.get_entities_by_domain('light')

    @property
    def switches(self) -> List[Entity]:
        """Get all switch entities"""
        return self.get_entities_by_domain('switch')

    @property
    def sensors(self) -> List[Entity]:
        """Get all sensor entities"""
        return self.get_entities_by_domain('sensor')

    @property
    def binary_sensors(self) -> List[Entity]:
        """Get all binary sensor entities"""
        return self.get_entities_by_domain('binary_sensor')

    @property
    def automations(self) -> List[Entity]:
        """Get all automation entities"""
        return self.get_entities_by_domain('automation')

    @property
    def scripts(self) -> List[Entity]:
        """Get all script entities"""
        return self.get_entities_by_domain('script')

    # ============================================================================
    # Summary & Reporting
    # ============================================================================

    def print_summary(self) -> None:
        """Print a formatted summary of the Home Assistant setup"""
        print("\n" + "="*60)
        print(f"🏠 Home Assistant Summary: {self.location_name}")
        print("="*60)
        print(f"Version: {self.version}")
        print(f"Status: {'✅ Running' if self.is_running else '❌ Not Running'}")
        print(f"\n📊 Entity Overview:")
        print("-" * 60)

        summary = self.get_domain_summary()
        total = sum(summary.values())

        for domain, count in sorted(summary.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * min(count // 2, 30)
            print(f"  {domain:20s}: {count:4d} {bar}")

        print("-" * 60)
        print(f"Total Entities: {total}")

        print(f"\n🔧 Active Components: {len(self.components)}")
        print(f"🎯 Service Domains: {len(self.domains)}")

        # Show active entities
        active = self.get_active_entities()
        active_count = sum(len(entities) for entities in active.values())
        print(f"\n⚡ Currently Active: {active_count} entities")

        for domain, entities in sorted(active.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {domain}: {len(entities)} active")

        print("="*60 + "\n")

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get comprehensive system information

        Returns:
            Dictionary with system info including version, config, counts, etc.
        """
        self.logger.debug("Gathering system info")

        return {
            'version': self.version,
            'location_name': self.location_name,
            'is_running': self.is_running,
            'config': self.config,
            'entity_count': self.get_entity_count(),
            'domain_summary': self.get_domain_summary(),
            'component_count': len(self.components),
            'service_domain_count': len(self.domains),
            'active_entities': {
                domain: len(entities)
                for domain, entities in self.get_active_entities().items()
            }
        }
