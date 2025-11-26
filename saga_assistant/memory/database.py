"""
Memory Database

SQLite database for storing user preferences, facts, and conversation history.
Designed to be simple, queryable, and multi-user ready.
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class MemoryDatabase:
    """SQLite database for Saga's memory system."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize memory database.

        Args:
            db_path: Path to SQLite database file.
                     Defaults to ~/.saga_assistant/memory.db
        """
        if db_path is None:
            db_path = Path.home() / '.saga_assistant' / 'memory.db'

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = None
        self._connect()
        self._create_schema()

    def _connect(self):
        """Connect to SQLite database."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Return rows as dicts
        logger.info(f"Connected to memory database: {self.db_path}")

    def _create_schema(self):
        """Create database schema if it doesn't exist."""
        cursor = self.conn.cursor()

        # User preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                category TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                scope TEXT DEFAULT 'default',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, category, preference_key)
            )
        """)

        # Facts to remember table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                fact_type TEXT NOT NULL,
                content TEXT NOT NULL,
                structured_data TEXT,
                relevance_tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        """)

        # Conversation log table (optional, for future)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                session_id TEXT NOT NULL,
                turn_number INTEGER NOT NULL,
                user_utterance TEXT,
                saga_response TEXT,
                intent_detected TEXT,
                memory_created BOOLEAN DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Session state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'default',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context_summary TEXT,
                active_tasks TEXT
            )
        """)

        self.conn.commit()
        logger.info("Database schema created/verified")

    def execute(self, query: str, params: tuple = ()):
        """
        Execute a query and return cursor.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Cursor with results
        """
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor

    def commit(self):
        """Commit current transaction."""
        self.conn.commit()

    def clear_all_memory(self, user_id: str = 'default'):
        """
        Clear all memory for a user (preferences, facts, etc.).

        Args:
            user_id: User to clear memory for
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM preferences WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM facts WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM conversation_log WHERE user_id = ?", (user_id,))
        self.conn.commit()
        logger.info(f"Cleared all memory for user: {user_id}")

    def get_stats(self, user_id: str = 'default') -> dict:
        """
        Get memory statistics for a user.

        Args:
            user_id: User to get stats for

        Returns:
            Dictionary with counts of preferences, facts, etc.
        """
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM preferences WHERE user_id = ?", (user_id,))
        pref_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM facts WHERE user_id = ?", (user_id,))
        fact_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM conversation_log WHERE user_id = ?", (user_id,))
        conv_count = cursor.fetchone()[0]

        return {
            'preferences': pref_count,
            'facts': fact_count,
            'conversations': conv_count
        }

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
