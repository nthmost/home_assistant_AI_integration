"""
Departure time optimization for Road Trip Planning Module

Analyzes traffic patterns to suggest optimal departure times.
"""

import logging
from typing import List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from .config import (
    DEPARTURE_TIME_WINDOW_HOURS,
    DEPARTURE_TIME_INTERVAL_MINUTES,
    MAX_ALTERNATIVE_TIMES,
)
from .routing import Route, Location, calculate_route
from .traffic import get_traffic_conditions, adjust_route_for_traffic

logger = logging.getLogger(__name__)


@dataclass
class DepartureOption:
    """Represents a possible departure time with estimated arrival."""
    departure_time: datetime
    route: Route  # Route with traffic-adjusted duration
    arrival_time: datetime
    traffic_severity: str

    def format_departure(self) -> str:
        """Format departure time as human-readable string."""
        now = datetime.now()

        # Today
        if self.departure_time.date() == now.date():
            if (self.departure_time - now).total_seconds() < 3600:  # Within 1 hour
                return "now" if (self.departure_time - now).total_seconds() < 300 else f"{self.departure_time.strftime('%-I:%M%p').lower()} today"
            return f"{self.departure_time.strftime('%-I:%M%p').lower()} today"

        # Tomorrow
        elif self.departure_time.date() == (now + timedelta(days=1)).date():
            return f"{self.departure_time.strftime('%-I:%M%p').lower()} tomorrow"

        # Other day
        else:
            return self.departure_time.strftime('%A at %-I:%M%p').lower()

    def format_arrival(self) -> str:
        """Format arrival time as human-readable string."""
        return self.arrival_time.strftime('%-I:%M%p').lower()


def find_best_departure_time(
    start: Location,
    end: Location,
    constraint: Optional[str] = None,
    max_results: int = 1,
) -> List[DepartureOption]:
    """
    Find optimal departure time(s) for a trip.

    Args:
        start: Starting location
        end: Destination location
        constraint: Optional time constraint (e.g., "after 5pm", "before noon")
        max_results: Number of best options to return (default 1)

    Returns:
        List of DepartureOption objects sorted by total travel time
    """
    now = datetime.now()

    # Parse constraint if provided
    constraint_start, constraint_end = _parse_time_constraint(constraint, now)

    # Generate candidate departure times
    candidates = _generate_candidate_times(
        start_time=constraint_start or now,
        end_time=constraint_end or (now + timedelta(hours=DEPARTURE_TIME_WINDOW_HOURS)),
        interval_minutes=DEPARTURE_TIME_INTERVAL_MINUTES
    )

    # Evaluate each candidate
    options = []
    for departure_time in candidates:
        try:
            # Calculate route
            route = calculate_route(start, end, departure_time=departure_time)

            # Get traffic conditions for this departure time
            traffic = get_traffic_conditions(route, departure_time=departure_time)

            # Adjust route for traffic
            adjusted_route = adjust_route_for_traffic(route, traffic)

            # Calculate arrival time
            arrival_time = departure_time + timedelta(seconds=adjusted_route.duration_seconds)

            option = DepartureOption(
                departure_time=departure_time,
                route=adjusted_route,
                arrival_time=arrival_time,
                traffic_severity=traffic.severity
            )

            options.append(option)

        except Exception as e:
            logger.warning(f"Failed to evaluate departure time {departure_time}: {e}")
            continue

    if not options:
        logger.error("No valid departure options found")
        return []

    # Sort by total travel time (shortest first)
    options.sort(key=lambda x: x.route.duration_seconds)

    # Return top N options
    return options[:max_results]


def _parse_time_constraint(constraint: Optional[str], reference_time: datetime) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Parse time constraint string into start/end datetime boundaries.

    Args:
        constraint: Constraint string (e.g., "after 5pm", "before noon", "between 8am and 10am")
        reference_time: Reference time (usually now)

    Returns:
        Tuple of (constraint_start, constraint_end) - both can be None
    """
    if not constraint:
        return None, None

    constraint = constraint.lower().strip()

    # "after X" or "after X pm/am"
    if constraint.startswith('after '):
        time_str = constraint.replace('after ', '').strip()
        constraint_time = _parse_time_of_day(time_str, reference_time)
        return constraint_time, None

    # "before X" or "before X pm/am"
    elif constraint.startswith('before '):
        time_str = constraint.replace('before ', '').strip()
        constraint_time = _parse_time_of_day(time_str, reference_time)
        return None, constraint_time

    # "between X and Y"
    elif 'between' in constraint and 'and' in constraint:
        parts = constraint.replace('between ', '').split(' and ')
        if len(parts) == 2:
            start_time = _parse_time_of_day(parts[0].strip(), reference_time)
            end_time = _parse_time_of_day(parts[1].strip(), reference_time)
            return start_time, end_time

    # Couldn't parse
    logger.warning(f"Could not parse time constraint: {constraint}")
    return None, None


def _parse_time_of_day(time_str: str, reference_time: datetime) -> datetime:
    """
    Parse time string like "5pm", "noon", "8:30am" into datetime.

    Args:
        time_str: Time string to parse
        reference_time: Reference date to use

    Returns:
        datetime object on the reference date
    """
    time_str = time_str.lower().strip()

    # Special cases
    if time_str in ('noon', '12pm'):
        return reference_time.replace(hour=12, minute=0, second=0, microsecond=0)
    elif time_str in ('midnight', '12am'):
        return reference_time.replace(hour=0, minute=0, second=0, microsecond=0)

    # Try to parse with various formats
    formats = [
        '%I%p',      # 5pm
        '%I:%M%p',   # 5:30pm
        '%H:%M',     # 17:30 (24-hour)
        '%H',        # 17 (24-hour)
    ]

    for fmt in formats:
        try:
            # Parse time component
            time_obj = datetime.strptime(time_str, fmt).time()

            # Combine with reference date
            result = reference_time.replace(
                hour=time_obj.hour,
                minute=time_obj.minute,
                second=0,
                microsecond=0
            )

            # If the time has already passed today, use tomorrow
            if result < reference_time:
                result += timedelta(days=1)

            return result

        except ValueError:
            continue

    # Fallback: return reference time
    logger.warning(f"Could not parse time string: {time_str}, using reference time")
    return reference_time


def _generate_candidate_times(
    start_time: datetime,
    end_time: datetime,
    interval_minutes: int
) -> List[datetime]:
    """
    Generate list of candidate departure times.

    Args:
        start_time: Earliest departure time to consider
        end_time: Latest departure time to consider
        interval_minutes: Interval between candidates

    Returns:
        List of datetime objects
    """
    candidates = []
    current = start_time

    while current <= end_time:
        candidates.append(current)
        current += timedelta(minutes=interval_minutes)

    return candidates


def estimate_arrival_time(
    start: Location,
    end: Location,
    departure_time: datetime
) -> Tuple[datetime, Route]:
    """
    Estimate arrival time for a specific departure time.

    Args:
        start: Starting location
        end: Destination location
        departure_time: When to depart

    Returns:
        Tuple of (arrival_time, route_with_traffic)
    """
    # Calculate base route
    route = calculate_route(start, end, departure_time=departure_time)

    # Get traffic for this departure time
    traffic = get_traffic_conditions(route, departure_time=departure_time)

    # Adjust for traffic
    adjusted_route = adjust_route_for_traffic(route, traffic)

    # Calculate arrival
    arrival_time = departure_time + timedelta(seconds=adjusted_route.duration_seconds)

    return arrival_time, adjusted_route
