"""
Weather V2 - Multi-Location, 5-Day Forecasts

Query weather across multiple locations with 5-day forecasts.
Perfect for bike ride planning!
"""

import logging
import re
from typing import Optional, List
from datetime import datetime, timedelta

from saga_assistant.services.weather_cache_v2 import WeatherCacheV2, LocationWeather
from saga_assistant.services.weather_apis_v2 import WeatherFetcherV2

logger = logging.getLogger(__name__)

DEFAULT_LOCATION = "San Francisco"
DEFAULT_ZIP = "94118"  # San Francisco default


def _fetch_and_cache(location: str, zip_code: str = None) -> Optional[LocationWeather]:
    """
    Fetch weather data on-demand and cache it.

    Args:
        location: Location name
        zip_code: ZIP code (if None, tries to guess from location)

    Returns:
        LocationWeather or None if fetch failed
    """
    # Try to guess ZIP from common locations
    if not zip_code:
        zip_map = {
            'san francisco': '94118',
            'sf': '94118',
            'marin city': '94965',
            'marin': '94965',
            'sausalito': '94965',
            'daly city': '94014',
            'daly': '94014',
            'oakland': '94612',
            'berkeley': '94704',
            'palo alto': '94301',
            'san jose': '95113',
        }
        zip_code = zip_map.get(location.lower().strip())

    if not zip_code:
        logger.warning(f"Cannot fetch weather for '{location}' - no ZIP code available")
        return None

    try:
        logger.info(f"⚡ Fetching weather on-demand for {location} ({zip_code})...")
        fetcher = WeatherFetcherV2()
        data = fetcher.fetch(zip_code)

        if not data:
            logger.warning(f"Failed to fetch weather for {location}")
            return None

        # Cache it
        cache = WeatherCacheV2()
        success = cache.set(location, data['current'], data['forecasts'])

        if success:
            logger.info(f"✅ Cached weather for {location}")
            return cache.get(location)
        else:
            logger.warning(f"Failed to cache weather for {location}")
            return None

    except Exception as e:
        logger.error(f"Error fetching weather for {location}: {e}")
        return None


def get_weather(location: str = None, when: str = "now") -> str:
    """
    Get weather for a location.

    Args:
        location: Location name (e.g., "San Francisco", "Marin City")
        when: "now", "today", "tomorrow", "monday", "tuesday", etc., or day offset like "day 3"

    Returns:
        Natural language weather description
    """
    if not location:
        location = DEFAULT_LOCATION

    cache = WeatherCacheV2()
    data = cache.get(location)

    # If not in cache, try to fetch on-demand
    if not data:
        logger.info(f"Cache miss for '{location}', attempting on-demand fetch...")
        data = _fetch_and_cache(location)
        if not data:
            return f"Sorry, I couldn't get weather data for {location}"

    if data.is_stale():
        logger.warning(f"Weather data for {location} is stale")

    try:
        # Current weather
        if when in ["now", "currently", "right now"]:
            response = f"In {location}, it's {data.current_temp_f} degrees and {data.current_condition.lower()}"
            if data.current_feels_like_f != data.current_temp_f:
                response += f", feels like {data.current_feels_like_f}"
            return response

        # Parse day offset
        day_offset = _parse_when(when)

        if day_offset is None:
            return f"Sorry, I don't understand '{when}'"

        forecast = data.get_forecast_for_day(day_offset)

        if not forecast:
            return f"Sorry, I only have forecasts for the next 5 days"

        # Format response
        day_name = _get_day_name(day_offset)
        return f"{day_name} in {location}: {forecast.condition.lower()}, high of {forecast.high_f}, low of {forecast.low_f}"

    except Exception as e:
        logger.error(f"Weather formatting error: {e}")
        return "Sorry, I had trouble formatting the weather data"


def get_week_summary(location: str = None) -> str:
    """
    Get weekly weather summary for a location.

    Args:
        location: Location name

    Returns:
        Week summary string
    """
    if not location:
        location = DEFAULT_LOCATION

    cache = WeatherCacheV2()
    data = cache.get(location)

    # If not in cache, try to fetch on-demand
    if not data:
        logger.info(f"Cache miss for '{location}', attempting on-demand fetch...")
        data = _fetch_and_cache(location)
        if not data:
            return f"Sorry, I couldn't get forecast data for {location}"

    if not data.forecasts:
        return f"Sorry, I don't have forecast data for {location}"

    try:
        # Calculate averages
        highs = [f.high_f for f in data.forecasts]
        lows = [f.low_f for f in data.forecasts]
        avg_high = sum(highs) / len(highs)
        avg_low = sum(lows) / len(lows)

        # Find most common condition
        conditions = [f.condition for f in data.forecasts]
        common_condition = max(set(conditions), key=conditions.count).lower()

        # Check for rain
        max_rain = max(f.rain_chance for f in data.forecasts)

        response = f"This week in {location}: mostly {common_condition}, "
        response += f"highs around {int(avg_high)}, lows around {int(avg_low)}"

        if max_rain > 30:
            response += f", {max_rain}% chance of rain"

        return response

    except Exception as e:
        logger.error(f"Week summary error: {e}")
        return "Sorry, I had trouble summarizing the week"


