"""
Configuration for Road Trip Planning Module

API keys, endpoints, and fallback configuration.
"""

import os
from typing import Dict, Any

# Distance unit based on locale (miles or km)
DEFAULT_UNIT_SYSTEM = 'imperial'  # 'imperial' or 'metric'

# Routing APIs (in priority order)
ROUTING_APIS = {
    'osrm': {
        'enabled': True,
        'base_url': 'https://router.project-osrm.org',
        'priority': 1,
        'timeout': 10,
    },
    'graphhopper': {
        'enabled': True,
        'base_url': 'https://graphhopper.com/api/1',
        'api_key': os.getenv('GRAPHHOPPER_API_KEY'),
        'priority': 2,
        'timeout': 10,
    },
}

# Traffic APIs (in priority order)
TRAFFIC_APIS = {
    'tomtom': {
        'enabled': bool(os.getenv('TOMTOM_API_KEY')),
        'api_key': os.getenv('TOMTOM_API_KEY'),
        'base_url': 'https://api.tomtom.com',
        'daily_limit': 2500,
        'priority': 1,
        'timeout': 10,
    },
    'here': {
        'enabled': bool(os.getenv('HERE_API_KEY')),
        'api_key': os.getenv('HERE_API_KEY'),
        'base_url': 'https://traffic.ls.hereapi.com/traffic/6.3',
        'monthly_limit': 250000,
        'priority': 2,
        'timeout': 10,
    },
}

# POI APIs
POI_APIS = {
    'overpass': {
        'enabled': True,
        'base_url': 'https://overpass-api.de/api',
        'timeout': 15,
        'priority': 1,
    },
}

# Geocoding APIs
GEOCODING_APIS = {
    'nominatim': {
        'enabled': True,
        'base_url': 'https://nominatim.openstreetmap.org',
        'timeout': 5,
        'priority': 1,
    },
}

# POI search parameters
POI_SEARCH_RADIUS_MILES = 5  # How far from route to search for POIs
POI_CATEGORIES = {
    'natural_landmarks': [
        'national_park',
        'state_park',
        'nature_reserve',
        'viewpoint',
        'peak',
        'beach',
        'waterfall',
        'cave',
        'hot_spring',
    ],
}

# Departure time optimization
DEPARTURE_TIME_WINDOW_HOURS = 24  # Look ahead this many hours
DEPARTURE_TIME_INTERVAL_MINUTES = 30  # Check every N minutes
MAX_ALTERNATIVE_TIMES = 3  # Maximum alternative departure times to suggest

# Speed assumptions (when traffic data unavailable)
DEFAULT_SPEEDS_MPH = {
    'highway': 65,
    'trunk': 55,
    'primary': 45,
    'secondary': 35,
    'tertiary': 25,
    'residential': 25,
}

# Response configuration
VERY_CLOSE_THRESHOLD_MILES = 5
VERY_FAR_THRESHOLD_MILES = 500
MULTIDAY_TRIP_THRESHOLD_HOURS = 10


def get_unit_preference(ha_config: Dict[str, Any] = None) -> str:
    """
    Get distance unit preference from Home Assistant config.

    Args:
        ha_config: Home Assistant configuration dict

    Returns:
        'imperial' or 'metric'
    """
    if ha_config and 'unit_system' in ha_config:
        unit_system = ha_config['unit_system'].get('name', '').lower()
        if 'metric' in unit_system:
            return 'metric'
    return DEFAULT_UNIT_SYSTEM


def get_enabled_apis(api_category: str) -> list:
    """
    Get list of enabled APIs for a category, sorted by priority.

    Args:
        api_category: 'routing', 'traffic', 'poi', or 'geocoding'

    Returns:
        List of (api_name, config) tuples sorted by priority
    """
    api_configs = {
        'routing': ROUTING_APIS,
        'traffic': TRAFFIC_APIS,
        'poi': POI_APIS,
        'geocoding': GEOCODING_APIS,
    }

    if api_category not in api_configs:
        return []

    apis = api_configs[api_category]
    enabled = [(name, cfg) for name, cfg in apis.items() if cfg.get('enabled', False)]
    return sorted(enabled, key=lambda x: x[1].get('priority', 999))
