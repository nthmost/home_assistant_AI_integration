"""
Traffic data integration for Road Trip Planning Module

Handles real-time traffic data, incidents, and travel time adjustments
using multiple APIs with fallback support.
"""

import logging
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from .config import get_enabled_apis
from .routing import Route, Location

logger = logging.getLogger(__name__)


@dataclass
class TrafficCondition:
    """Represents traffic conditions along a route."""
    severity: str  # 'light', 'moderate', 'heavy', 'severe'
    delay_seconds: int  # Additional time due to traffic
    description: str  # Human-readable description
    incidents: List['TrafficIncident'] = None

    def __post_init__(self):
        if self.incidents is None:
            self.incidents = []


@dataclass
class TrafficIncident:
    """Represents a traffic incident (accident, construction, etc.)."""
    type: str  # 'accident', 'construction', 'road_closure', etc.
    description: str
    location: Optional[Location] = None
    severity: str = 'moderate'  # 'minor', 'moderate', 'major'


class TrafficError(Exception):
    """Raised when traffic data fetching fails."""
    pass


def get_traffic_conditions(route: Route, departure_time: Optional[datetime] = None) -> TrafficCondition:
    """
    Get traffic conditions for a route.

    Args:
        route: Route to check traffic for
        departure_time: When the trip will start (None = now)

    Returns:
        TrafficCondition with delay and incident info

    Raises:
        TrafficError: If all traffic APIs fail
    """
    enabled_apis = get_enabled_apis('traffic')

    # If no traffic APIs enabled/configured, return estimate
    if not enabled_apis:
        logger.warning("No traffic APIs configured, returning 'unknown' condition")
        return TrafficCondition(
            severity='unknown',
            delay_seconds=0,
            description="Traffic data unavailable"
        )

    # Try each API in priority order
    for api_name, api_config in enabled_apis:
        try:
            if api_name == 'tomtom':
                return _get_traffic_tomtom(route, departure_time, api_config)
            elif api_name == 'here':
                return _get_traffic_here(route, departure_time, api_config)
        except Exception as e:
            logger.warning(f"Traffic check failed with {api_name}: {e}")
            continue

    # All APIs failed - return unknown condition
    logger.warning("All traffic APIs failed, returning 'unknown' condition")
    return TrafficCondition(
        severity='unknown',
        delay_seconds=0,
        description="Traffic data currently unavailable"
    )


def _get_traffic_tomtom(
    route: Route,
    departure_time: Optional[datetime],
    config: Dict
) -> TrafficCondition:
    """Get traffic conditions using TomTom Traffic API."""
    if not route.geometry or len(route.geometry) < 2:
        raise TrafficError("Route geometry required for TomTom traffic check")

    # Use first and last points for traffic flow check
    start = route.geometry[0]
    end = route.geometry[-1]

    # TomTom Traffic Flow API
    url = f"{config['base_url']}/traffic/services/4/flowSegmentData/absolute/10/json"

    params = {
        'key': config['api_key'],
        'point': f"{start[0]},{start[1]}",  # lat,lon
    }

    response = requests.get(url, params=params, timeout=config.get('timeout', 10))
    response.raise_for_status()

    data = response.json()

    # Extract traffic flow data
    flow_data = data.get('flowSegmentData', {})

    current_speed = flow_data.get('currentSpeed', 0)
    free_flow_speed = flow_data.get('freeFlowSpeed', 0)
    current_travel_time = flow_data.get('currentTravelTime', 0)
    free_flow_travel_time = flow_data.get('freeFlowTravelTime', 0)

    # Calculate delay
    delay_seconds = max(0, current_travel_time - free_flow_travel_time)

    # Determine severity based on speed ratio
    severity = _calculate_severity(current_speed, free_flow_speed)

    # Get incidents along route
    incidents = _get_incidents_tomtom(route, config)

    description = _format_traffic_description(severity, incidents)

    return TrafficCondition(
        severity=severity,
        delay_seconds=delay_seconds,
        description=description,
        incidents=incidents
    )


