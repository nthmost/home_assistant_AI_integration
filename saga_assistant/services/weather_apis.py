"""
Weather API Adapters

Adapters for multiple weather APIs with unified interface and fallback chain.
"""

import logging
import os
import requests
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class WeatherAPI(ABC):
    """Base class for weather API adapters."""

    @abstractmethod
    def fetch(self, zip_code: str) -> Optional[Dict[str, Any]]:
        """
        Fetch weather data.

        Args:
            zip_code: ZIP code

        Returns:
            Normalized weather data dict or None on failure

        Schema:
            {
                'current_temp_f': int,
                'current_condition': str,
                'current_feels_like_f': int,
                'current_humidity': int,
                'today_high_f': int,
                'today_low_f': int,
                'today_condition': str,
                'today_rain_chance': int,
                'tomorrow_high_f': int,
                'tomorrow_low_f': int,
                'tomorrow_condition': str,
                'tomorrow_rain_chance': int,
                'wind_speed_mph': int,
                'wind_direction': str
            }
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """API name for logging."""
        pass


class OpenWeatherMapAPI(WeatherAPI):
    """OpenWeatherMap adapter (primary API)."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenWeatherMap API.

        Args:
            api_key: API key (defaults to OPENWEATHER_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')

    @property
    def name(self) -> str:
        return "OpenWeatherMap"

    def fetch(self, zip_code: str) -> Optional[Dict[str, Any]]:
        """Fetch from OpenWeatherMap."""
        if not self.api_key:
            logger.debug("OpenWeatherMap: No API key configured")
            return None

        try:
            # Fetch current + forecast
            url = f"{self.BASE_URL}/forecast"
            params = {
                'zip': f"{zip_code},US",
                'appid': self.api_key,
                'units': 'imperial'  # Fahrenheit
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Parse response
            current = data['list'][0]  # First forecast point (now)
            today_forecasts = [f for f in data['list'][:8]]  # Next 24 hours (3hr intervals)
            tomorrow_forecasts = [f for f in data['list'][8:16]]  # Next 24-48 hours

            # Extract data
            result = {
                'current_temp_f': int(current['main']['temp']),
                'current_condition': current['weather'][0]['description'].title(),
                'current_feels_like_f': int(current['main']['feels_like']),
                'current_humidity': int(current['main']['humidity']),
                'today_high_f': int(max(f['main']['temp_max'] for f in today_forecasts)),
                'today_low_f': int(min(f['main']['temp_min'] for f in today_forecasts)),
                'today_condition': today_forecasts[0]['weather'][0]['description'].title(),
                'today_rain_chance': int(max((f.get('pop', 0) * 100 for f in today_forecasts), default=0)),
                'tomorrow_high_f': int(max(f['main']['temp_max'] for f in tomorrow_forecasts)) if tomorrow_forecasts else None,
                'tomorrow_low_f': int(min(f['main']['temp_min'] for f in tomorrow_forecasts)) if tomorrow_forecasts else None,
                'tomorrow_condition': tomorrow_forecasts[0]['weather'][0]['description'].title() if tomorrow_forecasts else None,
                'tomorrow_rain_chance': int(max((f.get('pop', 0) * 100 for f in tomorrow_forecasts), default=0)) if tomorrow_forecasts else None,
                'wind_speed_mph': int(current['wind']['speed']),
                'wind_direction': self._degrees_to_direction(current['wind']['deg'])
            }

            logger.info(f"✅ {self.name}: Fetched weather for {zip_code}")
            return result

        except requests.RequestException as e:
            logger.warning(f"⚠️  {self.name}: Request failed: {e}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            logger.error(f"❌ {self.name}: Parse error: {e}")
            return None

    def _degrees_to_direction(self, degrees: float) -> str:
        """Convert wind degrees to cardinal direction."""
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        idx = int((degrees + 11.25) / 22.5) % 16
        return directions[idx]


class WeatherAPIcom(WeatherAPI):
    """WeatherAPI.com adapter (secondary API)."""

    BASE_URL = "https://api.weatherapi.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize WeatherAPI.com.

        Args:
            api_key: API key (defaults to WEATHERAPI_KEY env var)
        """
        self.api_key = api_key or os.getenv('WEATHERAPI_KEY')

    @property
    def name(self) -> str:
        return "WeatherAPI.com"

    def fetch(self, zip_code: str) -> Optional[Dict[str, Any]]:
        """Fetch from WeatherAPI.com."""
        if not self.api_key:
            logger.debug("WeatherAPI.com: No API key configured")
            return None

        try:
            # Fetch forecast (includes current + 3 days)
            url = f"{self.BASE_URL}/forecast.json"
            params = {
                'key': self.api_key,
                'q': zip_code,
                'days': 2  # Today + tomorrow
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Parse response
            current = data['current']
            today = data['forecast']['forecastday'][0]
            tomorrow = data['forecast']['forecastday'][1] if len(data['forecast']['forecastday']) > 1 else None

            result = {
                'current_temp_f': int(current['temp_f']),
                'current_condition': current['condition']['text'],
                'current_feels_like_f': int(current['feelslike_f']),
                'current_humidity': int(current['humidity']),
                'today_high_f': int(today['day']['maxtemp_f']),
                'today_low_f': int(today['day']['mintemp_f']),
                'today_condition': today['day']['condition']['text'],
                'today_rain_chance': int(today['day']['daily_chance_of_rain']),
                'tomorrow_high_f': int(tomorrow['day']['maxtemp_f']) if tomorrow else None,
                'tomorrow_low_f': int(tomorrow['day']['mintemp_f']) if tomorrow else None,
                'tomorrow_condition': tomorrow['day']['condition']['text'] if tomorrow else None,
                'tomorrow_rain_chance': int(tomorrow['day']['daily_chance_of_rain']) if tomorrow else None,
                'wind_speed_mph': int(current['wind_mph']),
                'wind_direction': current['wind_dir']
            }

            logger.info(f"✅ {self.name}: Fetched weather for {zip_code}")
            return result

        except requests.RequestException as e:
            logger.warning(f"⚠️  {self.name}: Request failed: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"❌ {self.name}: Parse error: {e}")
            return None


class WttrInAPI(WeatherAPI):
    """wttr.in adapter (fallback API, no key needed)."""

    BASE_URL = "https://wttr.in"

    @property
    def name(self) -> str:
        return "wttr.in"

    def fetch(self, zip_code: str) -> Optional[Dict[str, Any]]:
        """Fetch from wttr.in (last resort)."""
        try:
            url = f"{self.BASE_URL}/{zip_code}"
            params = {'format': 'j1'}

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Parse response
            current = data['current_condition'][0]
            today = data['weather'][0]
            tomorrow = data['weather'][1] if len(data['weather']) > 1 else None

            result = {
                'current_temp_f': int(current['temp_F']),
                'current_condition': current['weatherDesc'][0]['value'],
                'current_feels_like_f': int(current['FeelsLikeF']),
                'current_humidity': int(current['humidity']),
                'today_high_f': int(today['maxtempF']),
                'today_low_f': int(today['mintempF']),
                'today_condition': today['hourly'][0]['weatherDesc'][0]['value'],
                'today_rain_chance': int(today['hourly'][0]['chanceofrain']),
                'tomorrow_high_f': int(tomorrow['maxtempF']) if tomorrow else None,
                'tomorrow_low_f': int(tomorrow['mintempF']) if tomorrow else None,
                'tomorrow_condition': tomorrow['hourly'][0]['weatherDesc'][0]['value'] if tomorrow else None,
                'tomorrow_rain_chance': int(tomorrow['hourly'][0]['chanceofrain']) if tomorrow else None,
                'wind_speed_mph': int(current['windspeedMiles']),
                'wind_direction': current['winddir16Point']
            }

            logger.info(f"✅ {self.name}: Fetched weather for {zip_code}")
            return result

        except requests.RequestException as e:
            logger.warning(f"⚠️  {self.name}: Request failed: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"❌ {self.name}: Parse error: {e}")
            return None


class WeatherFetcher:
    """Weather fetcher with fallback chain."""

    def __init__(self):
        """Initialize with all available APIs."""
        self.apis = [
            OpenWeatherMapAPI(),
            WeatherAPIcom(),
            WttrInAPI()
        ]

    def fetch(self, zip_code: str) -> Optional[Dict[str, Any]]:
        """
        Fetch weather with fallback chain.

        Tries APIs in order until one succeeds.

        Args:
            zip_code: ZIP code

        Returns:
            Weather data dict or None if all APIs fail
        """
        for api in self.apis:
            logger.debug(f"Trying {api.name}...")
            data = api.fetch(zip_code)

            if data:
                return data

            logger.info(f"⚠️  {api.name} failed, trying next API...")

        logger.error("❌ All weather APIs failed")
        return None
