"""Weather information retrieval using wttr.in API."""

import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_ZIP = "94118"
WTTR_BASE_URL = "https://wttr.in"


def get_weather(location: str = None, when: str = "now") -> str:
    """Get weather information.

    Args:
        location: Location (zip code, city name, etc.). Defaults to 94118.
        when: "now", "today", "tomorrow", "this morning", "this afternoon", "tonight"

    Returns:
        Natural language weather description
    """
    if not location:
        location = DEFAULT_ZIP

    try:
        # Fetch weather data
        url = f"{WTTR_BASE_URL}/{location}?format=j1"
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()

        # Extract relevant data
        current = data["current_condition"][0]
        today_forecast = data["weather"][0]
        tomorrow_forecast = data["weather"][1] if len(data["weather"]) > 1 else None

        # Time-specific responses
        if when == "now" or when == "today":
            temp = current["temp_F"]
            desc = current["weatherDesc"][0]["value"]
            feels_like = current["FeelsLikeF"]
            humidity = current["humidity"]

            response = f"It's {temp} degrees and {desc.lower()}"
            if int(feels_like) != int(temp):
                response += f", feels like {feels_like}"

            return response

        elif when == "this morning":
            # Use today's forecast
            desc = today_forecast["hourly"][2]["weatherDesc"][0]["value"]  # ~8am
            temp = today_forecast["hourly"][2]["tempF"]
            return f"This morning: {temp} degrees and {desc.lower()}"

        elif when == "this afternoon":
            # Use today's forecast
            desc = today_forecast["hourly"][4]["weatherDesc"][0]["value"]  # ~2pm
            temp = today_forecast["hourly"][4]["tempF"]
            return f"This afternoon: {temp} degrees and {desc.lower()}"

        elif when == "tonight":
            # Use today's forecast
            desc = today_forecast["hourly"][6]["weatherDesc"][0]["value"]  # ~8pm
            temp = today_forecast["hourly"][6]["tempF"]
            return f"Tonight: {temp} degrees and {desc.lower()}"

        elif when == "tomorrow":
            if tomorrow_forecast:
                max_temp = tomorrow_forecast["maxtempF"]
                min_temp = tomorrow_forecast["mintempF"]
                desc = tomorrow_forecast["hourly"][4]["weatherDesc"][0]["value"]  # afternoon
                return f"Tomorrow: {desc.lower()}, high of {max_temp}, low of {min_temp}"
            else:
                return "Sorry, I don't have tomorrow's forecast yet"

        else:
            # Default to current
            temp = current["temp_F"]
            desc = current["weatherDesc"][0]["value"]
            return f"It's {temp} degrees and {desc.lower()}"

    except requests.RequestException as e:
        logger.error(f"Weather API error: {e}")
        return "Sorry, I couldn't fetch the weather right now"
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Weather data parsing error: {e}")
        return "Sorry, I had trouble understanding the weather data"


def will_it_rain(location: str = None, when: str = "today") -> str:
    """Check if it will rain.

    Args:
        location: Location (zip code, city name, etc.). Defaults to 94118.
        when: "today" or "tomorrow"

    Returns:
        Natural language rain forecast
    """
    if not location:
        location = DEFAULT_ZIP

    try:
        url = f"{WTTR_BASE_URL}/{location}?format=j1"
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()

        # Get forecast day (0 = today, 1 = tomorrow)
        day_index = 0 if when == "today" else 1
        forecast = data["weather"][day_index]

        # Check hourly forecasts for rain
        rain_hours = []
        for i, hour in enumerate(forecast["hourly"]):
            chance = int(hour.get("chanceofrain", 0))
            if chance > 30:  # >30% chance
                time_label = ["night", "morning", "afternoon", "evening"][i // 2]
                rain_hours.append((time_label, chance))

        if rain_hours:
            # Build response for voice (keep it simple!)
            if len(rain_hours) == 1:
                time, chance = rain_hours[0]
                return f"{chance} percent chance of rain {time}"
            elif len(rain_hours) == 2:
                time1, chance1 = rain_hours[0]
                time2, chance2 = rain_hours[1]
                return f"Rain likely {time1} and {time2}"
            else:
                # Too many periods, just say "throughout the day"
                max_chance = max(chance for _, chance in rain_hours)
                return f"{max_chance} percent chance of rain throughout the day"
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
    if not location:
        location = DEFAULT_ZIP

    # Map compass abbreviations to full names for speech
    DIRECTION_MAP = {
        "N": "north",
        "NNE": "north northeast",
        "NE": "northeast",
        "ENE": "east northeast",
        "E": "east",
        "ESE": "east southeast",
        "SE": "southeast",
        "SSE": "south southeast",
        "S": "south",
        "SSW": "south southwest",
        "SW": "southwest",
        "WSW": "west southwest",
        "W": "west",
        "WNW": "west northwest",
        "NW": "northwest",
        "NNW": "north northwest",
    }

    try:
        url = f"{WTTR_BASE_URL}/{location}?format=j1"
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()

        current = data["current_condition"][0]
        speed_mph = current["windspeedMiles"]
        direction_abbr = current["winddir16Point"]
        gust_mph = current.get("WindGustMiles", speed_mph)

        # Convert abbreviation to full name
        direction = DIRECTION_MAP.get(direction_abbr, direction_abbr)

        # Classify wind
        speed = int(speed_mph)
        if speed < 5:
            desc = "calm"
        elif speed < 15:
            desc = "light"
        elif speed < 25:
            desc = "moderate"
        else:
            desc = "strong"

        response = f"Wind is {desc} at {speed_mph} miles per hour from the {direction}"

        if int(gust_mph) > speed + 5:
            response += f", gusting to {gust_mph}"

        return response

    except Exception as e:
        logger.error(f"Wind info error: {e}")
        return "Sorry, I couldn't get wind information"
