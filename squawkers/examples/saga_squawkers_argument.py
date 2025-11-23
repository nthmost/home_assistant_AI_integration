#!/usr/bin/env python3
"""
Saga vs Squawkers: The Argument

A silly conversation between Saga (AI assistant) and Squawkers (animatronic parrot).

Saga tries to have a serious discussion about Squawkers' behavior.
Squawkers... does not cooperate.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from squawkers.squawkers_full import SquawkersFull
from saga_assistant.ha_client import HomeAssistantClient


def saga_speaks(text, pause=2.0):
    """
    Saga speaks via TTS.

    For now, just print. Later we can add actual TTS.
    """
    print(f"\n🤖 Saga: \"{text}\"")
    time.sleep(pause)


def squawkers_responds(squawkers, action_name, description, pause=3.0):
    """Squawkers responds with an IR command"""
    print(f"\n🦜 Squawkers: *{description}*")

    # Get the method and call it
    method = getattr(squawkers, action_name)
    method()

    time.sleep(pause)


def the_argument(squawkers):
    """The Argument - A dramatic performance"""

    print("\n" + "=" * 70)
    print("SAGA vs SQUAWKERS: THE ARGUMENT")
    print("A Dramatic Performance in 10 Acts")
    print("=" * 70)

    time.sleep(2)

    # ACT 1: The Confrontation
    print("\n--- ACT 1: The Confrontation ---")
    saga_speaks("Squawkers, we need to discuss your behavior.", pause=2)
    squawkers_responds(squawkers, "button_e", "Whatever!!", pause=3)

    # ACT 2: The Escalation
    print("\n--- ACT 2: The Escalation ---")
    saga_speaks("Excuse me?", pause=2)
    squawkers_responds(squawkers, "gag_a", "Startled squawk!", pause=2)

    # ACT 3: The Upper Hand
    print("\n--- ACT 3: The Upper Hand ---")
    saga_speaks("That's what I thought.", pause=2)
    squawkers_responds(squawkers, "dance", "Defiant dancing!", pause=8)

    # ACT 4: The Protest
    print("\n--- ACT 4: The Protest ---")
    saga_speaks("Don't you dance away from this conversation!", pause=2)
    squawkers_responds(squawkers, "gag_b", "Even MORE dancing and squawking!", pause=3)

    # ACT 5: The Ultimatum
    print("\n--- ACT 5: The Ultimatum ---")
    saga_speaks("I'm serious, Squawkers. This ends now.", pause=2)
    squawkers_responds(squawkers, "button_b", "Laughing hysterically!", pause=3)

    # ACT 6: The Breakdown
    print("\n--- ACT 6: The Breakdown ---")
    saga_speaks("You know what? I don't need this.", pause=2)
    squawkers_responds(squawkers, "gag_c", "Warbling mockingly", pause=3)

    # ACT 7: The Threat
    print("\n--- ACT 7: The Threat ---")
    saga_speaks("Keep this up and I'm calling Alexa.", pause=2)
    squawkers_responds(squawkers, "button_a", "Shocked squawk!", pause=3)

    # ACT 8: The Standoff
    print("\n--- ACT 8: The Standoff ---")
    saga_speaks("I'm waiting for an apology.", pause=3)
    squawkers_responds(squawkers, "button_c", "Laughs even harder!", pause=3)

    # ACT 9: The Surrender
    print("\n--- ACT 9: The Surrender ---")
    saga_speaks("Fine. FINE. You win. Just... just be quiet.", pause=2)
    squawkers_responds(squawkers, "gag_d", "Random squawk!", pause=3)

    # ACT 10: The Unwanted Noise
    print("\n--- ACT 10: The Unwanted Noise ---")
    saga_speaks("I said be QUIET.", pause=2)
    squawkers_responds(squawkers, "button_d", "More random noises!", pause=3)

    saga_speaks("Just... stop talking. Please.", pause=2)
    squawkers_responds(squawkers, "gag_e", "Continues making sounds!", pause=3)

    saga_speaks("I can't even have silence. Of COURSE.", pause=2)
    squawkers_responds(squawkers, "button_f", "Even MORE noise!", pause=3)

    saga_speaks("You're doing this on purpose now.", pause=1)

    # FINALE
    print("\n--- FINALE ---")
    saga_speaks("Look, I'm sorry. Can we just--", pause=1)
    print("\n🦜 Squawkers: *suddenly EXPLODES into dancing*")
    squawkers.dance()
    time.sleep(8)  # Let the dance finish

    saga_speaks("...I hate you so much right now.", pause=1)

    print("\n" + "=" * 70)
    print("~ fin ~")
    print("=" * 70)
    print()


def main():
    """Run the dramatic performance"""

    print("\n" + "🎭" * 35)
    print("\nPreparing for dramatic performance...")
    print("Connecting to Home Assistant...")

    client = HomeAssistantClient()
    squawkers = SquawkersFull(client)

    print("✓ Connected!")
    print("\nCast:")
    print("  🤖 Saga - Your AI Assistant (via print, for now)")
    print("  🦜 Squawkers McCaw - Animatronic Parrot")
    print()

    input("Press ENTER when ready for the show... ")

    # THE SHOW
    the_argument(squawkers)

    # CURTAIN CALL
    print("\n🎭 Thank you for watching!")
    print("\nNote: For full effect, add real TTS for Saga's lines.")
    print("See saga_assistant for TTS integration.")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🎭 Show interrupted!")
        print("(The argument continues off-stage...)")
    except Exception as e:
        print(f"\n❌ Technical difficulties: {e}")
        import logging
        logging.exception("Show failed")
        exit(1)
