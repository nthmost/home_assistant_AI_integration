"""Home Assistant API client for Saga Assistant.

Provides a simple interface for controlling Home Assistant devices
and querying their states.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

logger = logging.getLogger(__name__)


class HomeAssistantError(Exception):
    """Base exception for Home Assistant client errors."""
    pass


class ConnectionError(HomeAssistantError):
    """Failed to connect to Home Assistant."""
    pass


class AuthenticationError(HomeAssistantError):
    """Authentication failed with Home Assistant."""
    pass


class EntityNotFoundError(HomeAssistantError):
    """Requested entity does not exist."""
    pass


class ServiceCallError(HomeAssistantError):
    """Failed to call Home Assistant service."""
    pass


class HomeAssistantClient:
    """Client for interacting with Home Assistant REST API."""

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        """Initialize the Home Assistant client.

        Args:
            url: Home Assistant URL (default: from HA_URL env var)
            token: Long-lived access token (default: from HA_TOKEN env var)

        Raises:
            ValueError: If URL or token not provided and not in environment
        """
        self.url = (url or os.getenv("HA_URL", "")).rstrip("/")
        self.token = token or os.getenv("HA_TOKEN")

        if not self.url:
            raise ValueError("Home Assistant URL not provided (set HA_URL or pass url parameter)")
        if not self.token:
            raise ValueError("Home Assistant token not provided (set HA_TOKEN or pass token parameter)")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        logger.info(f"Initialized Home Assistant client: {self.url}")

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make a request to the Home Assistant API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/api/states")
            **kwargs: Additional arguments for requests

        Returns:
            Response object

        Raises:
            ConnectionError: If request fails
            AuthenticationError: If authentication fails
        """
        url = f"{self.url}{endpoint}"

        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                timeout=10,
                **kwargs
            )

            if response.status_code == 401:
                raise AuthenticationError("Invalid Home Assistant token")

            response.raise_for_status()
            return response

        except requests.exceptions.Timeout as e:
            raise ConnectionError(f"Request timeout: {e}")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Home Assistant: {e}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid Home Assistant token")
            raise ConnectionError(f"HTTP error: {e}")

    def get_states(self) -> List[Dict[str, Any]]:
        """Get all entity states.

        Returns:
            List of entity state dictionaries
        """
        response = self._request("GET", "/api/states")
        return response.json()

    def get_state(self, entity_id: str) -> Dict[str, Any]:
        """Get state of a specific entity.

        Args:
            entity_id: Entity ID (e.g., "light.living_room")

        Returns:
            Entity state dictionary

        Raises:
            EntityNotFoundError: If entity does not exist
        """
        try:
            response = self._request("GET", f"/api/states/{entity_id}")
            return response.json()
        except ConnectionError as e:
            if "404" in str(e):
                raise EntityNotFoundError(f"Entity not found: {entity_id}")
            raise

    def call_service(
        self,
        domain: str,
        service: str,
        entity_id: Optional[str] = None,
        **service_data
    ) -> List[Dict[str, Any]]:
        """Call a Home Assistant service.

        Args:
            domain: Service domain (e.g., "light", "switch")
            service: Service name (e.g., "turn_on", "turn_off")
            entity_id: Target entity ID (optional)
            **service_data: Additional service data

        Returns:
            List of affected states

        Raises:
            ServiceCallError: If service call fails
        """
        data = {}
        if entity_id:
            data["entity_id"] = entity_id
        data.update(service_data)

        try:
            response = self._request(
                "POST",
                f"/api/services/{domain}/{service}",
                json=data
            )
            return response.json()
        except ConnectionError as e:
            raise ServiceCallError(f"Failed to call service {domain}.{service}: {e}")

    def turn_on(self, entity_id: str, **kwargs) -> List[Dict[str, Any]]:
        """Turn on a device.

        Args:
            entity_id: Entity ID (e.g., "light.living_room")
            **kwargs: Additional parameters (brightness, color, etc.)

        Returns:
            List of affected states
        """
        domain = entity_id.split(".")[0]
        return self.call_service(domain, "turn_on", entity_id=entity_id, **kwargs)

    def turn_off(self, entity_id: str, **kwargs) -> List[Dict[str, Any]]:
        """Turn off a device.

        Args:
            entity_id: Entity ID (e.g., "light.living_room")
            **kwargs: Additional parameters

        Returns:
            List of affected states
        """
        domain = entity_id.split(".")[0]
        return self.call_service(domain, "turn_off", entity_id=entity_id, **kwargs)

    def toggle(self, entity_id: str, **kwargs) -> List[Dict[str, Any]]:
        """Toggle a device.

        Args:
            entity_id: Entity ID (e.g., "light.living_room")
            **kwargs: Additional parameters

        Returns:
            List of affected states
        """
        domain = entity_id.split(".")[0]
        return self.call_service(domain, "toggle", entity_id=entity_id, **kwargs)

    def get_entities_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get all entities for a specific domain.

        Args:
            domain: Domain name (e.g., "light", "switch", "sensor")

        Returns:
            List of entity states matching the domain
        """
        all_states = self.get_states()
        return [
            state for state in all_states
            if state["entity_id"].startswith(f"{domain}.")
        ]

    def search_entities(self, query: str) -> List[Dict[str, Any]]:
        """Search for entities by name or entity_id.

        Args:
            query: Search query (case-insensitive)

        Returns:
            List of matching entity states
        """
        all_states = self.get_states()
        query_lower = query.lower()

        matches = []
        for state in all_states:
            entity_id = state["entity_id"].lower()
            friendly_name = state.get("attributes", {}).get("friendly_name", "").lower()

            if query_lower in entity_id or query_lower in friendly_name:
                matches.append(state)

        return matches

    def is_on(self, entity_id: str) -> bool:
        """Check if a device is on.

        Args:
            entity_id: Entity ID

        Returns:
            True if device is on, False otherwise
        """
        state = self.get_state(entity_id)
        return state["state"] == "on"

    def get_config(self) -> Dict[str, Any]:
        """Get Home Assistant configuration.

        Returns:
            Configuration dictionary
        """
        response = self._request("GET", "/api/config")
        return response.json()

    def check_health(self) -> bool:
        """Check if Home Assistant is responding.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = self._request("GET", "/api/")
            return response.json().get("message") == "API running."
        except (ConnectionError, AuthenticationError):
            return False


