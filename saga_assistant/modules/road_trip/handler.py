"""
Main handler for Road Trip Planning Module

Processes user queries and generates responses.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .config import (
    get_unit_preference,
    VERY_CLOSE_THRESHOLD_MILES,
    VERY_FAR_THRESHOLD_MILES,
    MULTIDAY_TRIP_THRESHOLD_HOURS,
)
from .routing import geocode, calculate_route, estimate_route_fallback, Location, GeocodingError, RoutingError
from .traffic import get_traffic_conditions, adjust_route_for_traffic
from .timing import find_best_departure_time, estimate_arrival_time
from .poi import find_pois_along_route

logger = logging.getLogger(__name__)


class RoadTripHandler:
    """Handles road trip planning queries."""

    def __init__(self, home_location: Location, unit_system: str = 'imperial'):
        """
        Initialize handler.

        Args:
            home_location: User's home location
            unit_system: 'imperial' or 'metric'
        """
        self.home_location = home_location
        self.unit_system = unit_system

    @classmethod
    def from_ha_config(cls, ha_config: Dict[str, Any]) -> 'RoadTripHandler':
        """
        Create handler from Home Assistant configuration.

        Args:
            ha_config: Home Assistant config dict

        Returns:
            RoadTripHandler instance
        """
        # Extract home location from HA config
        latitude = ha_config.get('latitude')
        longitude = ha_config.get('longitude')

        if not latitude or not longitude:
            raise ValueError("Home location not found in Home Assistant config")

        home_location = Location(
            latitude=float(latitude),
            longitude=float(longitude),
            address="home"
        )

        unit_system = get_unit_preference(ha_config)

        return cls(home_location, unit_system)

    def handle_query(self, query: str, quick_mode: bool = False) -> str:
        """
        Process a road trip query and generate response.

        Args:
            query: User's query text
            quick_mode: If True, return brief response

        Returns:
            Response string
        """
        try:
            # Parse query to determine intent and extract parameters
            intent = self._parse_intent(query)

            # Route to appropriate handler
            if intent['type'] == 'distance':
                return self._handle_distance_query(intent, quick_mode)
            elif intent['type'] == 'travel_time':
                return self._handle_travel_time_query(intent, quick_mode)
            elif intent['type'] == 'best_departure':
                return self._handle_best_departure_query(intent, quick_mode)
            elif intent['type'] == 'arrival_time':
                return self._handle_arrival_time_query(intent, quick_mode)
            elif intent['type'] == 'poi':
                return self._handle_poi_query(intent, quick_mode)
            else:
                return "I'm not sure what you're asking about. Try asking 'how far is the drive to [destination]' or 'when should I leave for [destination]'."

        except GeocodingError as e:
            return f"I couldn't find that location. Could you be more specific? Try including the city or state."
        except RoutingError as e:
            return f"I couldn't calculate a route to that location. It might be unreachable by car or too far away."
        except Exception as e:
            logger.error(f"Error handling road trip query: {e}", exc_info=True)
            return "Sorry, I encountered an error processing that request."

    def _parse_intent(self, query: str) -> Dict[str, Any]:
        """
        Parse user query to determine intent and extract parameters.

        Args:
            query: User query text

        Returns:
            Dict with intent type and parameters
        """
        query_lower = query.lower()

        # Extract destination (common to all queries)
        destination = self._extract_destination(query_lower)

        # Determine intent type
        if any(phrase in query_lower for phrase in ['how far', 'distance to', 'how many miles']):
            return {'type': 'distance', 'destination': destination}

        elif any(phrase in query_lower for phrase in ['how long', 'travel time', 'drive time']):
            # Check for specific departure time
            departure_time = self._extract_departure_time(query_lower)
            return {'type': 'travel_time', 'destination': destination, 'departure_time': departure_time}

        elif any(phrase in query_lower for phrase in ['best time to leave', 'when should i leave', 'best departure']):
            constraint = self._extract_time_constraint(query_lower)
            num_options = self._extract_num_options(query_lower)
            return {
                'type': 'best_departure',
                'destination': destination,
                'constraint': constraint,
                'num_options': num_options
            }

        elif any(phrase in query_lower for phrase in ['when will i arrive', 'what time will i get there', 'arrival time']):
            departure_time = self._extract_departure_time(query_lower)
            return {'type': 'arrival_time', 'destination': destination, 'departure_time': departure_time}

        elif any(phrase in query_lower for phrase in ['landmarks', 'stops', 'points of interest', 'interesting', 'things to see']):
            return {'type': 'poi', 'destination': destination}

        else:
            # Default to distance query
            return {'type': 'distance', 'destination': destination}

    def _extract_destination(self, query: str) -> str:
        """Extract destination from query."""
        # Simple extraction - look for "to X" or last few words
        to_idx = query.rfind(' to ')
        if to_idx >= 0:
            return query[to_idx + 4:].strip('?. ')

        # Fallback: take last 2-3 words
        words = query.strip('?. ').split()
        return ' '.join(words[-3:])

    def _extract_departure_time(self, query: str) -> Optional[datetime]:
        """Extract departure time from query."""
        # Look for time indicators
        if 'if i leave now' in query or 'leaving now' in query:
            return datetime.now()

        # Look for specific times (simplified - could be enhanced)
        # For now, return None (will use current time as default)
        return None

    def _extract_time_constraint(self, query: str) -> Optional[str]:
        """Extract time constraint from query."""
        # Look for "after X", "before X"
        if 'after ' in query:
            idx = query.find('after ')
            return query[idx:].split('.')[0].split('?')[0].strip()
        elif 'before ' in query:
            idx = query.find('before ')
            return query[idx:].split('.')[0].split('?')[0].strip()
        return None

    def _extract_num_options(self, query: str) -> int:
        """Extract number of options requested (for best departure times)."""
        # Look for "3 best times", "top 5 times", etc.
        words = query.split()
        for i, word in enumerate(words):
            if word.isdigit() and i + 1 < len(words) and 'time' in words[i + 1]:
                return int(word)
        return 1  # Default to single best time

    def _handle_distance_query(self, intent: Dict, quick_mode: bool) -> str:
        """Handle 'how far is the drive to X' queries."""
        destination = intent['destination']

        # Geocode destination
        dest_location = geocode(destination)

        # Calculate route
        try:
            route = calculate_route(self.home_location, dest_location)
        except RoutingError:
            # Fall back to simple estimate
            route = estimate_route_fallback(self.home_location, dest_location)

        # Quick mode: just distance and time
        if quick_mode:
            return f"{route.format_distance(self.unit_system)}, {route.format_duration()}"

        # Detailed mode
        response_parts = []

        # Check for very close/very far edge cases
        if route.distance_miles < VERY_CLOSE_THRESHOLD_MILES:
            response_parts.append(f"That's just {route.format_distance(self.unit_system)} away - about {route.format_duration()}.")
        elif route.distance_miles > VERY_FAR_THRESHOLD_MILES:
            response_parts.append(f"That's a long drive - {route.format_distance(self.unit_system)} to {dest_location.address}.")
            if route.duration_hours > MULTIDAY_TRIP_THRESHOLD_HOURS:
                response_parts.append(f"About {route.format_duration()} of driving. Consider breaking it into multiple days.")
            else:
                response_parts.append(f"About {route.format_duration()} of driving.")
        else:
            response_parts.append(f"The drive to {dest_location.address} is {route.format_distance(self.unit_system)} {route.route_name}.")
            response_parts.append(f"Takes about {route.format_duration()}.")

        return " ".join(response_parts)

    def _handle_travel_time_query(self, intent: Dict, quick_mode: bool) -> str:
        """Handle 'how long will it take' queries."""
        destination = intent['destination']
        departure_time = intent.get('departure_time') or datetime.now()

        # Geocode
        dest_location = geocode(destination)

        # Calculate route
        try:
            route = calculate_route(self.home_location, dest_location, departure_time)
        except RoutingError:
            route = estimate_route_fallback(self.home_location, dest_location)

        # Get traffic conditions
        traffic = get_traffic_conditions(route, departure_time)

        # Adjust for traffic
        adjusted_route = adjust_route_for_traffic(route, traffic)

        # Quick mode
        if quick_mode:
            return f"{adjusted_route.format_duration()}"

        # Detailed mode
        response_parts = [
            f"The drive to {dest_location.address} takes about {adjusted_route.format_duration()} {route.route_name}."
        ]

        # Add traffic info if meaningful
        if traffic.severity in ('moderate', 'heavy', 'severe'):
            response_parts.append(traffic.description + ".")

        if traffic.incidents:
            major_incidents = [i for i in traffic.incidents if i.severity in ('major', 'severe')]
            if major_incidents:
                response_parts.append(f"Note: {len(major_incidents)} incident{'s' if len(major_incidents) > 1 else ''} reported along the route.")

        return " ".join(response_parts)

    def _handle_best_departure_query(self, intent: Dict, quick_mode: bool) -> str:
        """Handle 'when should I leave' queries."""
        destination = intent['destination']
        constraint = intent.get('constraint')
        num_options = intent.get('num_options', 1)

        # Geocode
        dest_location = geocode(destination)

        # Find best departure time(s)
        options = find_best_departure_time(
            self.home_location,
            dest_location,
            constraint=constraint,
            max_results=num_options
        )

        if not options:
            return "I couldn't find a good departure time. Traffic data might be unavailable."

        # Quick mode: just the best time
        if quick_mode:
            best = options[0]
            return best.format_departure()

        # Detailed mode
        if num_options == 1:
            best = options[0]
            response = f"The best time to leave for {dest_location.address} is {best.format_departure()}. "
            response += f"Travel time: {best.route.format_duration()} {best.route.route_name}. "

            if best.traffic_severity == 'light':
                response += "Light traffic expected. "
            elif best.traffic_severity in ('moderate', 'heavy'):
                response += f"{best.traffic_severity.capitalize()} traffic expected. "

            response += f"Arriving around {best.format_arrival()}."

            return response
        else:
            # Multiple options
            response = f"Here are the best times to leave for {dest_location.address}:\n\n"

            for i, option in enumerate(options, 1):
                response += f"{i}. {option.format_departure().capitalize()} - "
                response += f"{option.route.format_duration()} "
                response += f"({option.traffic_severity} traffic)\n"

            return response.strip()

    def _handle_arrival_time_query(self, intent: Dict, quick_mode: bool) -> str:
        """Handle 'when will I arrive' queries."""
        destination = intent['destination']
        departure_time = intent.get('departure_time') or datetime.now()

        # Geocode
        dest_location = geocode(destination)

        # Estimate arrival
        arrival_time, route = estimate_arrival_time(
            self.home_location,
            dest_location,
            departure_time
        )

        # Quick mode
        if quick_mode:
            return arrival_time.strftime('%-I:%M%p').lower()

        # Detailed mode
        response = f"If you leave {departure_time.strftime('%A at %-I:%M%p').lower()}, "
        response += f"you'll arrive around {arrival_time.strftime('%-I:%M%p').lower()}. "
        response += f"Travel time: {route.format_duration()} {route.route_name}."

        return response

    def _handle_poi_query(self, intent: Dict, quick_mode: bool) -> str:
        """Handle 'what landmarks are between here and X' queries."""
        destination = intent['destination']

        # Geocode
        dest_location = geocode(destination)

        # Calculate route
        try:
            route = calculate_route(self.home_location, dest_location)
        except RoutingError:
            route = estimate_route_fallback(self.home_location, dest_location)

        # Find POIs
        pois = find_pois_along_route(route, max_results=5)

        if not pois:
            return f"I couldn't find any natural landmarks along the route to {dest_location.address}."

        # Quick mode: just names
        if quick_mode:
            return ", ".join([poi.name for poi in pois])

        # Detailed mode
        response = f"Along the route to {dest_location.address}, you could stop at:\n\n"

        for i, poi in enumerate(pois, 1):
            response += f"{i}. {poi.format_description()}\n"

        return response.strip()