def _get_incidents_tomtom(route: Route, config: Dict) -> List[TrafficIncident]:
    """Get traffic incidents along route using TomTom Incidents API."""
    if not route.start or not route.end:
        return []

    try:
        # Create bounding box around route
        bbox = _create_bbox(route)

        url = f"{config['base_url']}/traffic/services/5/incidentDetails"

        params = {
            'key': config['api_key'],
            'bbox': f"{bbox['min_lon']},{bbox['min_lat']},{bbox['max_lon']},{bbox['max_lat']}",
            'fields': '{incidents{type,geometry{type,coordinates},properties{iconCategory,magnitudeOfDelay,events{description,code,iconCategory}}}}',
        }

        response = requests.get(url, params=params, timeout=config.get('timeout', 10))
        response.raise_for_status()

        data = response.json()

        incidents = []
        for incident_data in data.get('incidents', []):
            incident = _parse_tomtom_incident(incident_data)
            if incident:
                incidents.append(incident)

        return incidents

    except Exception as e:
        logger.warning(f"Failed to fetch incidents from TomTom: {e}")
        return []


def _parse_tomtom_incident(data: Dict) -> Optional[TrafficIncident]:
    """Parse TomTom incident data into TrafficIncident."""
    try:
        props = data.get('properties', {})
        events = props.get('events', [{}])
        event = events[0] if events else {}

        incident_type = event.get('code', 'unknown')
        description = event.get('description', 'Traffic incident')

        # Map iconCategory to severity
        icon_category = props.get('iconCategory', 0)
        severity = _map_icon_to_severity(icon_category)

        return TrafficIncident(
            type=incident_type,
            description=description,
            severity=severity
        )
    except Exception as e:
        logger.warning(f"Failed to parse TomTom incident: {e}")
        return None


def _get_traffic_here(
    route: Route,
    departure_time: Optional[datetime],
    config: Dict
) -> TrafficCondition:
    """Get traffic conditions using HERE Traffic API."""
    # HERE Traffic API implementation
    # For now, return a placeholder - can be implemented similarly to TomTom
    raise TrafficError("HERE traffic API not yet implemented")


def _calculate_severity(current_speed: float, free_flow_speed: float) -> str:
    """
    Calculate traffic severity based on speed ratio.

    Args:
        current_speed: Current average speed (mph or kph)
        free_flow_speed: Free flow speed (mph or kph)

    Returns:
        Severity string: 'light', 'moderate', 'heavy', or 'severe'
    """
    if free_flow_speed == 0:
        return 'unknown'

    ratio = current_speed / free_flow_speed

    if ratio >= 0.85:
        return 'light'
    elif ratio >= 0.65:
        return 'moderate'
    elif ratio >= 0.40:
        return 'heavy'
    else:
        return 'severe'


def _format_traffic_description(severity: str, incidents: List[TrafficIncident]) -> str:
    """Format human-readable traffic description."""
    severity_desc = {
        'light': 'Light traffic',
        'moderate': 'Moderate traffic',
        'heavy': 'Heavy traffic',
        'severe': 'Severe traffic delays',
        'unknown': 'Traffic conditions unknown',
    }

    description = severity_desc.get(severity, 'Traffic conditions unknown')

    # Add incident info if present
    if incidents:
        major_incidents = [i for i in incidents if i.severity in ('major', 'severe')]
        if major_incidents:
            description += f". {len(major_incidents)} incident{'s' if len(major_incidents) > 1 else ''} reported"

    return description


def _create_bbox(route: Route) -> Dict[str, float]:
    """Create bounding box around route."""
    if route.geometry:
        lats = [coord[0] for coord in route.geometry]
        lons = [coord[1] for coord in route.geometry]
    elif route.start and route.end:
        lats = [route.start.latitude, route.end.latitude]
        lons = [route.start.longitude, route.end.longitude]
    else:
        raise ValueError("Cannot create bbox: no geometry or start/end points")

    # Add small buffer (approximately 0.1 degrees ~ 7 miles)
    buffer = 0.1

    return {
        'min_lat': min(lats) - buffer,
        'max_lat': max(lats) + buffer,
        'min_lon': min(lons) - buffer,
        'max_lon': max(lons) + buffer,
    }


def _map_icon_to_severity(icon_category: int) -> str:
    """Map TomTom icon category to severity."""
    # TomTom icon categories (0-14)
    # Lower numbers are typically more severe
    if icon_category <= 3:
        return 'major'
    elif icon_category <= 7:
        return 'moderate'
    else:
        return 'minor'


def adjust_route_for_traffic(route: Route, traffic: TrafficCondition) -> Route:
    """
    Create new route with traffic-adjusted duration.

    Args:
        route: Original route
        traffic: Traffic conditions

    Returns:
        New Route object with adjusted duration
    """
    adjusted_duration = route.duration_seconds + traffic.delay_seconds

    return Route(
        distance_miles=route.distance_miles,
        duration_seconds=adjusted_duration,
        route_name=route.route_name,
        geometry=route.geometry,
        start=route.start,
        end=route.end,
    )
