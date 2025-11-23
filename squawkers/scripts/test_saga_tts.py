#!/usr/bin/env python3
"""
Quick test to verify Saga's TTS voice can be loaded.
"""

import sys
from pathlib import Path
import numpy as np
import sounddevice as sd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from piper import PiperVoice

TTS_VOICE = "en_GB-semaine-medium"

def main():
    print("Testing Saga TTS voice loading...")

    # Load voice
    models_dir = Path.home() / ".local" / "share" / "piper" / "voices"
    model_file = models_dir / f"{TTS_VOICE}.onnx"
    config_file = models_dir / f"{TTS_VOICE}.onnx.json"

    print(f"Model file: {model_file}")
    print(f"Config file: {config_file}")
    print(f"Model exists: {model_file.exists()}")
    print(f"Config exists: {config_file.exists()}")

    if not (model_file.exists() and config_file.exists()):
        print("\n❌ Voice files not found!")
        return 1

    print("\nLoading voice...")
    tts_voice = PiperVoice.load(str(model_file), config_path=str(config_file))
    print(f"✓ Voice loaded: {TTS_VOICE}")

    print("\nSynthesizing test phrase...")
    text = "Hello, I'm Saga. This is a test."

    audio_chunks = []
    for audio_chunk in tts_voice.synthesize(text):
        audio_chunks.append(audio_chunk.audio_int16_array)

    if audio_chunks:
        audio_array = np.concatenate(audio_chunks)
        print(f"✓ Synthesized {len(audio_array)} samples")
        print(f"  Sample rate: {tts_voice.config.sample_rate}Hz")
        print(f"  Duration: {len(audio_array) / tts_voice.config.sample_rate:.2f}s")

        # Play
        print("\nPlaying audio...")
        sd.play(audio_array, samplerate=tts_voice.config.sample_rate)
        sd.wait()
        print("✓ Done!")
    else:
        print("❌ No audio generated")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
