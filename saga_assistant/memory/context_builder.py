"""
Context Builder

Build LLM context from memory (preferences, facts, session state).
Injects relevant memory into system prompts for personalized responses.
"""

import logging
from typing import Dict, List, Any, Optional

from .database import MemoryDatabase
from .preferences import PreferenceManager

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Build LLM context from memory system."""

    def __init__(self, db: MemoryDatabase, user_id: str = 'default'):
        """
        Initialize context builder.

        Args:
            db: Memory database instance
            user_id: User identifier
        """
        self.db = db
        self.user_id = user_id
        self.pref_manager = PreferenceManager(db, user_id)

    def build_context(
        self,
        utterance: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build context for LLM from relevant memories.

        Args:
            utterance: User's current utterance (for relevance filtering)
            category: Specific category to retrieve preferences for

        Returns:
            Dictionary with preferences, facts, and context summary

        Example:
            >>> builder.build_context(category="lights")
            {
                "preferences": {"default_color": "pink"},
                "facts": [],
                "context_summary": "User prefers pink lights."
            }
        """
        context = {
            "preferences": {},
            "facts": [],
            "context_summary": None
        }

        # Get preferences
        if category:
            # Get specific category preferences
            context["preferences"] = self.pref_manager.get_category_preferences(category)
        else:
            # Get all preferences
            context["preferences"] = self.pref_manager.get_all_preferences()

        # Build human-readable summary
        context["context_summary"] = self._build_summary(context)

        return context

    def _build_summary(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Build human-readable summary of context.

        Args:
            context: Context dictionary

        Returns:
            Summary string or None if no context
        """
        parts = []

        # Summarize preferences
        prefs = context.get("preferences", {})
        if prefs:
            if isinstance(prefs, dict):
                # Check if it's categorized (dict of dicts) or flat
                if prefs and isinstance(next(iter(prefs.values())), dict):
                    # Categorized preferences
                    for category, category_prefs in prefs.items():
                        for key, value in category_prefs.items():
                            parts.append(f"For {category}, {key}: {value}")
                else:
                    # Flat preferences
                    for key, value in prefs.items():
                        parts.append(f"{key}: {value}")

        # Summarize facts (Phase 2)
        facts = context.get("facts", [])
        if facts:
            parts.extend([f"Fact: {fact}" for fact in facts[:3]])  # Limit to 3

        if not parts:
            return None

        return " ".join(parts)

    def format_for_system_prompt(
        self,
        base_prompt: str,
        utterance: Optional[str] = None,
        category: Optional[str] = None
    ) -> str:
        """
        Format context for injection into system prompt.

        Args:
            base_prompt: Base system prompt
            utterance: User's current utterance
            category: Specific category to focus on

        Returns:
            Enhanced system prompt with memory context

        Example:
            >>> base = "You are Saga, a helpful assistant."
            >>> enhanced = builder.format_for_system_prompt(base, category="lights")
            # Returns: "You are Saga, a helpful assistant.
            #
            # USER PREFERENCES:
            # For lights, default_color: pink
            #
            # Use this information to personalize your responses."
        """
        context = self.build_context(utterance, category)

        if not context["context_summary"]:
            # No context to add
            return base_prompt

        # Build context section
        context_section = "\n\nUSER CONTEXT:\n"

        # Add preferences
        if context["preferences"]:
            context_section += self._format_preferences(context["preferences"])

        # Add facts (Phase 2)
        if context["facts"]:
            context_section += "\n\nREMEMBERED FACTS:\n"
            for fact in context["facts"][:5]:
                context_section += f"- {fact}\n"

        context_section += "\nUse this information to personalize your responses."

        return base_prompt + context_section

    def _format_preferences(self, preferences: Dict[str, Any]) -> str:
        """
        Format preferences for display in prompt.

        Args:
            preferences: Preferences dictionary

        Returns:
            Formatted string
        """
        if not preferences:
            return ""

        lines = []

        # Check if categorized or flat
        if preferences and isinstance(next(iter(preferences.values())), dict):
            # Categorized
            for category, category_prefs in preferences.items():
                for key, value in category_prefs.items():
                    lines.append(f"- {category}.{key}: {value}")
        else:
            # Flat
            for key, value in preferences.items():
                lines.append(f"- {key}: {value}")

        if not lines:
            return ""

        return "\n" + "\n".join(lines)

    def get_preference(self, category: str, key: str) -> Optional[Any]:
        """
        Quick helper to get a specific preference.

        Args:
            category: Preference category
            key: Preference key

        Returns:
            Preference value or None
        """
        return self.pref_manager.get_preference(category, key)
