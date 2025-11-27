"""
Routing logic for Road Trip Planning Module

Handles route calculation, geocoding, and distance/time estimates
using multiple APIs with fallback support.
"""

import logging
import requests
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

from .config import (
    get_enabled_apis,
    DEFAULT_SPEEDS_MPH,
    get_unit_preference,
)

logger = logging.getLogger(__name__)


@dataclass
class Location:
    """Represents a geographic location."""
    latitude: float
    longitude: float
    address: str = ""

    def to_tuple(self) -> Tuple[float, float]:
        """Return (lat, lon) tuple."""
        return (self.latitude, self.longitude)

    def format_concise(self) -> str:
        """
        Format location name concisely for voice output.

        Removes verbose country names and unnecessary detail.
        Examples:
            "Big Sur, Monterey County, California, United States of America"
            → "Big Sur in Monterey County, California"

            "San Francisco, California, United States"
            → "San Francisco, California"
        """
        if not self.address:
            return "your destination"

        # Split by commas
        parts = [p.strip() for p in self.address.split(',')]

        # Remove "United States of America" or "United States"
        parts = [p for p in parts if p not in ['United States of America', 'United States', 'USA']]

        # If we have 3+ parts (city, county, state), use "X in Y, Z" format
        if len(parts) >= 3:
            city = parts[0]
            county_or_region = parts[1]
            state = parts[2]
            return f"{city} in {county_or_region}, {state}"

        # Otherwise just join with commas
        return ', '.join(parts[:3])  # Max 3 parts for brevity


@dataclass
class Route:
    """Represents a calculated route."""
    distance_miles: float
    duration_seconds: int
    route_name: str  # e.g., "via I-80 and CA-1"
    geometry: Optional[List[Tuple[float, float]]] = None  # Route coordinates
    start: Optional[Location] = None
    end: Optional[Location] = None

    @property
    def distance_km(self) -> float:
        """Convert distance to kilometers."""
        return self.distance_miles * 1.60934

    @property
    def duration_minutes(self) -> int:
        """Duration in minutes."""
        return int(self.duration_seconds / 60)

    @property
    def duration_hours(self) -> float:
        """Duration in hours."""
        return self.duration_seconds / 3600

    def format_duration(self) -> str:
        """Format duration as human-readable string."""
        hours = int(self.duration_hours)
        minutes = self.duration_minutes % 60

        if hours == 0:
            return f"{minutes} minutes"
        elif minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minutes"

    def format_distance(self, unit_system: str = 'imperial') -> str:
        """Format distance as human-readable string."""
        if unit_system == 'metric':
            return f"{self.distance_km:.1f} km"
        else:
            return f"{self.distance_miles:.1f} miles"


class GeocodingError(Exception):
    """Raised when geocoding fails."""
    pass


class RoutingError(Exception):
    """Raised when route calculation fails."""
    pass


def geocode(address: str, original_query: Optional[str] = None) -> Location:
    """
    Convert address to geographic coordinates.

    Args:
        address: Address string to geocode
        original_query: Optional original user query for disambiguation

    Returns:
        Location object with coordinates

    Raises:
        GeocodingError: If geocoding fails with all APIs
    """
    enabled_apis = get_enabled_apis('geocoding')

    if not enabled_apis:
        raise GeocodingError("No geocoding APIs configured")

    for api_name, api_config in enabled_apis:
        try:
            if api_name == 'nominatim':
                return _geocode_nominatim(address, api_config, original_query)
        except Exception as e:
            logger.warning(f"Geocoding failed with {api_name}: {e}")
            continue

    raise GeocodingError(f"Failed to geocode address: {address}")


def _geocode_nominatim(address: str, config: Dict, original_query: Optional[str] = None) -> Location:
    """Geocode using Nominatim (OpenStreetMap) with LLM disambiguation."""
    url = f"{config['base_url']}/search"
    params = {
        'q': address,
        'format': 'json',
        'limit': 5,  # Get top 5 results for disambiguation
    }
    headers = {
        'User-Agent': 'SagaAssistant/1.0'  # Nominatim requires user agent
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=config.get('timeout', 5)
    )
    response.raise_for_status()

    results = response.json()
    if not results:
        raise GeocodingError(f"No results found for: {address}")

    # Nominatim ranks results by importance/relevance
    # The first result is almost always what the user wants
    # (e.g., "Big Sur" → California, not Kansas)
    result = results[0]

    # Log if there were multiple options (for debugging)
    if len(results) > 1:
        logger.info(f"Geocoding '{address}' found {len(results)} results, using: {result.get('display_name')}")

    return Location(
        latitude=float(result['lat']),
        longitude=float(result['lon']),
        address=result.get('display_name', address)
    )


def calculate_route(
    start: Location,
    end: Location,
    departure_time: Optional[datetime] = None
) -> Route:
    """
    Calculate route between two locations.

    Args:
        start: Starting location
        end: Destination location
        departure_time: Optional departure time (for future traffic)

    Returns:
        Route object with distance, duration, and route info

    Raises:
        RoutingError: If route calculation fails with all APIs
    """
    enabled_apis = get_enabled_apis('routing')

    if not enabled_apis:
        raise RoutingError("No routing APIs configured")

    for api_name, api_config in enabled_apis:
        try:
            if api_name == 'osrm':
                return _calculate_route_osrm(start, end, api_config)
            elif api_name == 'graphhopper':
                return _calculate_route_graphhopper(start, end, api_config)
        except Exception as e:
            logger.warning(f"Routing failed with {api_name}: {e}")
            continue

    raise RoutingError("Failed to calculate route with all APIs")


