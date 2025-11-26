"""
Timer Sound Management - Custom sounds for different timer types.

Allows users to associate unique sounds with timer types (laundry, tea, meditation, etc.)
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class TimerSoundManager:
    """Manage custom sounds for timer types."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize timer sound manager.

        Args:
            db_path: Path to SQLite database (defaults to ~/.saga_assistant/timer_sounds.db)
        """
        if db_path is None:
            db_path = Path.home() / '.saga_assistant' / 'timer_sounds.db'

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Path to sound files
        self.sounds_dir = Path(__file__).parent / 'sounds' / 'timers'

        self._init_db()

    def _init_db(self):
        """Create database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Timer types and their assigned sounds
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timer_sounds (
                timer_type TEXT PRIMARY KEY,
                sound_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP
            )
        """)

        # Default mappings (optional, user can override)
        defaults = {
            'laundry': 'laundry',
            'tea': 'tea',
            'meditation': 'meditation',
            'cooking': 'cooking',
            'kitchen': 'kitchen',
            'workout': 'workout',
            'exercise': 'workout',
            'bike': 'bike',
            'pomodoro': 'pomodoro',
            'work': 'pomodoro',
            'parking': 'parking',
        }

        for timer_type, sound_name in defaults.items():
            cursor.execute("""
                INSERT OR IGNORE INTO timer_sounds (timer_type, sound_name)
                VALUES (?, ?)
            """, (timer_type, sound_name))

        conn.commit()
        conn.close()

        logger.debug(f"Timer sounds database initialized: {self.db_path}")

    def get_sound_for_timer(self, timer_type: str) -> Optional[str]:
        """
        Get the sound file path for a timer type.

        Args:
            timer_type: Timer type (e.g., "laundry", "tea")

        Returns:
            Path to sound file, or None if not assigned
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT sound_name FROM timer_sounds WHERE timer_type = ?
        """, (timer_type.lower(),))

        row = cursor.fetchone()
        conn.close()

        if row:
            sound_name = row[0]
            sound_path = self.sounds_dir / f"{sound_name}.wav"

            if sound_path.exists():
                return str(sound_path)
            else:
                logger.warning(f"Sound file not found: {sound_path}")
                return None

        return None

    def set_sound_for_timer(self, timer_type: str, sound_name: str) -> bool:
        """
        Associate a sound with a timer type.

        Args:
            timer_type: Timer type (e.g., "laundry")
            sound_name: Sound name (e.g., "laundry", "kitchen", "tea")

        Returns:
            True if successful
        """
        # Validate sound exists
        sound_path = self.sounds_dir / f"{sound_name}.wav"
        if not sound_path.exists():
            logger.error(f"Sound '{sound_name}' does not exist")
            return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO timer_sounds (timer_type, sound_name)
            VALUES (?, ?)
        """, (timer_type.lower(), sound_name))

        conn.commit()
        conn.close()

        logger.info(f"✅ Assigned '{sound_name}' sound to '{timer_type}' timer")
        return True

    def get_available_sounds(self) -> List[Dict[str, str]]:
        """
        Get list of available timer sounds.

        Returns:
            List of dicts with 'name' and 'description' keys
        """
        sounds = []

        # Sound descriptions
        descriptions = {
            'kitchen': 'Classic kitchen timer bell - three dings',
            'tea': 'Tea kettle whistle',
            'meditation': 'Singing bowl / meditation chime',
            'laundry': 'Pleasant two-tone doorbell chime',
            'cooking': 'Friendly triple beep',
            'workout': 'Energetic ascending beeps',
            'bike': 'Bike bell - two short dings',
            'pomodoro': 'Work timer - single decisive tone',
            'parking': 'Urgent alert - fast triple beep',
            'default': 'Generic pleasant two-tone beep',
        }

        for sound_file in sorted(self.sounds_dir.glob("*.wav")):
            name = sound_file.stem
            sounds.append({
                'name': name,
                'description': descriptions.get(name, name.title()),
                'path': str(sound_file)
            })

        return sounds

    def has_sound_for_timer(self, timer_type: str) -> bool:
        """
        Check if a timer type has an assigned sound.

        Args:
            timer_type: Timer type to check

        Returns:
            True if sound is assigned
        """
        return self.get_sound_for_timer(timer_type) is not None

    def get_default_sound(self) -> str:
        """
        Get path to default timer sound.

        Returns:
            Path to default.wav
        """
        default_path = self.sounds_dir / "default.wav"
        if default_path.exists():
            return str(default_path)
        else:
            logger.error("Default sound not found!")
            return None

    def update_last_used(self, timer_type: str):
        """
        Update last_used timestamp for a timer type.

        Args:
            timer_type: Timer type
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE timer_sounds
            SET last_used = CURRENT_TIMESTAMP
            WHERE timer_type = ?
        """, (timer_type.lower(),))

        conn.commit()
        conn.close()
