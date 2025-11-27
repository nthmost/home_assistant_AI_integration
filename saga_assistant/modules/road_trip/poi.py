"""
Points of Interest queries for Road Trip Planning Module

Finds natural landmarks and interesting stops along routes using OpenStreetMap data.
"""

import logging
import requests
from typing import List, Optional, Tuple
from dataclasses import dataclass
from math import radians, cos, sin, asin, sqrt

from .config import POI_SEARCH_RADIUS_MILES, POI_CATEGORIES, get_enabled_apis
from .routing import Route, Location

logger = logging.getLogger(__name__)


@dataclass
class PointOfInterest:
    """Represents a point of interest along a route."""
    name: str
    category: str  # 'park', 'viewpoint', 'beach', etc.
    location: Location
    distance_from_route_miles: float
    description: Optional[str] = None
    estimated_stop_duration_minutes: Optional[int] = None

    def format_description(self) -> str:
        """Format POI as human-readable description."""
        parts = [self.name]

        if self.distance_from_route_miles < 0.5:
            parts.append("right on your route")
        else:
            parts.append(f"{self.distance_from_route_miles:.1f} miles off route")

        if self.estimated_stop_duration_minutes:
            parts.append(f"good for a {self.estimated_stop_duration_minutes}-minute stop")

        if self.description:
            parts.append(self.description)

        return " - ".join(parts)


class POIError(Exception):
    """Raised when POI search fails."""
    pass


def find_pois_along_route(
    route: Route,
    categories: Optional[List[str]] = None,
    max_results: int = 5
) -> List[PointOfInterest]:
    """
    Find points of interest along a route.

    Args:
        route: Route to search along
        categories: POI categories to search for (default: natural landmarks)
        max_results: Maximum number of POIs to return

    Returns:
        List of PointOfInterest objects sorted by proximity to route
    """
    if not route.geometry:
        logger.warning("Route has no geometry, cannot search for POIs")
        return []

    # Use natural landmarks by default
    if not categories:
        categories = POI_CATEGORIES['natural_landmarks']

    enabled_apis = get_enabled_apis('poi')

    if not enabled_apis:
        logger.warning("No POI APIs configured")
        return []

    # Try each API
    for api_name, api_config in enabled_apis:
        try:
            if api_name == 'overpass':
                return _find_pois_overpass(route, categories, max_results, api_config)
        except Exception as e:
            logger.warning(f"POI search failed with {api_name}: {e}")
            continue

    logger.warning("All POI APIs failed")
    return []


def _find_pois_overpass(
    route: Route,
    categories: List[str],
    max_results: int,
    config: dict
) -> List[PointOfInterest]:
    """Find POIs using Overpass API (OpenStreetMap)."""

    # Create bounding box around route
    bbox = _create_route_bbox(route, POI_SEARCH_RADIUS_MILES)

    # Build Overpass query
    query = _build_overpass_query(bbox, categories)

    # Query Overpass API
    url = f"{config['base_url']}/interpreter"

    response = requests.post(
        url,
        data={'data': query},
        timeout=config.get('timeout', 15)
    )
    response.raise_for_status()

    data = response.json()

    # Parse results
    pois = []
    for element in data.get('elements', []):
        poi = _parse_overpass_element(element, route)
        if poi:
            pois.append(poi)

    # Sort by distance from route
    pois.sort(key=lambda p: p.distance_from_route_miles)

    return pois[:max_results]


def _create_route_bbox(route: Route, radius_miles: float) -> dict:
    """Create bounding box around route with buffer radius."""
    if not route.geometry:
        # Fallback to start/end points
        if route.start and route.end:
            lats = [route.start.latitude, route.end.latitude]
            lons = [route.start.longitude, route.end.longitude]
        else:
            raise ValueError("Route has no geometry or start/end points")
    else:
        lats = [coord[0] for coord in route.geometry]
        lons = [coord[1] for coord in route.geometry]

    # Convert miles to degrees (approximate)
    # 1 degree latitude ≈ 69 miles
    buffer_degrees = radius_miles / 69.0

    return {
        'south': min(lats) - buffer_degrees,
        'north': max(lats) + buffer_degrees,
        'west': min(lons) - buffer_degrees,
        'east': max(lons) + buffer_degrees,
    }


def _build_overpass_query(bbox: dict, categories: List[str]) -> str:
    """
    Build Overpass QL query for POI search.

    Args:
        bbox: Bounding box dict with south, north, west, east
        categories: List of POI categories to search for

    Returns:
        Overpass QL query string
    """
    # Map our categories to OSM tags
    tag_filters = []

    for category in categories:
        if category == 'national_park':
            tag_filters.append('node["boundary"="national_park"]')
            tag_filters.append('way["boundary"="national_park"]')
        elif category == 'state_park':
            tag_filters.append('node["leisure"="park"]["park:type"="state_park"]')
            tag_filters.append('way["leisure"="park"]["park:type"="state_park"]')
        elif category == 'nature_reserve':
            tag_filters.append('node["leisure"="nature_reserve"]')
            tag_filters.append('way["leisure"="nature_reserve"]')
        elif category == 'viewpoint':
            tag_filters.append('node["tourism"="viewpoint"]')
        elif category == 'peak':
            tag_filters.append('node["natural"="peak"]')
        elif category == 'beach':
            tag_filters.append('node["natural"="beach"]')
            tag_filters.append('way["natural"="beach"]')
        elif category == 'waterfall':
            tag_filters.append('node["waterway"="waterfall"]')
        elif category == 'cave':
            tag_filters.append('node["natural"="cave_entrance"]')
        elif category == 'hot_spring':
            tag_filters.append('node["natural"="hot_spring"]')

    # Build query
    bbox_str = f"{bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']}"

    query_parts = ['[out:json][timeout:15];', '(']
    for tag_filter in tag_filters:
        query_parts.append(f'  {tag_filter}({bbox_str});')
    query_parts.append(');')
    query_parts.append('out center;')

    return '\n'.join(query_parts)


