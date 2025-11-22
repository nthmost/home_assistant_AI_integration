#!/usr/bin/env python3
"""
Demo script to test Minnie power phrases.
"""

import json
import re
from pathlib import Path


def load_power_phrases(filepath: Path = None) -> dict:
    """Load power phrases from JSON file."""
    if filepath is None:
        filepath = Path(__file__).parent / "power_phrases.json"

    phrases = {}
    with open(filepath) as f:
        data = json.load(f)

    for category, patterns in data.items():
        for pattern, response in patterns.items():
            # Convert pipe-separated pattern to regex with word boundaries
            regex = r"\b(" + pattern + r")\b"
            phrases[regex] = response

    return phrases


def check_power_phrases(text: str, power_phrases: dict) -> str:
    """Check if text matches a power phrase."""
    text_lower = text.lower()

    for pattern, response in power_phrases.items():
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            return response
    return None


def main():
    print("\n" + "="*60)
    print("  Testing Minnie Power Phrases")
    print("="*60 + "\n")

    power_phrases = load_power_phrases()

    # Test cases
    test_phrases = [
        "Who's fault is it?",
        "Whose fault is this?",
        "Who is to blame?",
        "Who did this?",
        "Who's to blame for this mess?",
        "Who made this mess?",
        "Was it Minnie?",
        "Is it Minnie's fault?",
        "Did Minnie do this?",
        "I think it was Minnie's fault",
        "What happened here?",
        "Who broke this?",
        "Blame Minnie!",
        "Is this Minnie?",
    ]

    print("Test queries:\n")
    for query in test_phrases:
        response = check_power_phrases(query, power_phrases)
        if response:
            print(f"✅ \"{query}\"")
            print(f"   → {response}\n")
        else:
            print(f"❌ \"{query}\"")
            print(f"   → No match\n")


if __name__ == "__main__":
    main()
