"""
Preference Manager

Store and retrieve user preferences with category-based organization.
"""

import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from .database import MemoryDatabase

logger = logging.getLogger(__name__)


class PreferenceManager:
    """Manage user preferences with SQLite storage."""

    def __init__(self, db: MemoryDatabase, user_id: str = 'default'):
        """
        Initialize preference manager.

        Args:
            db: Memory database instance
            user_id: User identifier (default: 'default')
        """
        self.db = db
        self.user_id = user_id

    def save_preference(
        self,
        category: str,
        preference_key: str,
        preference_value: Any,
        scope: str = 'default'
    ) -> bool:
        """
        Save or update a user preference.

        Args:
            category: Category of preference ('lights', 'climate', 'routines', etc.)
            preference_key: Key within category ('color', 'temperature', etc.)
            preference_value: Value (will be JSON-encoded if not string)
            scope: Scope of preference ('default', 'always', 'specific')

        Returns:
            True if saved successfully

        Example:
            >>> pref.save_preference('lights', 'default_color', 'pink')
            >>> pref.save_preference('climate', 'temperature', 72)
        """
        # Encode value as JSON if not already string
        if not isinstance(preference_value, str):
            value_str = json.dumps(preference_value)
        else:
            value_str = preference_value

        try:
            cursor = self.db.execute("""
                INSERT INTO preferences
                    (user_id, category, preference_key, preference_value, scope, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, category, preference_key)
                DO UPDATE SET
                    preference_value = excluded.preference_value,
                    scope = excluded.scope,
                    updated_at = excluded.updated_at
            """, (
                self.user_id,
                category,
                preference_key,
                value_str,
                scope,
                datetime.now().isoformat()
            ))

            self.db.commit()

            logger.info(
                f"Saved preference: {category}.{preference_key} = {preference_value} "
                f"(scope: {scope})"
            )
            return True

        except Exception as e:
            logger.error(f"Error saving preference: {e}")
            return False

    def get_preference(
        self,
        category: str,
        preference_key: str
    ) -> Optional[Any]:
        """
        Get a specific preference value.

        Args:
            category: Preference category
            preference_key: Preference key

        Returns:
            Preference value (JSON-decoded if possible), or None if not found

        Example:
            >>> pref.get_preference('lights', 'default_color')
            'pink'
        """
        cursor = self.db.execute("""
            SELECT preference_value FROM preferences
            WHERE user_id = ? AND category = ? AND preference_key = ?
        """, (self.user_id, category, preference_key))

        row = cursor.fetchone()
        if not row:
            return None

        value_str = row['preference_value']

        # Try to decode JSON, fall back to string
        try:
            return json.loads(value_str)
        except (json.JSONDecodeError, TypeError):
            return value_str

    def get_category_preferences(self, category: str) -> Dict[str, Any]:
        """
        Get all preferences in a category.

        Args:
            category: Category to retrieve

        Returns:
            Dictionary of {preference_key: value}

        Example:
            >>> pref.get_category_preferences('lights')
            {'default_color': 'pink', 'brightness': 80}
        """
        cursor = self.db.execute("""
            SELECT preference_key, preference_value FROM preferences
            WHERE user_id = ? AND category = ?
        """, (self.user_id, category))

        prefs = {}
        for row in cursor.fetchall():
            key = row['preference_key']
            value_str = row['preference_value']

            # Try to decode JSON
            try:
                prefs[key] = json.loads(value_str)
            except (json.JSONDecodeError, TypeError):
                prefs[key] = value_str

        return prefs

    def get_all_preferences(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all preferences for user, organized by category.

        Returns:
            Dictionary of {category: {preference_key: value}}

        Example:
            >>> pref.get_all_preferences()
            {
                'lights': {'default_color': 'pink'},
                'climate': {'temperature': 72}
            }
        """
        cursor = self.db.execute("""
            SELECT category, preference_key, preference_value FROM preferences
            WHERE user_id = ?
            ORDER BY category, preference_key
        """, (self.user_id,))

        prefs = {}
        for row in cursor.fetchall():
            category = row['category']
            key = row['preference_key']
            value_str = row['preference_value']

            if category not in prefs:
                prefs[category] = {}

            # Try to decode JSON
            try:
                prefs[category][key] = json.loads(value_str)
            except (json.JSONDecodeError, TypeError):
                prefs[category][key] = value_str

        return prefs

    def delete_preference(
        self,
        category: str,
        preference_key: str
    ) -> bool:
        """
        Delete a specific preference.

        Args:
            category: Preference category
            preference_key: Preference key

        Returns:
            True if deleted successfully
        """
        try:
            self.db.execute("""
                DELETE FROM preferences
                WHERE user_id = ? AND category = ? AND preference_key = ?
            """, (self.user_id, category, preference_key))

            self.db.commit()
            logger.info(f"Deleted preference: {category}.{preference_key}")
            return True

        except Exception as e:
            logger.error(f"Error deleting preference: {e}")
            return False

    def delete_category(self, category: str) -> bool:
        """
        Delete all preferences in a category.

        Args:
            category: Category to delete

        Returns:
            True if deleted successfully
        """
        try:
            self.db.execute("""
                DELETE FROM preferences
                WHERE user_id = ? AND category = ?
            """, (self.user_id, category))

            self.db.commit()
            logger.info(f"Deleted all preferences in category: {category}")
            return True

        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            return False

    def format_for_display(self) -> str:
        """
        Format preferences for human-readable display.

        Returns:
            Formatted string of all preferences
        """
        all_prefs = self.get_all_preferences()

        if not all_prefs:
            return "No preferences saved."

        lines = []
        for category, prefs in sorted(all_prefs.items()):
            lines.append(f"\n{category.upper()}:")
            for key, value in sorted(prefs.items()):
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)
