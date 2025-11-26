"""
Weather Cache

SQLite-based weather cache with staleness detection.
Stores current conditions and forecasts for fast, offline-capable access.
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class WeatherData:
    """Weather data container with staleness checking."""

    def __init__(self, row: sqlite3.Row):
        """
        Initialize from database row.

        Args:
            row: SQLite row with weather data
        """
        self.zip_code = row['zip_code']
        self.current_temp_f = row['current_temp_f']
        self.current_condition = row['current_condition']
        self.current_feels_like_f = row['current_feels_like_f']
        self.current_humidity = row['current_humidity']
        self.today_high_f = row['today_high_f']
        self.today_low_f = row['today_low_f']
        self.today_condition = row['today_condition']
        self.today_rain_chance = row['today_rain_chance']
        self.tomorrow_high_f = row['tomorrow_high_f']
        self.tomorrow_low_f = row['tomorrow_low_f']
        self.tomorrow_condition = row['tomorrow_condition']
        self.tomorrow_rain_chance = row['tomorrow_rain_chance']
        self.wind_speed_mph = row['wind_speed_mph']
        self.wind_direction = row['wind_direction']
        self.updated_at = datetime.fromisoformat(row['updated_at'])

    def is_stale(self, threshold_minutes: int = 30) -> bool:
        """
        Check if data is stale.

        Args:
            threshold_minutes: Minutes before data is considered stale

        Returns:
            True if data is older than threshold
        """
        age = datetime.now() - self.updated_at
        return age > timedelta(minutes=threshold_minutes)

    def age_minutes(self) -> int:
        """Get age of data in minutes."""
        age = datetime.now() - self.updated_at
        return int(age.total_seconds() / 60)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'zip_code': self.zip_code,
            'current_temp_f': self.current_temp_f,
            'current_condition': self.current_condition,
            'current_feels_like_f': self.current_feels_like_f,
            'current_humidity': self.current_humidity,
            'today_high_f': self.today_high_f,
            'today_low_f': self.today_low_f,
            'today_condition': self.today_condition,
            'today_rain_chance': self.today_rain_chance,
            'tomorrow_high_f': self.tomorrow_high_f,
            'tomorrow_low_f': self.tomorrow_low_f,
            'tomorrow_condition': self.tomorrow_condition,
            'tomorrow_rain_chance': self.tomorrow_rain_chance,
            'wind_speed_mph': self.wind_speed_mph,
            'wind_direction': self.wind_direction,
            'updated_at': self.updated_at.isoformat(),
            'age_minutes': self.age_minutes()
        }


class WeatherCache:
    """SQLite-based weather cache."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize weather cache.

        Args:
            db_path: Path to SQLite database (defaults to ~/.saga_assistant/weather.db)
        """
        if db_path is None:
            db_path = Path.home() / '.saga_assistant' / 'weather.db'

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_db()

    def _init_db(self):
        """Create database schema if needed."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zip_code TEXT NOT NULL,
                current_temp_f INTEGER,
                current_condition TEXT,
                current_feels_like_f INTEGER,
                current_humidity INTEGER,
                today_high_f INTEGER,
                today_low_f INTEGER,
                today_condition TEXT,
                today_rain_chance INTEGER,
                tomorrow_high_f INTEGER,
                tomorrow_low_f INTEGER,
                tomorrow_condition TEXT,
                tomorrow_rain_chance INTEGER,
                wind_speed_mph INTEGER,
                wind_direction TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(zip_code)
            )
        """)

        conn.commit()
        conn.close()

        logger.debug(f"Weather cache initialized: {self.db_path}")

    def get(self, zip_code: str) -> Optional[WeatherData]:
        """
        Get cached weather data.

        Args:
            zip_code: ZIP code

        Returns:
            WeatherData or None if not cached
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM weather_cache WHERE zip_code = ?
        """, (zip_code,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return WeatherData(row)
        return None

    def set(self, zip_code: str, data: Dict[str, Any]) -> bool:
        """
        Update cached weather data.

        Args:
            zip_code: ZIP code
            data: Weather data dictionary with keys matching schema

        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO weather_cache (
                    zip_code,
                    current_temp_f,
                    current_condition,
                    current_feels_like_f,
                    current_humidity,
                    today_high_f,
                    today_low_f,
                    today_condition,
                    today_rain_chance,
                    tomorrow_high_f,
                    tomorrow_low_f,
                    tomorrow_condition,
                    tomorrow_rain_chance,
                    wind_speed_mph,
                    wind_direction,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(zip_code) DO UPDATE SET
                    current_temp_f = excluded.current_temp_f,
                    current_condition = excluded.current_condition,
                    current_feels_like_f = excluded.current_feels_like_f,
                    current_humidity = excluded.current_humidity,
                    today_high_f = excluded.today_high_f,
                    today_low_f = excluded.today_low_f,
                    today_condition = excluded.today_condition,
                    today_rain_chance = excluded.today_rain_chance,
                    tomorrow_high_f = excluded.tomorrow_high_f,
                    tomorrow_low_f = excluded.tomorrow_low_f,
                    tomorrow_condition = excluded.tomorrow_condition,
                    tomorrow_rain_chance = excluded.tomorrow_rain_chance,
                    wind_speed_mph = excluded.wind_speed_mph,
                    wind_direction = excluded.wind_direction,
                    updated_at = excluded.updated_at
            """, (
                zip_code,
                data.get('current_temp_f'),
                data.get('current_condition'),
                data.get('current_feels_like_f'),
                data.get('current_humidity'),
                data.get('today_high_f'),
                data.get('today_low_f'),
                data.get('today_condition'),
                data.get('today_rain_chance'),
                data.get('tomorrow_high_f'),
                data.get('tomorrow_low_f'),
                data.get('tomorrow_condition'),
                data.get('tomorrow_rain_chance'),
                data.get('wind_speed_mph'),
                data.get('wind_direction'),
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

            logger.info(f"✅ Weather cache updated for {zip_code}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update weather cache: {e}")
            return False

    def clear(self, zip_code: Optional[str] = None):
        """
        Clear cache.

        Args:
            zip_code: Clear specific ZIP code, or all if None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if zip_code:
            cursor.execute("DELETE FROM weather_cache WHERE zip_code = ?", (zip_code,))
            logger.info(f"Cleared weather cache for {zip_code}")
        else:
            cursor.execute("DELETE FROM weather_cache")
            logger.info("Cleared all weather cache")

        conn.commit()
        conn.close()
