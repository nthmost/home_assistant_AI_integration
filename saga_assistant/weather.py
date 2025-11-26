"""Weather information retrieval with caching and fallback."""

import logging
from typing import Optional

from saga_assistant.services.weather_cache import WeatherCache, WeatherData
from saga_assistant.services.weather_apis import WeatherFetcher

logger = logging.getLogger(__name__)

DEFAULT_ZIP = "94118"

# Direction map for wind (abbreviations to full names for speech)
DIRECTION_MAP = {
    "N": "north", "NNE": "north northeast", "NE": "northeast",
    "ENE": "east northeast", "E": "east", "ESE": "east southeast",
    "SE": "southeast", "SSE": "south southeast", "S": "south",
    "SSW": "south southwest", "SW": "southwest", "WSW": "west southwest",
    "W": "west", "WNW": "west northwest", "NW": "northwest",
    "NNW": "north northwest",
}


def _get_weather_data(location: str = None) -> Optional[WeatherData]:
    """
    Get weather data from cache or API.

    Fast path: Returns cached data if fresh (<30 minutes old).
    Slow path: Fetches from API if cache is stale or missing.

    Args:
        location: ZIP code (defaults to DEFAULT_ZIP)

    Returns:
        WeatherData or None if all sources fail
    """
    if not location:
        location = DEFAULT_ZIP

    # Try cache first (fast!)
    cache = WeatherCache()
    data = cache.get(location)

    if data and not data.is_stale():
        logger.debug(f"✅ Using cached weather ({data.age_minutes()}m old)")
        return data

    # Cache miss or stale - fetch from API
    if data:
        logger.info(f"⚠️  Cache stale ({data.age_minutes()}m old), fetching fresh data...")
    else:
        logger.info("⚠️  Cache miss, fetching from API...")

    fetcher = WeatherFetcher()
    fresh_data = fetcher.fetch(location)

    if fresh_data:
        # Update cache
        cache.set(location, fresh_data)
        # Return fresh data wrapped in WeatherData
        return cache.get(location)

    # API failed - use stale cache if available
    if data:
        logger.warning(f"⚠️  API failed, using stale cache ({data.age_minutes()}m old)")
        return data

    logger.error("❌ No weather data available (cache empty, API failed)")
    return None


def get_weather(location: str = None, when: str = "now") -> str:
    """Get weather information.

    Args:
        location: Location (zip code, city name, etc.). Defaults to 94118.
        when: "now", "today", "tomorrow", "this morning", "this afternoon", "tonight"

    Returns:
        Natural language weather description
    """
    data = _get_weather_data(location)

    if not data:
        return "Sorry, I couldn't fetch the weather right now"

    try:
        # Time-specific responses
        if when == "now" or when == "today":
            response = f"It's {data.current_temp_f} degrees and {data.current_condition.lower()}"
            if data.current_feels_like_f != data.current_temp_f:
                response += f", feels like {data.current_feels_like_f}"
            return response

        elif when == "this morning":
            # Use today's forecast
            return f"This morning: High of {data.today_high_f}, {data.today_condition.lower()}"

        elif when == "this afternoon":
            # Use today's forecast
            return f"This afternoon: High of {data.today_high_f}, {data.today_condition.lower()}"

        elif when == "tonight":
            # Use today's forecast
            return f"Tonight: Low of {data.today_low_f}, {data.today_condition.lower()}"

        elif when == "tomorrow":
            if data.tomorrow_high_f:
                return f"Tomorrow: {data.tomorrow_condition.lower()}, high of {data.tomorrow_high_f}, low of {data.tomorrow_low_f}"
            else:
                return "Sorry, I don't have tomorrow's forecast yet"

        else:
            # Default to current
            return f"It's {data.current_temp_f} degrees and {data.current_condition.lower()}"

    except Exception as e:
        logger.error(f"Weather formatting error: {e}")
        return "Sorry, I had trouble formatting the weather data"


def will_it_rain(location: str = None, when: str = "today") -> str:
    """Check if it will rain.

    Args:
        location: Location (zip code, city name, etc.). Defaults to 94118.
        when: "today" or "tomorrow"

    Returns:
        Natural language rain forecast
    """
    data = _get_weather_data(location)

    if not data:
        return "Sorry, I couldn't check the rain forecast"

    try:
        if when == "today":
            chance = data.today_rain_chance
        elif when == "tomorrow":
            if data.tomorrow_rain_chance is not None:
                chance = data.tomorrow_rain_chance
            else:
                return "Sorry, I don't have tomorrow's forecast yet"
        else:
            chance = data.today_rain_chance

        if chance > 60:
            return f"Yes, {chance} percent chance of rain"
        elif chance > 30:
            return f"{chance} percent chance of rain"
        else:
            return "No rain expected"

    except Exception as e:
        logger.error(f"Rain forecast error: {e}")
        return "Sorry, I couldn't check the rain forecast"


def get_wind_info(location: str = None) -> str:
    """Get current wind information.

    Args:
        location: Location (zip code, city name, etc.). Defaults to 94118.

    Returns:
        Natural language wind description
    """
    data = _get_weather_data(location)

    if not data:
        return "Sorry, I couldn't get wind information"

    try:
        speed = data.wind_speed_mph
        direction_abbr = data.wind_direction

        # Convert abbreviation to full name for speech
        direction = DIRECTION_MAP.get(direction_abbr, direction_abbr.lower())

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