def _parse_overpass_element(element: dict, route: Route) -> Optional[PointOfInterest]:
    """Parse Overpass API element into PointOfInterest."""
    try:
        # Get coordinates
        if element['type'] == 'node':
            lat = element['lat']
            lon = element['lon']
        elif 'center' in element:
            lat = element['center']['lat']
            lon = element['center']['lon']
        else:
            return None

        location = Location(latitude=lat, longitude=lon)

        # Get name
        tags = element.get('tags', {})
        name = tags.get('name')
        if not name:
            return None  # Skip unnamed features

        # Determine category
        category = _categorize_element(tags)

        # Calculate distance from route
        distance_miles = _distance_to_route(location, route)

        # Estimate stop duration based on category
        stop_duration = _estimate_stop_duration(category, tags)

        # Get description
        description = tags.get('description') or _generate_description(category, tags)

        return PointOfInterest(
            name=name,
            category=category,
            location=location,
            distance_from_route_miles=distance_miles,
            description=description,
            estimated_stop_duration_minutes=stop_duration
        )

    except Exception as e:
        logger.warning(f"Failed to parse POI element: {e}")
        return None


def _categorize_element(tags: dict) -> str:
    """Determine POI category from OSM tags."""
    if tags.get('boundary') == 'national_park':
        return 'national_park'
    elif tags.get('boundary') == 'protected_area' or tags.get('leisure') == 'nature_reserve':
        return 'nature_reserve'
    elif tags.get('tourism') == 'viewpoint':
        return 'viewpoint'
    elif tags.get('natural') == 'peak':
        return 'peak'
    elif tags.get('natural') == 'beach':
        return 'beach'
    elif tags.get('waterway') == 'waterfall':
        return 'waterfall'
    elif tags.get('natural') == 'cave_entrance':
        return 'cave'
    elif tags.get('natural') == 'hot_spring':
        return 'hot_spring'
    elif tags.get('leisure') == 'park':
        return 'park'
    else:
        return 'landmark'


def _distance_to_route(location: Location, route: Route) -> float:
    """
    Calculate minimum distance from location to any point on route.

    Args:
        location: Point to measure from
        route: Route with geometry

    Returns:
        Distance in miles
    """
    if not route.geometry:
        # Fallback: distance to midpoint between start and end
        if route.start and route.end:
            mid_lat = (route.start.latitude + route.end.latitude) / 2
            mid_lon = (route.start.longitude + route.end.longitude) / 2
            mid_point = Location(latitude=mid_lat, longitude=mid_lon)
            return _haversine_distance(location, mid_point)
        return 0.0

    # Find minimum distance to any point on route
    min_distance = float('inf')

    for route_point in route.geometry:
        route_loc = Location(latitude=route_point[0], longitude=route_point[1])
        distance = _haversine_distance(location, route_loc)
        min_distance = min(min_distance, distance)

    return min_distance


def _haversine_distance(loc1: Location, loc2: Location) -> float:
    """
    Calculate great circle distance between two locations.

    Args:
        loc1: First location
        loc2: Second location

    Returns:
        Distance in miles
    """
    # Convert to radians
    lon1, lat1, lon2, lat2 = map(radians, [
        loc1.longitude, loc1.latitude,
        loc2.longitude, loc2.latitude
    ])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    # Earth radius in miles
    r = 3956

    return c * r


def _estimate_stop_duration(category: str, tags: dict) -> int:
    """Estimate how long to spend at a POI (in minutes)."""
    duration_map = {
        'viewpoint': 15,
        'beach': 45,
        'waterfall': 30,
        'peak': 60,
        'cave': 45,
        'hot_spring': 60,
        'national_park': 120,
        'state_park': 90,
        'nature_reserve': 60,
        'park': 30,
    }

    return duration_map.get(category, 30)


def _generate_description(category: str, tags: dict) -> str:
    """Generate description for POI based on category and tags."""
    descriptions = {
        'viewpoint': 'Scenic viewpoint',
        'beach': 'Beach area',
        'waterfall': 'Natural waterfall',
        'peak': 'Mountain peak',
        'cave': 'Cave entrance',
        'hot_spring': 'Natural hot spring',
        'national_park': 'National park',
        'state_park': 'State park',
        'nature_reserve': 'Nature reserve',
    }

    base_desc = descriptions.get(category, 'Point of interest')

    # Add elevation for peaks
    if category == 'peak' and 'ele' in tags:
        try:
            elevation_m = float(tags['ele'])
            elevation_ft = int(elevation_m * 3.28084)
            base_desc += f", {elevation_ft:,}ft elevation"
        except (ValueError, TypeError):
            pass

    return base_desc
