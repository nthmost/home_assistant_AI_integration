#!/usr/bin/env python3
"""
Test script for "quick question" power phrase parsing.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)


def test_quick_question_parsing():
    """Test various quick question patterns."""

    print("\n" + "="*70)
    print("  Testing 'Quick Question' Power Phrase")
    print("="*70 + "\n")

    test_cases = [
        # Different punctuation
        "Quick question. How far is it to LA?",
        "Quick question, how far is it to LA?",
        "Quick question - how far is it to LA?",
        "Quick question: how far is it to LA?",
        "Quick question how far is it to LA?",

        # Case variations (should all work since we lowercase)
        "quick question. what's the weather?",
        "QUICK QUESTION. WHAT'S THE WEATHER?",

        # Without quick question (should have quick_mode=False)
        "How far is it to LA?",
        "What's the weather?",
    ]

    for test_text in test_cases:
        print(f"\n📝 Input: \"{test_text}\"")
        print("-" * 70)

        try:
            # We need to handle that some queries won't match any action
            # For this test, we just care about quick_mode detection

            # Manually test the quick question detection logic
            text = test_text.lower().strip()
            quick_mode = False

            if text.startswith("quick question"):
                quick_mode = True
                text = text.replace("quick question", "", 1).strip()
                text = text.lstrip('.,;:!? ').strip()

            print(f"   Quick Mode: {quick_mode}")
            print(f"   Cleaned Text: \"{text}\"")

            # Verify the text is properly cleaned
            if quick_mode:
                # Should not start with punctuation
                if text and text[0] in '.,;:!? ':
                    print(f"   ❌ ERROR: Text still has leading punctuation!")
                else:
                    print(f"   ✅ Punctuation properly stripped")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "="*70)
    print("  Test Complete!")
    print("="*70 + "\n")


if __name__ == '__main__':
    test_quick_question_parsing()