def _calculate_route_osrm(start: Location, end: Location, config: Dict) -> Route:
    """Calculate route using OSRM."""
    # OSRM uses lon,lat order (not lat,lon!)
    coords = f"{start.longitude},{start.latitude};{end.longitude},{end.latitude}"
    url = f"{config['base_url']}/route/v1/driving/{coords}"

    params = {
        'overview': 'full',
        'steps': 'true',
        'geometries': 'geojson',
    }

    response = requests.get(url, params=params, timeout=config.get('timeout', 10))
    response.raise_for_status()

    data = response.json()

    if data.get('code') != 'Ok' or not data.get('routes'):
        raise RoutingError(f"OSRM returned no routes: {data.get('code')}")

    route_data = data['routes'][0]

    # Extract distance (meters to miles)
    distance_meters = route_data['distance']
    distance_miles = distance_meters * 0.000621371

    # Extract duration (seconds)
    duration_seconds = int(route_data['duration'])

    # Extract route name from legs
    route_name = _extract_route_name_from_osrm(route_data)

    # Extract geometry (coordinates)
    geometry = None
    if 'geometry' in route_data and 'coordinates' in route_data['geometry']:
        # GeoJSON uses lon,lat order
        geometry = [(lat, lon) for lon, lat in route_data['geometry']['coordinates']]

    return Route(
        distance_miles=distance_miles,
        duration_seconds=duration_seconds,
        route_name=route_name,
        geometry=geometry,
        start=start,
        end=end,
    )


def _extract_route_name_from_osrm(route_data: Dict) -> str:
    """Extract primary road names from OSRM route data."""
    road_names = []

    for leg in route_data.get('legs', []):
        for step in leg.get('steps', []):
            name = step.get('name', '')
            if name and name not in road_names and name != '':
                road_names.append(name)

    if not road_names:
        return "route calculated"

    # Take first 2-3 major roads
    major_roads = [r for r in road_names if any(
        prefix in r for prefix in ['I-', 'US-', 'CA-', 'SR-', 'Highway']
    )]

    if major_roads:
        return f"via {' and '.join(major_roads[:3])}"
    else:
        return f"via {' and '.join(road_names[:2])}"


def _calculate_route_graphhopper(start: Location, end: Location, config: Dict) -> Route:
    """Calculate route using GraphHopper."""
    url = f"{config['base_url']}/route"

    params = {
        'point': [
            f"{start.latitude},{start.longitude}",
            f"{end.latitude},{end.longitude}"
        ],
        'vehicle': 'car',
        'locale': 'en',
        'instructions': 'true',
        'calc_points': 'true',
    }

    if config.get('api_key'):
        params['key'] = config['api_key']

    response = requests.get(url, params=params, timeout=config.get('timeout', 10))
    response.raise_for_status()

    data = response.json()

    if 'paths' not in data or not data['paths']:
        raise RoutingError("GraphHopper returned no routes")

    route_data = data['paths'][0]

    # Distance (meters to miles)
    distance_meters = route_data['distance']
    distance_miles = distance_meters * 0.000621371

    # Duration (milliseconds to seconds)
    duration_ms = route_data['time']
    duration_seconds = int(duration_ms / 1000)

    # Extract route name
    route_name = _extract_route_name_from_graphhopper(route_data)

    return Route(
        distance_miles=distance_miles,
        duration_seconds=duration_seconds,
        route_name=route_name,
        start=start,
        end=end,
    )


def _extract_route_name_from_graphhopper(route_data: Dict) -> str:
    """Extract primary road names from GraphHopper route data."""
    road_names = []

    for instruction in route_data.get('instructions', []):
        name = instruction.get('street_name', '')
        if name and name not in road_names:
            road_names.append(name)

    if not road_names:
        return "route calculated"

    # Take first 2-3 roads
    return f"via {' and '.join(road_names[:3])}"


def estimate_route_fallback(start: Location, end: Location) -> Route:
    """
    Estimate route using simple great circle distance and default speeds.
    Used as last resort when all routing APIs fail.

    Args:
        start: Starting location
        end: Destination location

    Returns:
        Route with estimated distance and time
    """
    from math import radians, cos, sin, asin, sqrt

    # Haversine formula for great circle distance
    lon1, lat1, lon2, lat2 = map(radians, [
        start.longitude, start.latitude,
        end.longitude, end.latitude
    ])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    # Earth radius in miles
    r = 3956
    distance_miles = c * r

    # Estimate time using average highway speed
    avg_speed = DEFAULT_SPEEDS_MPH['highway']
    duration_seconds = int((distance_miles / avg_speed) * 3600)

    logger.warning(
        f"Using fallback route estimation: {distance_miles:.1f} miles, "
        f"{duration_seconds/3600:.1f} hours (all routing APIs failed)"
    )

    return Route(
        distance_miles=distance_miles,
        duration_seconds=duration_seconds,
        route_name="estimated route",
        start=start,
        end=end,
    )
