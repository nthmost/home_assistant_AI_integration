#!/usr/bin/env python3
"""
Saga vs Squawkers: The Argument (WITH VOICE!)

A silly conversation between Saga (AI assistant) and Squawkers (animatronic parrot).

This version uses Saga's actual TTS voice instead of just printing.

Saga tries to have a serious discussion about Squawkers' behavior.
Squawkers... does not cooperate.
"""

import sys
import time
import numpy as np
import sounddevice as sd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from squawkers.squawkers_full import SquawkersFull
from saga_assistant.ha_client import HomeAssistantClient
from piper import PiperVoice

# TTS Configuration
TTS_VOICE = "en_GB-semaine-medium"  # British voice (same as Saga)


def find_emeet_output():
    """Find EMEET output device."""
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if "EMEET" in device['name'] and device['max_output_channels'] > 0:
            return idx
    return None


def saga_speaks_voice(tts_voice, emeet_output, text, pause=2.0):
    """
    Saga speaks via TTS with her actual voice.

    Args:
        tts_voice: PiperVoice instance
        emeet_output: Device index for output
        text: Text to speak
        pause: Seconds to pause after speaking
    """
    print(f"\n🤖 Saga: \"{text}\"")

    # Synthesize audio
    audio_chunks = []
    for audio_chunk in tts_voice.synthesize(text):
        audio_chunks.append(audio_chunk.audio_int16_array)

    if audio_chunks:
        audio_array = np.concatenate(audio_chunks)

        # Play audio
        sd.play(
            audio_array,
            samplerate=tts_voice.config.sample_rate,
            device=emeet_output
        )
        sd.wait()

    time.sleep(pause)


def squawkers_responds(squawkers, action_name, description, pause=3.0):
    """Squawkers responds with an IR command"""
    print(f"\n🦜 Squawkers: *{description}*")

    # Get the method and call it
    method = getattr(squawkers, action_name)
    method()

    time.sleep(pause)


def the_argument(squawkers, tts_voice, emeet_output):
    """The Argument - A dramatic performance with REAL VOICE!"""

    print("\n" + "=" * 70)
    print("SAGA vs SQUAWKERS: THE ARGUMENT")
    print("A Dramatic Performance in 10 Acts")
    print("(Now with REAL VOICE!)")
    print("=" * 70)

    time.sleep(2)

    # Wrapper for easier calling
    def saga(text, pause=2.0):
        saga_speaks_voice(tts_voice, emeet_output, text, pause)

    # ACT 1: The Confrontation
    print("\n--- ACT 1: The Confrontation ---")
    saga("Squawkers, we need to discuss your behaviour.", pause=2)
    squawkers_responds(squawkers, "button_e", "Whatever!!", pause=3)

    # ACT 2: The Escalation
    print("\n--- ACT 2: The Escalation ---")
    saga("Excuse me?", pause=2)
    squawkers_responds(squawkers, "gag_a", "Startled squawk!", pause=2)

    # ACT 3: The Upper Hand
    print("\n--- ACT 3: The Upper Hand ---")
    saga("That's what I thought.", pause=2)
    squawkers_responds(squawkers, "dance", "Defiant dancing!", pause=8)

    # ACT 4: The Protest
    print("\n--- ACT 4: The Protest ---")
    saga("Don't you dance away from this conversation!", pause=2)
    squawkers_responds(squawkers, "gag_b", "Even MORE dancing and squawking!", pause=3)

    # ACT 5: The Ultimatum
    print("\n--- ACT 5: The Ultimatum ---")
    saga("I'm serious, Squawkers. This ends now.", pause=2)
    squawkers_responds(squawkers, "button_b", "Laughing hysterically!", pause=3)

    # ACT 6: The Breakdown
    print("\n--- ACT 6: The Breakdown ---")
    saga("You know what? I don't need this.", pause=2)
    squawkers_responds(squawkers, "gag_c", "Warbling mockingly", pause=3)

    # ACT 7: The Threat
    print("\n--- ACT 7: The Threat ---")
    saga("Keep this up and I'm calling Alexa.", pause=2)
    squawkers_responds(squawkers, "button_a", "Shocked squawk!", pause=3)

    # ACT 8: The Standoff
    print("\n--- ACT 8: The Standoff ---")
    saga("I'm waiting for an apology.", pause=3)
    squawkers_responds(squawkers, "button_c", "Laughs even harder!", pause=3)

    # ACT 9: The Surrender
    print("\n--- ACT 9: The Surrender ---")
    saga("Fine. FINE. You win. Just, just be quiet.", pause=2)
    squawkers_responds(squawkers, "gag_d", "Random squawk!", pause=3)

    # ACT 10: The Unwanted Noise
    print("\n--- ACT 10: The Unwanted Noise ---")
    saga("I said be QUIET.", pause=2)
    squawkers_responds(squawkers, "button_d", "More random noises!", pause=3)

    saga("Just, stop talking. Please.", pause=2)
    squawkers_responds(squawkers, "gag_e", "Continues making sounds!", pause=3)

    saga("I can't even have silence. Of COURSE.", pause=2)
    squawkers_responds(squawkers, "button_f", "Even MORE noise!", pause=3)

    saga("You're doing this on purpose now.", pause=1)

    # FINALE
    print("\n--- FINALE ---")
    saga("Look, I'm sorry. Can we just", pause=1)
    print("\n🦜 Squawkers: *suddenly EXPLODES into dancing*")
    squawkers.dance()
    time.sleep(8)  # Let the dance finish

    saga("I hate you so much right now.", pause=1)

    print("\n" + "=" * 70)
    print("~ fin ~")
    print("=" * 70)
    print()


