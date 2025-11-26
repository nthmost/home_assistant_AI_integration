"""
Weather API Adapters V2 - 5-Day Forecasts

Fetch 5-day forecasts from multiple weather APIs.
"""

import logging
import os
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class WeatherAPIV2(ABC):
    """Base class for weather API adapters with 5-day support."""

    @abstractmethod
    def fetch(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Fetch weather data.

        Args:
            location: ZIP code or city name

        Returns:
            Dict with 'current' and 'forecasts' keys, or None on failure

        Schema:
            {
                'current': {
                    'temp_f': int,
                    'condition': str,
                    'feels_like_f': int,
                    'humidity': int
                },
                'forecasts': [
                    {
                        'date': 'YYYY-MM-DD',
                        'high_f': int,
                        'low_f': int,
                        'condition': str,
                        'rain_chance': int,
                        'wind_speed_mph': int,
                        'wind_direction': str
                    },
                    ... (up to 5 days)
                ]
            }
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """API name for logging."""
        pass


class OpenWeatherMapAPIV2(WeatherAPIV2):
    """OpenWeatherMap adapter with 5-day forecast support."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')

    @property
    def name(self) -> str:
        return "OpenWeatherMap"

    def fetch(self, location: str) -> Optional[Dict[str, Any]]:
        """Fetch 5-day forecast from OpenWeatherMap."""
        if not self.api_key:
            logger.debug("OpenWeatherMap: No API key configured")
            return None

        try:
            # Fetch forecast (includes current + 5 days in 3hr intervals)
            url = f"{self.BASE_URL}/forecast"
            params = {
                'zip': f"{location},US",
                'appid': self.api_key,
                'units': 'imperial'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Parse current (first forecast point)
            first = data['list'][0]
            current = {
                'temp_f': int(first['main']['temp']),
                'condition': first['weather'][0]['description'].title(),
                'feels_like_f': int(first['main']['feels_like']),
                'humidity': int(first['main']['humidity'])
            }

            # Parse daily forecasts (group by date, take highs/lows)
            daily_forecasts = self._group_by_day(data['list'])

            logger.info(f"✅ {self.name}: Fetched {len(daily_forecasts)} days for {location}")
            return {
                'current': current,
                'forecasts': daily_forecasts
            }

        except requests.RequestException as e:
            logger.warning(f"⚠️  {self.name}: Request failed: {e}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            logger.error(f"❌ {self.name}: Parse error: {e}")
            return None

    def _group_by_day(self, forecast_list: List[Dict]) -> List[Dict[str, Any]]:
        """
        Group 3-hour forecasts into daily summaries.

        Args:
            forecast_list: List of 3-hour forecast points

        Returns:
            List of daily forecast dicts (up to 5 days)
        """
        daily = {}

        for item in forecast_list:
            # Extract date (YYYY-MM-DD)
            dt = datetime.fromtimestamp(item['dt'])
            date_key = dt.strftime('%Y-%m-%d')

            if date_key not in daily:
                daily[date_key] = {
                    'date': date_key,
                    'highs': [],
                    'lows': [],
                    'conditions': [],
                    'rain_chances': [],
                    'wind_speeds': [],
                    'wind_dirs': []
                }

            daily[date_key]['highs'].append(item['main']['temp_max'])
            daily[date_key]['lows'].append(item['main']['temp_min'])
            daily[date_key]['conditions'].append(item['weather'][0]['description'])
            daily[date_key]['rain_chances'].append(item.get('pop', 0) * 100)
            daily[date_key]['wind_speeds'].append(item['wind']['speed'])
            daily[date_key]['wind_dirs'].append(self._degrees_to_direction(item['wind']['deg']))

        # Convert to final format
        result = []
        for date_key in sorted(daily.keys())[:5]:  # Limit to 5 days
            day_data = daily[date_key]
            result.append({
                'date': date_key,
                'high_f': int(max(day_data['highs'])),
                'low_f': int(min(day_data['lows'])),
                'condition': max(set(day_data['conditions']), key=day_data['conditions'].count).title(),
                'rain_chance': int(max(day_data['rain_chances'])),
                'wind_speed_mph': int(sum(day_data['wind_speeds']) / len(day_data['wind_speeds'])),
                'wind_direction': max(set(day_data['wind_dirs']), key=day_data['wind_dirs'].count)
            })

        return result

    def _degrees_to_direction(self, degrees: float) -> str:
        """Convert wind degrees to cardinal direction."""
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        idx = int((degrees + 11.25) / 22.5) % 16
        return directions[idx]


class WeatherFetcherV2:
    """Weather fetcher with 5-day forecast support."""

    def __init__(self):
        self.api = OpenWeatherMapAPIV2()  # Primary API for now

    def fetch(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Fetch 5-day weather forecast.

        Args:
            location: ZIP code

        Returns:
            Weather data dict with 'current' and 'forecasts', or None if failed
        """
        logger.debug(f"Fetching 5-day forecast for {location}...")
        return self.api.fetch(location)
