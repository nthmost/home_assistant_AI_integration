"""Intent parser for natural language Home Assistant commands.

Converts natural language like "turn on the lights" into
Home Assistant service calls.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from saga_assistant.ha_client import HomeAssistantClient
from saga_assistant.modules.road_trip import RoadTripHandler
from saga_assistant.modules.road_trip.routing import Location, GeocodingError, RoutingError
from saga_assistant.modules.road_trip.llm_extractor import LLMIntentExtractor

logger = logging.getLogger(__name__)


@dataclass
class Intent:
    """Parsed intent from natural language."""
    action: str  # "turn_on", "turn_off", "toggle", "status", "save_parking", etc.
    entity_type: Optional[str] = None  # "light", "switch", etc.
    entity_name: Optional[str] = None  # "tv", "aqua", etc.
    entity_id: Optional[str] = None  # Full entity_id if resolved
    confidence: float = 0.0  # 0.0-1.0 confidence score
    data: Optional[Dict[str, Any]] = None  # Extra data (e.g., parking location)
    quick_mode: bool = False  # Quick response mode (brief answers only)


class IntentParseError(Exception):
    """Failed to parse intent from natural language."""
    pass


class IntentParser:
    """Parse natural language commands into Home Assistant intents."""

    # Action patterns
    ACTION_PATTERNS = {
        # Memory management (check FIRST - user wants to save/forget things)
        "save_preference": [
            r"\b(in general |generally )?i (prefer|like|want)\b",
            r"\bmy default .+ (is|should be)\b",
            r"\bi have a preference for\b",
            r"\b(prefer|like) .+ for (my|the)\b",
        ],
        "remember_fact": [
            r"\b(remember that|keep in mind that|for future reference|don't forget)\b",
        ],
        "forget_memory": [
            r"\b(forget (?:about )?|clear (?:my )?memory|reset (?:your )?memory)\b",
        ],
        "show_preferences": [
            r"\b(what (?:do you know about my |are my )?preferences|show (?:my )?preferences)\b",
        ],
        "show_memory": [
            r"\b(what do you (remember|know) about me|what facts do you know)\b",
        ],
        # Minnie blame (check EARLY before other actions)
        "minnie_blame": [
            r"\b(who'?s fault|whose fault|who is to blame|who did this|who'?s to blame|who made this mess|what happened|who broke|who kicked|why is there|who was yodeling|who'?s running|who should we blame|who do we blame)\b",
            r"\b(was it minnie|is it minnie|did minnie|is this minnie|blame minnie)\b",
            r"\b(what did minnie do|what did many do)\b",  # "many" is common STT error for "Minnie"
            r"\b(minnie'?s fault)\b",
        ],
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
            r"\b(status|state|is|are)\b.*\b(on|off|open|closed)\b",
            r"\b(check|what'?s|what is)\b.*(light|switch|fan|lock|cover|device|status|temperature|humidity)",
        ],
        "brightness": [
            r"\b(brightness|dim|brighten)\b",
            r"\b(set|make).*(brighter|dimmer|darker)\b",
        ],
        # Parking actions (order matters!)
        # Check specific patterns BEFORE general ones to avoid false matches
        "where_parked": [
            r"\b(where (did i park|is my car|is the car|did i leave|is my vehicle|did i move my car))\b",
            r"\b(where'?s my car|where am i parked)\b",
            r"\b(remind me where|tell me where).+(parked|car)\b",
        ],
        "forget_parking": [
            # Must come BEFORE save_parking (contains "parked" which would match save_parking)
            r"\b(forget where i parked|forget my (car|parking))\b",
            r"\b(clear (my )?(parking|car location))\b",
            r"\b(delete (my )?(parking|car) (location|spot))\b",
            r"\b(i moved (my|the) car)\b",
            r"\b(reset parking)\b",
        ],
        "save_parking": [
            r"\b(i parked|my car is|car is parked|i'm parked|i just parked)\b",
            r"\b(i left (my|the) car)\b",
        ],
        "when_to_move": [
            r"\b(when (do i need to |should i |do i have to )?move (my car|the car|my vehicle))\b",
            r"\b(do i need to move)\b",
            r"\b(street sweeping|when is street sweeping|is there street sweeping)\b",
            r"\b(when (is|do i have) street cleaning)\b",
            r"\b(any (street sweeping|parking restrictions))\b",
        ],
        # Road trip planning (distance, time, routes)
        "road_trip_distance": [
            r"\b(how far|how many miles|what'?s the distance|distance to)\b.*(to|is it to)\b",
            r"\b(miles to|kilometers to)\b",
        ],
        "road_trip_time": [
            r"\b(how long|drive time|travel time)\b",
            r"\btime to\b",  # Broad match - let LLM figure out the rest
            r"\b(how long (will it take|does it take|is the drive))\b",
            r"\b(what'?s|what is) the drive time\b",
            r"\b(let'?s|lets) .{0,10}(drive time|travel time)\b",
        ],
        "road_trip_best_time": [
            r"\b(when should i leave|best time to leave|when (to|should i) depart)\b",
            r"\b(what time should i leave|optimal (time|departure))\b",
        ],
        "road_trip_poi": [
            r"\b(landmarks|points of interest|things to see|places to stop|stops)\b.*(between|along|on the way)\b",
            r"\b(what (can i see|is there to see)|interesting (places|spots|locations))\b.*(between|along|to)\b",
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

    def __init__(self, ha_client: Optional[HomeAssistantClient]):
        """Initialize the intent parser.

        Args:
            ha_client: Home Assistant client for entity lookup (None if HA unavailable)
        """
        self.ha_client = ha_client
        self._entity_cache = None

        # Lazy init parking manager
        self._parking_manager = None

        # Lazy init Minnie model
        self._minnie_model = None

        # Lazy init memory system
        self._memory_db = None
        self._preference_manager = None

        # Initialize road trip handler
        self._road_trip_handler = self._init_road_trip_handler()

        # Initialize LLM extractor for road trip queries
        self._llm_extractor = None  # Lazy init

    def _init_road_trip_handler(self) -> RoadTripHandler:
        """Initialize the road trip handler.

        Returns:
            RoadTripHandler instance
        """
        # Get HA config if available
        if self.ha_client:
            # TODO: Get actual lat/lon from HA config
            ha_config = {
                'latitude': 37.7749,
                'longitude': -122.4194,
                'unit_system': {'name': 'imperial'}
            }
            return RoadTripHandler.from_ha_config(ha_config)
        else:
            # Fallback: create handler with default SF location
            home = Location(latitude=37.7749, longitude=-122.4194, address="home")
            return RoadTripHandler(home, unit_system='imperial')

    @property
    def memory_db(self):
        """Lazy-load memory database"""
        if self._memory_db is None:
            from saga_assistant.memory import MemoryDatabase
            self._memory_db = MemoryDatabase()
        return self._memory_db

    @property
    def preference_manager(self):
        """Lazy-load preference manager"""
        if self._preference_manager is None:
            from saga_assistant.memory import PreferenceManager
            self._preference_manager = PreferenceManager(self.memory_db)
        return self._preference_manager

    @property
    def parking_manager(self):
        """Lazy-load parking manager"""
        if self._parking_manager is None:
            from saga_assistant.parking import StreetSweepingLookup, ParkingManager
            lookup = StreetSweepingLookup()
            self._parking_manager = ParkingManager(lookup)
        return self._parking_manager

    @property
    def minnie_model(self):
        """Lazy-load Minnie model"""
        if self._minnie_model is None:
            from saga_assistant.minnie_model import MinnieModel
            self._minnie_model = MinnieModel()
        return self._minnie_model

    @property
    def llm_extractor(self):
        """Lazy-load LLM extractor for road trip queries"""
        if self._llm_extractor is None:
            self._llm_extractor = LLMIntentExtractor()
        return self._llm_extractor

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

        # Check for "quick question" power phrase
        quick_mode = False
        if text.startswith("quick question"):
            quick_mode = True
            # Remove the phrase and any trailing punctuation/whitespace
            text = text.replace("quick question", "", 1).strip()
            # Strip leading punctuation (period, comma, dash, etc.)
            text = text.lstrip('.,;:!?- ').strip()
            logger.debug(f"Quick mode enabled, parsing: {text}")

        # Parse action
        action = self._parse_action(text)
        if not action:
            raise IntentParseError(f"Could not determine action from: {text}")

        # Handle Minnie blame queries specially
        if action == "minnie_blame":
            return Intent(
                action="minnie_blame",
                confidence=1.0,  # Always high confidence for Minnie!
                data={"question": text},
                quick_mode=quick_mode
            )

        # Handle memory actions specially
        if action in ["save_preference", "remember_fact", "forget_memory",
                      "show_preferences", "show_memory"]:
            return self._parse_memory_intent(action, text)

        # Handle parking actions specially
        if action in ["save_parking", "where_parked", "when_to_move"]:
            return self._parse_parking_intent(action, text)

        # Handle road trip actions specially
        if action in ["road_trip_distance", "road_trip_time", "road_trip_best_time", "road_trip_poi"]:
            return self._parse_road_trip_intent(action, text, quick_mode)

        # Parse entity type and name for HA actions
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
            f"name={entity_name}, id={entity_id}, confidence={confidence:.2f}, "
            f"quick_mode={quick_mode}"
        )

        return Intent(
            action=action,
            entity_type=entity_type,
            entity_name=entity_name,
            entity_id=entity_id,
            confidence=confidence,
            quick_mode=quick_mode,
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
        # Can't resolve entities without HA client
        if not self.ha_client:
            return None, 0.0

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

    def _parse_memory_intent(self, action: str, text: str) -> Intent:
        """Parse memory-specific intents.

        Args:
            action: Memory action (save_preference, remember_fact, etc.)
            text: Original text

        Returns:
            Memory Intent
        """
        data = {"original_text": text}
        confidence = 0.9  # High confidence for memory actions

        if action == "save_preference":
            # Extract preference details
            # Pattern: "I prefer X" or "I like Y for Z"
            preference_patterns = [
                r"(?:in general |generally )?i (?:prefer|like|want)\s+(.+)",
                r"my default (.+?) (?:is|should be)\s+(.+)",
                r"i have a preference for\s+(.+)",
            ]

            for pattern in preference_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data['preference_text'] = match.group(1).strip()
                    break

        elif action == "remember_fact":
            # Extract fact
            fact_patterns = [
                r"(?:remember that|keep in mind that|for future reference,?|don't forget)\s+(.+)",
            ]

            for pattern in fact_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data['fact_text'] = match.group(1).strip()
                    break

        logger.info(f"Parsed memory intent: action={action}, data={data}")

        return Intent(
            action=action,
            confidence=confidence,
            data=data,
            quick_mode=False  # Memory actions don't support quick mode
        )

    def _parse_parking_intent(self, action: str, text: str) -> Intent:
        """Parse parking-specific intents

        Args:
            action: Parking action (save_parking, where_parked, when_to_move)
            text: Original text

        Returns:
            Parking Intent
        """
        data = {}
        confidence = 0.9  # High confidence for parking actions

        if action == "save_parking":
            # Extract location from text
            # Look for patterns like "I parked on X" or "my car is at Y"
            location_patterns = [
                r"(?:i parked|my car is|car is parked|i'?m parked|parked)\s+(?:on |at |in )?(?:the )?(.+)",
            ]

            location_text = None
            for pattern in location_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    location_text = match.group(1).strip()
                    break

            if location_text:
                data['location_text'] = location_text
                logger.info(f"Parsed parking location: {location_text}")
            else:
                confidence = 0.4
                logger.warning(f"Could not extract location from: {text}")

        logger.info(f"Parsed parking intent: action={action}, confidence={confidence:.2f}")

        return Intent(
            action=action,
            confidence=confidence,
            data=data,
            quick_mode=False  # Parking actions don't support quick mode yet
        )

    def _parse_road_trip_intent(self, action: str, text: str, quick_mode: bool) -> Intent:
        """Parse road trip planning intents using LLM extraction.

        Args:
            action: Road trip action (road_trip_distance, road_trip_time, etc.)
            text: Original text
            quick_mode: Whether quick mode is enabled

        Returns:
            Road trip Intent
        """
        # Use LLM to extract structured intent
        llm_result = self.llm_extractor.extract_road_trip_intent(text)

        data = {"query": text}

        # Map LLM action to our action types (validate LLM output)
        action_mapping = {
            'distance': 'road_trip_distance',
            'time': 'road_trip_time',
            'best_time': 'road_trip_best_time',
            'poi': 'road_trip_poi',
        }

        # If LLM action matches our detected action, use it
        # Otherwise trust the regex-based broad detection
        llm_action = action_mapping.get(llm_result.get('action'))
        if llm_action == action:
            # LLM agrees with broad detection
            confidence = llm_result.get('confidence', 0.9)
        else:
            # LLM disagrees, but we still use its extraction
            # Trust the broad detection more for action type
            confidence = 0.7
            logger.info(f"LLM action '{llm_result.get('action')}' differs from detected '{action}'")

        # Always use LLM's destination and time extraction
        if llm_result.get('destination'):
            data['destination'] = llm_result['destination']
            logger.info(f"LLM extracted destination: {llm_result['destination']}")
        else:
            confidence = min(confidence, 0.5)
            logger.warning(f"LLM could not extract destination from: {text}")

        if llm_result.get('departure_time'):
            data['departure_time'] = llm_result['departure_time']

        logger.info(f"Parsed road trip intent: action={action}, quick_mode={quick_mode}, confidence={confidence:.2f}")

        return Intent(
            action=action,
            confidence=confidence,
            data=data,
            quick_mode=quick_mode
        )

    def _execute_road_trip_intent(self, intent: Intent) -> Dict[str, Any]:
        """Execute a road trip planning intent.

        Args:
            intent: Road trip intent to execute

        Returns:
            Result dictionary with status and message
        """
        # Use LLM-extracted destination directly instead of synthetic query
        # This avoids handler re-parsing and breaking the clean extraction
        destination = intent.data.get('destination')
        original_query = intent.data.get('query', '')

        try:
            # Call handler with LLM-extracted data directly
            response = self._road_trip_handler.handle_query_with_destination(
                destination=destination,
                action_type=intent.action,
                quick_mode=intent.quick_mode,
                original_query=original_query
            )
            return {
                "status": "success",
                "message": response
            }
        except GeocodingError as e:
            logger.warning(f"Geocoding failed for road trip query: {e}")
            return {
                "status": "error",
                "message": "I couldn't find that location. Could you be more specific?"
            }
        except RoutingError as e:
            logger.warning(f"Routing failed for road trip query: {e}")
            return {
                "status": "error",
                "message": "I couldn't calculate a route to that location."
            }
        except ValueError as e:
            logger.warning(f"Invalid road trip query: {e}")
            return {
                "status": "error",
                "message": f"Sorry, I couldn't understand that query: {str(e)}"
            }

    def execute(self, intent: Intent) -> Dict[str, Any]:
        """Execute an intent.

        Args:
            intent: Parsed intent

        Returns:
            Result dictionary with status and message

        Raises:
            IntentParseError: If intent cannot be executed
        """
        # Handle Minnie blame queries
        if intent.action == "minnie_blame":
            question = intent.data.get("question", "Whose fault is it?")
            response = self.minnie_model.blame_minnie(question)
            return {
                "status": "success",
                "message": response
            }

        # Handle memory actions
        if intent.action == "save_preference":
            # For now, store the raw text - we'll enhance with LLM later
            preference_text = intent.data.get('preference_text', intent.data.get('original_text'))

            # Simple categorization for MVP
            # TODO: Use LLM to extract category/key/value
            self.preference_manager.save_preference(
                category="general",
                preference_key="preference",
                preference_value=preference_text
            )

            return {
                "status": "success",
                "message": "Got it. I'll remember that preference."
            }

        elif intent.action == "remember_fact":
            fact_text = intent.data.get('fact_text', intent.data.get('original_text'))

            # Store in facts table (will implement in Phase 2)
            # For now, just acknowledge
            logger.info(f"Would remember fact: {fact_text}")

            return {
                "status": "success",
                "message": "I'll remember that."
            }

        elif intent.action == "show_preferences":
            formatted_prefs = self.preference_manager.format_for_display()

            return {
                "status": "success",
                "message": f"Here are your preferences: {formatted_prefs}"
            }

        elif intent.action == "show_memory":
            stats = self.memory_db.get_stats()
            msg = f"I remember {stats['preferences']} preferences"
            if stats['facts'] > 0:
                msg += f" and {stats['facts']} facts"

            return {
                "status": "success",
                "message": msg
            }

        elif intent.action == "forget_memory":
            # This should trigger confirmation in the assistant
            return {
                "status": "needs_confirmation",
                "confirmation_type": "clear_memory",
                "message": "This will delete all your preferences and facts. Are you sure?"
            }

        # Handle road trip actions
        if intent.action in ["road_trip_distance", "road_trip_time", "road_trip_best_time", "road_trip_poi"]:
            return self._execute_road_trip_intent(intent)

        # Handle parking actions
        if intent.action == "save_parking":
            location_text = intent.data.get('location_text')
            if not location_text:
                return {
                    "status": "error",
                    "message": "I didn't understand where you parked. Try saying 'I parked on Valencia between 18th and 19th'"
                }

            # Parse location
            location = self.parking_manager.parser.parse(location_text)
            if not location:
                return {
                    "status": "error",
                    "message": f"I couldn't find that street. Could you say it again?"
                }

            # Check for missing side information (critical for accurate schedule)
            if location.side == "Unknown":
                # Get valid sides for this street/block
                valid_sides = self.parking_manager.lookup.get_valid_sides(
                    location.street,
                    location.block_limits
                )

                # Build question based on valid sides
                if len(valid_sides) == 2:
                    sides_str = f"{valid_sides[0].lower()} or {valid_sides[1].lower()}"
                elif len(valid_sides) > 2:
                    sides_str = ", ".join([s.lower() for s in valid_sides[:-1]]) + f", or {valid_sides[-1].lower()}"
                else:
                    # Fallback to all four if we can't determine
                    sides_str = "north, south, east, or west"

                return {
                    "status": "needs_followup",
                    "followup_type": "parking_side",
                    "partial_data": {"location": location, "valid_sides": valid_sides},
                    "message": f"Which side of the street - {sides_str}?"
                }

            # Save location
            self.parking_manager.save_parking_location(location)

            # Expand abbreviations for TTS
            from saga_assistant.parking import expand_street_abbreviations
            street_spoken = expand_street_abbreviations(location.street)

            return {
                "status": "success",
                "message": f"Got it. You're parked on {street_spoken}. I'll remind you about street sweeping."
            }

        elif intent.action == "where_parked":
            # Check if we have parking location saved
            state = self.parking_manager.load_parking_state()
            if not state:
                return {
                    "status": "needs_followup",
                    "followup_type": "no_parking_saved",
                    "message": "I don't know where you parked. Where is your car?"
                }

            # Check if we have critical information (side)
            location_data = state.get('location', {})
            if location_data.get('side') == "Unknown":
                # Get valid sides for this street/block
                valid_sides = self.parking_manager.lookup.get_valid_sides(
                    location_data.get('street'),
                    location_data.get('block_limits')
                )

                # Build question based on valid sides
                if len(valid_sides) == 2:
                    sides_str = f"{valid_sides[0].lower()} or {valid_sides[1].lower()}"
                elif len(valid_sides) > 2:
                    sides_str = ", ".join([s.lower() for s in valid_sides[:-1]]) + f", or {valid_sides[-1].lower()}"
                else:
                    sides_str = "north, south, east, or west"

                return {
                    "status": "needs_followup",
                    "followup_type": "parking_side",
                    "partial_data": {"location": location_data, "valid_sides": valid_sides},
                    "message": f"I know you're parked, but which side - {sides_str}?"
                }

            status = self.parking_manager.get_human_readable_status(expand_abbreviations=True)
            return {
                "status": "success",
                "message": status
            }

        elif intent.action == "forget_parking":
            # Clear saved parking location
            state = self.parking_manager.load_parking_state()
            if not state:
                return {
                    "status": "success",
                    "message": "I don't have any parking location saved."
                }

            # Delete the state file
            self.parking_manager.state_file.unlink(missing_ok=True)

            return {
                "status": "success",
                "message": "Okay, I've forgotten where you parked."
            }

        elif intent.action == "when_to_move":
            # Check if we have parking location saved
            state = self.parking_manager.load_parking_state()
            if not state:
                return {
                    "status": "needs_followup",
                    "followup_type": "no_parking_saved",
                    "message": "I don't know where you parked. Tell me where your car is first."
                }

            # Check if we have critical information (side) BEFORE looking up schedule
            location_data = state.get('location', {})
            if location_data.get('side') == "Unknown":
                # Get valid sides for this street/block
                valid_sides = self.parking_manager.lookup.get_valid_sides(
                    location_data.get('street'),
                    location_data.get('block_limits')
                )

                # Build question based on valid sides
                if len(valid_sides) == 2:
                    sides_str = f"{valid_sides[0].lower()} or {valid_sides[1].lower()}"
                elif len(valid_sides) > 2:
                    sides_str = ", ".join([s.lower() for s in valid_sides[:-1]]) + f", or {valid_sides[-1].lower()}"
                else:
                    sides_str = "north, south, east, or west"

                return {
                    "status": "needs_followup",
                    "followup_type": "parking_side_for_schedule",
                    "partial_data": {"location": location_data, "valid_sides": valid_sides},
                    "message": f"I need to know which side you're parked on - {sides_str}?"
                }

            next_sweep = self.parking_manager.get_next_sweeping(days_ahead=14)
            if not next_sweep:
                return {
                    "status": "success",
                    "message": "No street sweeping scheduled in the next 2 weeks."
                }

            schedule = next_sweep['schedule']
            start_time = next_sweep['start_time']
            from datetime import datetime
            delta = start_time - datetime.now()

            if delta.days == 0:
                when = "today"
            elif delta.days == 1:
                when = "tomorrow"
            else:
                # Use ordinal for day (December 2nd, not December 2)
                from saga_assistant.parking import ordinal
                when = start_time.strftime('%A, %B ') + ordinal(start_time.day)

            from_hour = schedule.fromhour % 12 or 12
            from_period = 'AM' if schedule.fromhour < 12 else 'PM'
            to_hour = schedule.tohour % 12 or 12
            to_period = 'AM' if schedule.tohour < 12 else 'PM'

            message = f"Street sweeping is {when} from {from_hour} {from_period} to {to_hour} {from_period}."

            if delta.total_seconds() / 3600 < 24:
                message += " Make sure to move your car!"

            return {
                "status": "success",
                "message": message
            }

        # Handle Home Assistant actions
        if not intent.entity_id:
            raise IntentParseError(
                f"Cannot execute intent: no entity found for "
                f"type={intent.entity_type} name={intent.entity_name}"
            )

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

    def handle_followup(self, followup_type: str, answer_text: str, partial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a follow-up answer to complete a previous intent.

        Args:
            followup_type: Type of follow-up (e.g., "parking_side")
            answer_text: User's answer text
            partial_data: Partial data from previous interaction

        Returns:
            Result dictionary
        """
        # Parse side from answer (common to multiple follow-up types)
        def parse_side(text: str) -> Optional[str]:
            text_lower = text.lower().strip()
            if "north" in text_lower:
                return "North"
            elif "south" in text_lower:
                return "South"
            elif "east" in text_lower:
                return "East"
            elif "west" in text_lower:
                return "West"
            return None

        if followup_type == "parking_side":
            # Initial save - user just told us where they parked, missing side
            side = parse_side(answer_text)
            if not side:
                return {
                    "status": "error",
                    "message": "I didn't catch that. Is it north, south, east, or west?"
                }

            # Update location with side
            from saga_assistant.parking import ParkingLocation
            location_dict = partial_data["location"]
            location = ParkingLocation(**location_dict) if isinstance(location_dict, dict) else location_dict
            location.side = side

            # Now save the complete location
            self.parking_manager.save_parking_location(location)

            # Expand abbreviations for TTS
            from saga_assistant.parking import expand_street_abbreviations
            street_spoken = expand_street_abbreviations(location.street)

            return {
                "status": "success",
                "message": f"Got it. You're parked on {street_spoken}. I'll remind you about street sweeping."
            }

        elif followup_type == "parking_side_for_schedule":
            # User asked "when do I move?" but we had incomplete info
            side = parse_side(answer_text)
            if not side:
                return {
                    "status": "error",
                    "message": "I didn't catch that. Is it north, south, east, or west?"
                }

            # Load current state, update side, re-save
            state = self.parking_manager.load_parking_state()
            if not state:
                return {
                    "status": "error",
                    "message": "I lost track of where you parked. Could you tell me again?"
                }

            # Update location in state
            from saga_assistant.parking import ParkingLocation
            location_dict = state['location']
            location = ParkingLocation(**location_dict)
            location.side = side

            # Re-save with updated side
            self.parking_manager.save_parking_location(location)

            # Now answer the original question: when do I move?
            next_sweep = self.parking_manager.get_next_sweeping(days_ahead=14)
            if not next_sweep:
                return {
                    "status": "success",
                    "message": "No street sweeping scheduled in the next 2 weeks."
                }

            schedule = next_sweep['schedule']
            start_time = next_sweep['start_time']
            from datetime import datetime
            from saga_assistant.parking import ordinal
            delta = start_time - datetime.now()

            if delta.days == 0:
                when = "today"
            elif delta.days == 1:
                when = "tomorrow"
            else:
                when = start_time.strftime('%A, %B ') + ordinal(start_time.day)

            from_hour = schedule.fromhour % 12 or 12
            from_period = 'AM' if schedule.fromhour < 12 else 'PM'
            to_hour = schedule.tohour % 12 or 12
            to_period = 'AM' if schedule.tohour < 12 else 'PM'

            message = f"Street sweeping is {when} from {from_hour} {from_period} to {to_hour} {from_period}."

            if delta.total_seconds() / 3600 < 24:
                message += " Make sure to move your car!"

            return {
                "status": "success",
                "message": message
            }

        elif followup_type == "no_parking_saved":
            # User asked about parking but never told us where they parked
            # Try to parse their answer as a new parking location
            location_text = answer_text.strip()

            location = self.parking_manager.parser.parse(location_text)
            if not location:
                return {
                    "status": "error",
                    "message": "I couldn't find that street. Could you say it again?"
                }

            # Check if we got side info this time
            if location.side == "Unknown":
                return {
                    "status": "needs_followup",
                    "followup_type": "parking_side",
                    "partial_data": {"location": location},
                    "message": "Which side of the street - north, south, east, or west?"
                }

            # Save complete location
            self.parking_manager.save_parking_location(location)

            from saga_assistant.parking import expand_street_abbreviations
            street_spoken = expand_street_abbreviations(location.street)

            return {
                "status": "success",
                "message": f"Got it. You're parked on {street_spoken}. I'll remind you about street sweeping."
            }

        else:
            return {
                "status": "error",
                "message": "I lost track of what we were talking about. Could you start over?"
            }

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
