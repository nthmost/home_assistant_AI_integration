"""Intent parser for natural language Home Assistant commands.

Converts natural language like "turn on the lights" into
Home Assistant service calls.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from saga_assistant.ha_client import HomeAssistantClient

logger = logging.getLogger(__name__)


@dataclass
class Intent:
    """Parsed intent from natural language."""
    action: str  # "turn_on", "turn_off", "toggle", "status"
    entity_type: Optional[str] = None  # "light", "switch", etc.
    entity_name: Optional[str] = None  # "tv", "aqua", etc.
    entity_id: Optional[str] = None  # Full entity_id if resolved
    confidence: float = 0.0  # 0.0-1.0 confidence score


class IntentParseError(Exception):
    """Failed to parse intent from natural language."""
    pass


class IntentParser:
    """Parse natural language commands into Home Assistant intents."""

    # Action patterns
    ACTION_PATTERNS = {
        "turn_on": [
            r"\b(turn on|switch on|enable|activate)\b",
            r"\b(open)\b",  # For covers/blinds
        ],
        "turn_off": [
            r"\b(turn off|switch off|disable|deactivate|shut off)\b",
            r"\b(close)\b",  # For covers/blinds
        ],
        "toggle": [
            r"\b(toggle|flip|switch)\b",
        ],
        "status": [
            r"\b(status|state|is|are)\b.*\b(on|off)\b",
            r"\b(check|what'?s|what is)\b",
        ],
        "brightness": [
            r"\b(brightness|dim|brighten)\b",
            r"\b(set|make).*(brighter|dimmer|darker)\b",
        ],
    }

    # Entity type patterns
    ENTITY_PATTERNS = {
        "light": [r"\blight[s]?\b", r"\blamp[s]?\b", r"\bbulb[s]?\b"],
        "switch": [r"\bswitch(es)?\b", r"\boutlet[s]?\b", r"\bplug[s]?\b"],
        "cover": [r"\bblind[s]?\b", r"\bshade[s]?\b", r"\bcurtain[s]?\b"],
        "fan": [r"\bfan[s]?\b"],
        "lock": [r"\block[s]?\b"],
    }

    # Common entity name patterns (specific to your setup)
    DEVICE_ALIASES = {
        "tv": ["tv", "television"],
        "aqua": ["aqua", "aquarium", "fish"],
        "strip": ["strip", "power strip"],
        "candelabra": ["candelabra", "candle"],
        "tube": ["tube", "tube lamp"],
    }

    def __init__(self, ha_client: HomeAssistantClient):
        """Initialize the intent parser.

        Args:
            ha_client: Home Assistant client for entity lookup
        """
        self.ha_client = ha_client
        self._entity_cache = None

    def parse(self, text: str) -> Intent:
        """Parse natural language text into an intent.

        Args:
            text: Natural language command

        Returns:
            Parsed Intent object

        Raises:
            IntentParseError: If intent cannot be parsed
        """
        text = text.lower().strip()
        logger.debug(f"Parsing: {text}")

        # Parse action
        action = self._parse_action(text)
        if not action:
            raise IntentParseError(f"Could not determine action from: {text}")

        # Parse entity type and name
        entity_type = self._parse_entity_type(text)
        entity_name = self._parse_entity_name(text)

        # Try to resolve to a specific entity
        entity_id = None
        confidence = 0.5  # Base confidence

        if entity_type or entity_name:
            entity_id, match_confidence = self._resolve_entity(
                entity_type, entity_name, text
            )
            confidence = match_confidence

        logger.info(
            f"Parsed intent: action={action}, type={entity_type}, "
            f"name={entity_name}, id={entity_id}, confidence={confidence:.2f}"
        )

        return Intent(
            action=action,
            entity_type=entity_type,
            entity_name=entity_name,
            entity_id=entity_id,
            confidence=confidence,
        )

    def _parse_action(self, text: str) -> Optional[str]:
        """Parse action from text.

        Args:
            text: Natural language text

        Returns:
            Action name or None
        """
        for action, patterns in self.ACTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return action
        return None

    def _parse_entity_type(self, text: str) -> Optional[str]:
        """Parse entity type from text.

        Args:
            text: Natural language text

        Returns:
            Entity type (domain) or None
        """
        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return entity_type
        return None

    def _parse_entity_name(self, text: str) -> Optional[str]:
        """Parse entity name from text.

        Args:
            text: Natural language text

        Returns:
            Entity name or None
        """
        # Check known device aliases
        for device, aliases in self.DEVICE_ALIASES.items():
            for alias in aliases:
                if re.search(r"\b" + re.escape(alias) + r"\b", text, re.IGNORECASE):
                    return device

        # Extract potential names (words between action and entity type)
        # This is a simple heuristic - could be improved
        words = text.split()
        for word in words:
            if len(word) > 3 and word not in ["turn", "switch", "light", "the"]:
                return word

        return None

    def _resolve_entity(
        self, entity_type: Optional[str], entity_name: Optional[str], text: str
    ) -> Tuple[Optional[str], float]:
        """Resolve entity type and name to a specific entity_id.

        Args:
            entity_type: Entity type (domain)
            entity_name: Entity name or alias
            text: Original text for fallback search

        Returns:
            Tuple of (entity_id, confidence)
        """
        # Get all entities (use cache)
        if self._entity_cache is None:
            self._entity_cache = self.ha_client.get_states()

        # Filter by type if specified
        candidates = self._entity_cache
        confidence = 0.3  # Start with low confidence

        if entity_type:
            candidates = [
                e for e in candidates if e["entity_id"].startswith(f"{entity_type}.")
            ]
            confidence += 0.3

        # Filter by name if specified
        if entity_name:
            # Search in entity_id and friendly_name
            name_matches = []
            for entity in candidates:
                entity_id = entity["entity_id"].lower()
                friendly_name = entity.get("attributes", {}).get("friendly_name", "").lower()

                # Check if entity_name appears in either
                if entity_name in entity_id or entity_name in friendly_name:
                    name_matches.append(entity)

            if name_matches:
                candidates = name_matches
                confidence += 0.4

        # If we have exactly one match, high confidence
        if len(candidates) == 1:
            confidence = 0.95
            return candidates[0]["entity_id"], confidence

        # Multiple matches - try to pick the best one
        if len(candidates) > 1:
            # Prefer devices that are not unavailable
            available = [e for e in candidates if e["state"] != "unavailable"]
            if available:
                candidates = available

            # If still multiple, pick the first one
            # TODO: Could improve this with better ranking
            confidence = 0.6
            return candidates[0]["entity_id"], confidence

        # No matches - try fuzzy search on full text
        search_results = self.ha_client.search_entities(text)
        if search_results:
            # Filter to available entities
            available = [e for e in search_results if e["state"] != "unavailable"]
            if available:
                search_results = available

            confidence = 0.4
            return search_results[0]["entity_id"], confidence

        return None, 0.0

    def execute(self, intent: Intent) -> Dict[str, Any]:
        """Execute an intent.

        Args:
            intent: Parsed intent

        Returns:
            Result dictionary with status and message

        Raises:
            IntentParseError: If intent cannot be executed
        """
        if not intent.entity_id:
            raise IntentParseError(
                f"Cannot execute intent: no entity found for "
                f"type={intent.entity_type} name={intent.entity_name}"
            )

        try:
            if intent.action == "turn_on":
                self.ha_client.turn_on(intent.entity_id)
                return {"status": "success", "message": f"Turned on {intent.entity_id}"}

            elif intent.action == "turn_off":
                self.ha_client.turn_off(intent.entity_id)
                return {"status": "success", "message": f"Turned off {intent.entity_id}"}

            elif intent.action == "toggle":
                self.ha_client.toggle(intent.entity_id)
                return {"status": "success", "message": f"Toggled {intent.entity_id}"}

            elif intent.action == "status":
                state = self.ha_client.get_state(intent.entity_id)
                return {
                    "status": "success",
                    "message": f"{intent.entity_id} is {state['state']}",
                    "state": state,
                }

            else:
                raise IntentParseError(f"Unsupported action: {intent.action}")

        except Exception as e:
            logger.exception(f"Failed to execute intent: {e}")
            raise IntentParseError(f"Failed to execute: {e}")

    def parse_and_execute(self, text: str) -> Dict[str, Any]:
        """Parse and execute a natural language command.

        Args:
            text: Natural language command

        Returns:
            Result dictionary

        Raises:
            IntentParseError: If parsing or execution fails
        """
        intent = self.parse(text)

        if intent.confidence < 0.4:
            logger.warning(f"Low confidence intent: {intent}")
            # Could ask for confirmation here
            raise IntentParseError(
                f"Low confidence in parsing command (confidence={intent.confidence:.2f})"
            )

        return self.execute(intent)


def main():
    """Demo the intent parser."""
    import sys
    from pathlib import Path

    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("\n" + "="*60)
    print("  🧠 Intent Parser Demo")
    print("="*60 + "\n")

    # Initialize
    client = HomeAssistantClient()
    parser = IntentParser(client)

    # Test commands
    test_commands = [
        "turn on the TV light",
        "turn off the aqua lights",
        "toggle the power strip",
        "turn on all the lights",
        "switch off the lamp",
        "what's the status of the TV light",
    ]

    print("Testing commands:\n")
    for cmd in test_commands:
        print(f"📝 '{cmd}'")
        try:
            intent = parser.parse(cmd)
            print(f"   Action:     {intent.action}")
            print(f"   Type:       {intent.entity_type}")
            print(f"   Name:       {intent.entity_name}")
            print(f"   Entity ID:  {intent.entity_id}")
            print(f"   Confidence: {intent.confidence:.2f}")
        except IntentParseError as e:
            print(f"   ❌ Error: {e}")
        print()

    # Interactive mode
    print("\n" + "="*60)
    print("  Interactive Mode (Ctrl+C to exit)")
    print("="*60 + "\n")

    try:
        while True:
            cmd = input("Command: ").strip()
            if not cmd:
                continue

            try:
                result = parser.parse_and_execute(cmd)
                print(f"✅ {result['message']}\n")
            except IntentParseError as e:
                print(f"❌ {e}\n")

    except KeyboardInterrupt:
        print("\n\nBye!\n")


if __name__ == "__main__":
    main()
