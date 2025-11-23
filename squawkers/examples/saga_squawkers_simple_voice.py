#!/usr/bin/env python3
"""
Simple Saga vs Squawkers interaction with REAL VOICE.

A quick demo showing Saga speaking with her actual TTS voice
while Squawkers responds with IR commands.
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


def saga_speaks(tts_voice, emeet_output, text, pause=2.0):
    """Saga speaks via TTS."""
    print(f"\n🤖 Saga: \"{text}\"")

    # Synthesize audio
    audio_chunks = []
    for audio_chunk in tts_voice.synthesize(text):
        audio_chunks.append(audio_chunk.audio_int16_array)

    if audio_chunks:
        audio_array = np.concatenate(audio_chunks)
        sd.play(audio_array, samplerate=tts_voice.config.sample_rate, device=emeet_output)
        sd.wait()

    time.sleep(pause)


def squawkers_responds(squawkers, action_name, description, pause=3.0):
    """Squawkers responds with an IR command."""
    print(f"\n🦜 Squawkers: *{description}*")
    method = getattr(squawkers, action_name)
    method()
    time.sleep(pause)


def main():
    """Run a simple interaction."""

    print("\n" + "=" * 60)
    print("SAGA vs SQUAWKERS: Simple Demo (WITH VOICE!)")
    print("=" * 60)

    # Initialize
    print("\nInitializing...")
    client = HomeAssistantClient()
    squawkers = SquawkersFull(client)

    # Load TTS voice
    models_dir = Path.home() / ".local" / "share" / "piper" / "voices"
    model_file = models_dir / f"{TTS_VOICE}.onnx"
    config_file = models_dir / f"{TTS_VOICE}.onnx.json"

    if not (model_file.exists() and config_file.exists()):
        print(f"\n❌ TTS voice not found: {TTS_VOICE}")
        print("Run: cd saga_assistant && pipenv run python run_assistant.py")
        return 1

    tts_voice = PiperVoice.load(str(model_file), config_path=str(config_file))

    # Find audio output
    emeet_output = find_emeet_output()
    if emeet_output is None:
        emeet_output = sd.default.device[1]

    print("✓ Ready!")
    print()
    time.sleep(1)

    # Simple interaction
    saga_speaks(tts_voice, emeet_output, "Hello, Squawkers.", pause=1)
    squawkers_responds(squawkers, "button_e", "Whatever!!", pause=2)

    saga_speaks(tts_voice, emeet_output, "Excuse me?", pause=1)
    squawkers_responds(squawkers, "button_b", "Laughing!", pause=2)

    saga_speaks(tts_voice, emeet_output, "You're impossible.", pause=1)
    squawkers_responds(squawkers, "dance", "Dancing defiantly!", pause=8)

    saga_speaks(tts_voice, emeet_output, "Of course you are.", pause=1)

    print("\n" + "=" * 60)
    print("~ Demo complete ~")
    print("=" * 60)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