def main():
    """Quick test of Home Assistant client."""
    logging.basicConfig(level=logging.INFO)

    try:
        client = HomeAssistantClient()

        # Health check
        print("🔌 Testing connection...")
        if client.check_health():
            print("✅ Connected to Home Assistant!")
        else:
            print("❌ Failed to connect")
            return

        # Get config
        config = client.get_config()
        print(f"\n🏠 Location: {config.get('location_name', 'Unknown')}")
        print(f"🌐 URL: {client.url}")
        print(f"🔢 Version: {config.get('version', 'Unknown')}")

        # Get all entities
        print("\n📊 Fetching entities...")
        states = client.get_states()
        print(f"   Found {len(states)} total entities")

        # Show entities by domain
        domains = {}
        for state in states:
            domain = state["entity_id"].split(".")[0]
            domains[domain] = domains.get(domain, 0) + 1

        print("\n📦 Entities by domain:")
        for domain, count in sorted(domains.items(), key=lambda x: -x[1])[:10]:
            print(f"   {domain:20s} {count:3d}")

        # Show some lights
        lights = client.get_entities_by_domain("light")
        if lights:
            print(f"\n💡 Sample lights ({len(lights)} total):")
            for light in lights[:5]:
                name = light.get("attributes", {}).get("friendly_name", light["entity_id"])
                state = light["state"]
                print(f"   {name:30s} [{state}]")

        # Show some switches
        switches = client.get_entities_by_domain("switch")
        if switches:
            print(f"\n🔌 Sample switches ({len(switches)} total):")
            for switch in switches[:5]:
                name = switch.get("attributes", {}).get("friendly_name", switch["entity_id"])
                state = switch["state"]
                print(f"   {name:30s} [{state}]")

    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