def compare_locations(locations: List[str], when: str = "tomorrow") -> str:
    """
    Compare weather across multiple locations.

    Perfect for deciding where to bike!

    Args:
        locations: List of location names
        when: Day to compare (default: tomorrow)

    Returns:
        Comparison summary
    """
    cache = WeatherCacheV2()
    day_offset = _parse_when(when)

    if day_offset is None:
        return "Sorry, I can only compare specific days"

    comparisons = []

    for location in locations:
        data = cache.get(location)
        if data:
            forecast = data.get_forecast_for_day(day_offset)
            if forecast:
                comparisons.append({
                    'location': location,
                    'high': forecast.high_f,
                    'low': forecast.low_f,
                    'condition': forecast.condition,
                    'rain': forecast.rain_chance,
                    'wind': forecast.wind_speed_mph
                })

    if not comparisons:
        return "Sorry, I don't have forecast data for those locations"

    # Find best for biking (warmest, least rain, least wind)
    best = max(comparisons, key=lambda x: x['high'] - x['rain']/10 - x['wind']/5)

    day_name = _get_day_name(day_offset)
    response = f"{day_name} bike ride comparison:\n"

    for c in comparisons:
        response += f"  • {c['location']}: {c['high']}°F, {c['condition'].lower()}"
        if c['rain'] > 20:
            response += f", {c['rain']}% rain"
        if c['wind'] > 15:
            response += f", windy ({c['wind']} mph)"
        response += "\n"

    response += f"\nBest for biking: {best['location']}"

    return response


def _parse_when(when: str) -> Optional[int]:
    """
    Parse 'when' string to day offset.

    Args:
        when: "today", "tomorrow", "monday", "day 3", etc.

    Returns:
        Day offset (0=today, 1=tomorrow, etc.) or None if invalid
    """
    when_lower = when.lower()

    # Direct offsets
    if when_lower in ["today", "tonight"]:
        return 0
    elif when_lower == "tomorrow":
        return 1
    elif when_lower == "day after tomorrow":
        return 2

    # Day of week
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if when_lower in weekdays:
        target_day = weekdays.index(when_lower)
        today_day = datetime.now().weekday()
        offset = (target_day - today_day) % 7
        if offset == 0:
            offset = 7  # Next week if same day
        return offset if offset < 5 else None  # Only have 5 days

    # "day N" format
    if when_lower.startswith("day "):
        try:
            offset = int(when_lower.split()[1])
            return offset if 0 <= offset < 5 else None
        except:
            pass

    return None


def _get_day_name(day_offset: int) -> str:
    """Get day name for offset (0=Today, 1=Tomorrow, etc.)."""
    if day_offset == 0:
        return "Today"
    elif day_offset == 1:
        return "Tomorrow"
    else:
        target_date = datetime.now() + timedelta(days=day_offset)
        return target_date.strftime("%A")  # Monday, Tuesday, etc.


def will_it_rain(location: str = None, when: str = "today") -> str:
    """
    Check if it will rain.

    Args:
        location: Location name (defaults to San Francisco)
        when: "today" or "tomorrow"

    Returns:
        Natural language rain forecast
    """
    if not location:
        location = DEFAULT_LOCATION

    cache = WeatherCacheV2()
    data = cache.get(location)

    # If not in cache, try to fetch on-demand
    if not data:
        logger.info(f"Cache miss for '{location}', attempting on-demand fetch...")
        data = _fetch_and_cache(location)
        if not data:
            return f"Sorry, I couldn't get weather data for {location}"

    try:
        day_offset = 0 if when == "today" else 1
        forecast = data.get_forecast_for_day(day_offset)

        if not forecast:
            return "Sorry, I don't have that forecast"

        chance = forecast.rain_chance

        if chance > 60:
            return f"Yes, {chance}% chance of rain"
        elif chance > 30:
            return f"{chance}% chance of rain"
        else:
            return "No rain expected"

    except Exception as e:
        logger.error(f"Rain forecast error: {e}")
        return "Sorry, I couldn't check the rain forecast"


def get_wind_info(location: str = None) -> str:
    """
    Get current wind information.

    Args:
        location: Location name (defaults to San Francisco)

    Returns:
        Natural language wind description
    """
    if not location:
        location = DEFAULT_LOCATION

    cache = WeatherCacheV2()
    data = cache.get(location)

    # If not in cache, try to fetch on-demand
    if not data:
        logger.info(f"Cache miss for '{location}', attempting on-demand fetch...")
        data = _fetch_and_cache(location)
        if not data:
            return f"Sorry, I couldn't get weather data for {location}"

    if not data.forecasts:
        return f"Sorry, I don't have weather data for {location}"

    try:
        # Use today's forecast for wind
        today = data.forecasts[0]
        speed = today.wind_speed_mph
        direction = today.wind_direction.lower()

        # Classify wind
        if speed < 5:
            desc = "calm"
        elif speed < 15:
            desc = "light"
        elif speed < 25:
            desc = "moderate"
        else:
            desc = "strong"

        return f"Wind is {desc} at {speed} miles per hour from the {direction}"

    except Exception as e:
        logger.error(f"Wind info error: {e}")
        return "Sorry, I couldn't get wind information"
