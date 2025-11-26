"""
Weather Cache V2 - Multi-Location, 5-Day Forecasts

Stores weather for multiple locations with 5-day forecasts.
Perfect for bike ride planning across Bay Area microclimates.
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class DailyForecast:
    """Single day forecast data."""

    def __init__(self, row: sqlite3.Row):
        self.location = row['location']
        self.date = row['date']
        self.high_f = row['high_f']
        self.low_f = row['low_f']
        self.condition = row['condition']
        self.rain_chance = row['rain_chance']
        self.wind_speed_mph = row['wind_speed_mph']
        self.wind_direction = row['wind_direction']

    def to_dict(self) -> Dict[str, Any]:
        return {
            'location': self.location,
            'date': self.date,
            'high_f': self.high_f,
            'low_f': self.low_f,
            'condition': self.condition,
            'rain_chance': self.rain_chance,
            'wind_speed_mph': self.wind_speed_mph,
            'wind_direction': self.wind_direction
        }


class LocationWeather:
    """Complete weather for a location."""

    def __init__(self, location: str, current: Dict[str, Any], forecasts: List[DailyForecast], updated_at: datetime):
        self.location = location
        self.current_temp_f = current['temp_f']
        self.current_condition = current['condition']
        self.current_feels_like_f = current['feels_like_f']
        self.current_humidity = current['humidity']
        self.forecasts = forecasts  # List of 5 DailyForecast objects
        self.updated_at = updated_at

    def is_stale(self, threshold_minutes: int = 30) -> bool:
        """Check if data is stale."""
        age = datetime.now() - self.updated_at
        return age > timedelta(minutes=threshold_minutes)

    def get_forecast_for_day(self, day_offset: int) -> Optional[DailyForecast]:
        """
        Get forecast for specific day.

        Args:
            day_offset: 0=today, 1=tomorrow, 2=day after, etc.

        Returns:
            DailyForecast or None if not available
        """
        if 0 <= day_offset < len(self.forecasts):
            return self.forecasts[day_offset]
        return None


class WeatherCacheV2:
    """Multi-location weather cache with 5-day forecasts."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path.home() / '.saga_assistant' / 'weather_v2.db'

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def _init_db(self):
        """Create database schema."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Current conditions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS current_weather (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL UNIQUE,
                temp_f INTEGER NOT NULL,
                condition TEXT NOT NULL,
                feels_like_f INTEGER NOT NULL,
                humidity INTEGER NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """)

        # Daily forecasts table (5 days per location)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                date TEXT NOT NULL,
                high_f INTEGER NOT NULL,
                low_f INTEGER NOT NULL,
                condition TEXT NOT NULL,
                rain_chance INTEGER NOT NULL,
                wind_speed_mph INTEGER NOT NULL,
                wind_direction TEXT NOT NULL,
                UNIQUE(location, date)
            )
        """)

        # Index for fast location lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_location
            ON daily_forecasts(location)
        """)

        conn.commit()
        conn.close()

        logger.debug(f"Weather cache V2 initialized: {self.db_path}")

    def set(self, location: str, current: Dict[str, Any], forecasts: List[Dict[str, Any]]) -> bool:
        """
        Update weather for a location.

        Args:
            location: Location name (e.g., "San Francisco", "Marin City")
            current: Current conditions dict with keys: temp_f, condition, feels_like_f, humidity
            forecasts: List of daily forecast dicts (up to 5 days)

        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Update current conditions
            cursor.execute("""
                INSERT INTO current_weather (location, temp_f, condition, feels_like_f, humidity, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(location) DO UPDATE SET
                    temp_f = excluded.temp_f,
                    condition = excluded.condition,
                    feels_like_f = excluded.feels_like_f,
                    humidity = excluded.humidity,
                    updated_at = excluded.updated_at
            """, (
                location,
                current['temp_f'],
                current['condition'],
                current['feels_like_f'],
                current['humidity'],
                datetime.now().isoformat()
            ))

            # Clear old forecasts for this location
            cursor.execute("DELETE FROM daily_forecasts WHERE location = ?", (location,))

            # Insert new forecasts
            for forecast in forecasts:
                cursor.execute("""
                    INSERT INTO daily_forecasts
                    (location, date, high_f, low_f, condition, rain_chance, wind_speed_mph, wind_direction)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    location,
                    forecast['date'],
                    forecast['high_f'],
                    forecast['low_f'],
                    forecast['condition'],
                    forecast['rain_chance'],
                    forecast['wind_speed_mph'],
                    forecast['wind_direction']
                ))

            conn.commit()
            conn.close()

            logger.info(f"✅ Updated weather for {location} ({len(forecasts)} days)")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update weather cache: {e}")
            return False

    def _normalize_location(self, location: str) -> Optional[str]:
        """
        Normalize location name to match cached entries.

        Supports case-insensitive matching and common aliases.

        Args:
            location: User input location name

        Returns:
            Canonical location name or None if not found
        """
        # Common aliases
        aliases = {
            'sf': 'San Francisco',
            'san fran': 'San Francisco',
            'marin': 'Marin City',
            'daly': 'Daly City',
            'sausilito': 'Sausalito',  # Common misspelling
        }

        # Check aliases first
        location_lower = location.lower().strip()
        if location_lower in aliases:
            return aliases[location_lower]

        # Get all cached locations for fuzzy matching
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT location FROM current_weather")
            cached_locations = [row[0] for row in cursor.fetchall()]
            conn.close()

            # Try case-insensitive exact match
            for cached in cached_locations:
                if cached.lower() == location_lower:
                    return cached

            # Try partial match (e.g., "francisco" matches "San Francisco")
            for cached in cached_locations:
                if location_lower in cached.lower() or cached.lower() in location_lower:
                    return cached

        except Exception as e:
            logger.error(f"Location normalization error: {e}")

        return None

    def get(self, location: str) -> Optional[LocationWeather]:
        """
        Get weather for a location.

        Args:
            location: Location name (supports fuzzy matching)

        Returns:
            LocationWeather or None if not cached
        """
        # Normalize location name
        normalized_location = self._normalize_location(location)
        if not normalized_location:
            logger.debug(f"Location '{location}' not found in cache")
            return None

        if normalized_location != location:
            logger.debug(f"Matched '{location}' → '{normalized_location}'")

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get current conditions
            cursor.execute("""
                SELECT * FROM current_weather WHERE location = ?
            """, (normalized_location,))
            current_row = cursor.fetchone()

            if not current_row:
                conn.close()
                return None

            # Get forecasts
            cursor.execute("""
                SELECT * FROM daily_forecasts
                WHERE location = ?
                ORDER BY date
            """, (normalized_location,))
            forecast_rows = cursor.fetchall()

            conn.close()

            # Build objects
            current = {
                'temp_f': current_row['temp_f'],
                'condition': current_row['condition'],
                'feels_like_f': current_row['feels_like_f'],
                'humidity': current_row['humidity']
            }

            forecasts = [DailyForecast(row) for row in forecast_rows]
            updated_at = datetime.fromisoformat(current_row['updated_at'])

            return LocationWeather(normalized_location, current, forecasts, updated_at)

        except Exception as e:
            logger.error(f"❌ Failed to get weather: {e}")
            return None

    def get_all_locations(self) -> List[str]:
        """Get list of all cached locations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT location FROM current_weather ORDER BY location")
        locations = [row[0] for row in cursor.fetchall()]

        conn.close()
        return locations
