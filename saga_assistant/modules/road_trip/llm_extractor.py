"""
LLM-based intent extraction for road trip queries.

Instead of complex regex patterns, use a small LLM to semantically parse queries.
This handles transcription errors, natural language variations, and ambiguity.
"""

import logging
import json
import re
from typing import Dict, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMIntentExtractor:
    """Use LLM to extract structured intent from natural language queries."""

    def __init__(self, model: str = "qwen2.5:1.5b", base_url: str = "http://loki.local:11434/v1"):
        """
        Initialize LLM extractor.

        Args:
            model: Model to use (default: fast 1.5B model)
            base_url: Ollama API endpoint
        """
        self.client = OpenAI(base_url=base_url, api_key="ollama")
        self.model = model

    def extract_road_trip_intent(self, query: str) -> Dict[str, any]:
        """
        Extract structured intent from a road trip query.

        Args:
            query: User's natural language query

        Returns:
            Dict with:
                - action: "distance", "time", "best_time", "poi", or "unknown"
                - destination: Extracted destination name (or None)
                - departure_time: Extracted time constraint (or None)
                - confidence: 0.0-1.0 confidence score

        Example:
            >>> extract_road_trip_intent("What's the distance to Big Sur from here?")
            {'action': 'distance', 'destination': 'Big Sur', 'departure_time': None, 'confidence': 0.95}

            >>> extract_road_trip_intent("time to pick sir")  # Transcription error
            {'action': 'time', 'destination': 'Big Sur', 'departure_time': None, 'confidence': 0.70}
        """
        # System prompt for structured extraction
        system_prompt = """You are a precise intent extraction system for road trip queries.

Extract the following from the user's query:
1. action: What they want to know
   - "distance": How far is it?
   - "time": How long will it take?
   - "best_time": When should I leave?
   - "poi": What's interesting along the way?
   - "unknown": Can't determine

2. destination: Where they're going (just the place name, no extra words)
   - Remove words like "from", "here", "there"
   - Handle transcription errors (e.g., "pick sir" → "Big Sur")
   - If unclear, use your best guess

3. departure_time: When they're leaving (if mentioned)
   - "now", "tomorrow", "5pm", etc.
   - null if not mentioned

4. confidence: How confident you are (0.0-1.0)
   - 1.0 = very clear
   - 0.5 = ambiguous but guessable
   - 0.0 = completely unclear

Respond ONLY with valid JSON. No explanation, no markdown.

Examples:
Query: "What's the distance to Big Sur from here?"
{"action": "distance", "destination": "Big Sur", "departure_time": null, "confidence": 0.95}

Query: "time to pick sir"
{"action": "time", "destination": "Big Sur", "departure_time": null, "confidence": 0.60}

Query: "best time to leave for Lake Tahoe tomorrow"
{"action": "best_time", "destination": "Lake Tahoe", "departure_time": "tomorrow", "confidence": 0.95}

Query: "Let's the drive time to Big Sur"
{"action": "time", "destination": "Big Sur", "departure_time": null, "confidence": 0.85}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Query: {query}"}
                ],
                temperature=0.1,  # Low temp for consistent extraction
                max_tokens=100,
            )

            result_text = response.choices[0].message.content.strip()

            # Parse JSON response
            # Sometimes models wrap in markdown code blocks
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)

            result = json.loads(result_text)

            # Validate and normalize
            if 'action' not in result:
                result['action'] = 'unknown'
            if 'destination' not in result:
                result['destination'] = None
            if 'departure_time' not in result:
                result['departure_time'] = None
            if 'confidence' not in result:
                result['confidence'] = 0.5

            logger.info(f"LLM extracted: {result}")
            return result

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            logger.warning(f"Response was: {result_text}")
            return {
                'action': 'unknown',
                'destination': None,
                'departure_time': None,
                'confidence': 0.0
            }
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}", exc_info=True)
            return {
                'action': 'unknown',
                'destination': None,
                'departure_time': None,
                'confidence': 0.0
            }


def disambiguate_destination(query: str, failed_destination: str, suggestions: list) -> Optional[str]:
    """
    Use LLM to disambiguate when geocoding fails.

    Args:
        query: Original user query
        failed_destination: The destination that failed to geocode
        suggestions: List of potential matches from geocoding service

    Returns:
        Best match from suggestions, or None

    Example:
        >>> disambiguate_destination(
        ...     "What's the drive time to Big Sur?",
        ...     "big sur",
        ...     ["Big Sur Drive, Utah", "Big Sur, California", "Big Sur River, CA"]
        ... )
        "Big Sur, California"
    """
    extractor = LLMIntentExtractor()

    prompt = f"""User asked: "{query}"

We tried to find "{failed_destination}" but got multiple results:
{chr(10).join(f"{i+1}. {s}" for i, s in enumerate(suggestions))}

Which is most likely what they meant? Respond with ONLY the number (1-{len(suggestions)}).
No explanation."""

    try:
        response = extractor.client.chat.completions.create(
            model=extractor.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=5,
        )

        result = response.choices[0].message.content.strip()
        # Extract number
        match = re.search(r'\d+', result)
        if match:
            idx = int(match.group(0)) - 1
            if 0 <= idx < len(suggestions):
                return suggestions[idx]

    except Exception as e:
        logger.warning(f"Disambiguation failed: {e}")

    return None