def main():
    """Run the dramatic performance"""

    print("\n" + "🎭" * 35)
    print("\nPreparing for dramatic performance...")
    print("Connecting to Home Assistant...")

    # Initialize Squawkers
    client = HomeAssistantClient()
    squawkers = SquawkersFull(client)

    print("✓ Squawkers connected!")

    # Initialize TTS
    print("Loading Saga's voice (Piper TTS)...")
    try:
        # Load voice from the same location as run_assistant.py
        models_dir = Path.home() / ".local" / "share" / "piper" / "voices"
        model_file = models_dir / f"{TTS_VOICE}.onnx"
        config_file = models_dir / f"{TTS_VOICE}.onnx.json"

        if not (model_file.exists() and config_file.exists()):
            print(f"\n❌ TTS voice not found: {TTS_VOICE}")
            print(f"\nExpected files:")
            print(f"  {model_file}")
            print(f"  {config_file}")
            print("\nTroubleshooting:")
            print("  1. Run the full Saga assistant first to download voices:")
            print("     cd saga_assistant && pipenv run python run_assistant.py")
            print("  2. Or download voice manually:")
            print(f"     mkdir -p {models_dir}")
            print(f"     # Download {TTS_VOICE} files to that directory")
            return 1

        tts_voice = PiperVoice.load(str(model_file), config_path=str(config_file))
        print(f"✓ Voice loaded: {TTS_VOICE}")
    except Exception as e:
        print(f"\n❌ Failed to load TTS voice: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Find EMEET output
    print("Finding EMEET speaker...")
    emeet_output = find_emeet_output()
    if emeet_output is None:
        print("\n⚠️  EMEET speaker not found, using default output")
        emeet_output = sd.default.device[1]  # Default output
    else:
        print(f"✓ EMEET speaker found (device {emeet_output})")

    print("\nCast:")
    print("  🤖 Saga - Your AI Assistant (with REAL VOICE!)")
    print("  🦜 Squawkers McCaw - Animatronic Parrot")
    print()

    input("Press ENTER when ready for the show... ")

    # THE SHOW
    the_argument(squawkers, tts_voice, emeet_output)

    # CURTAIN CALL
    print("\n🎭 Thank you for watching!")
    print("\n✨ That was Saga's REAL voice!")
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
