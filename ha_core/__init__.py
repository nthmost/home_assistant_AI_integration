"""
Home Assistant Core

A clean Python interface for Home Assistant using the HomeAssistant-API library.

This module provides:
- HomeAssistantInspector: High-level API for discovering and querying HA entities
- Credential management: Load HA credentials from .env or environment variables
- Colorful logging: Enhanced visibility for debugging and monitoring

Example:
    from ha_core import HomeAssistantInspector, load_credentials

    url, token = load_credentials()
    inspector = HomeAssistantInspector(url, token)

    # Get all lights
    lights = inspector.lights

    # Get active entities only
    active = inspector.get_active_entities()

    # Print system summary
    inspector.print_summary()
"""

from .client import HomeAssistantInspector, setup_logger
from .config import load_credentials, get_ha_url, get_ha_token

__all__ = [
    'HomeAssistantInspector',
    'setup_logger',
    'load_credentials',
    'get_ha_url',
    'get_ha_token',
]

__version__ = '0.2.0'
