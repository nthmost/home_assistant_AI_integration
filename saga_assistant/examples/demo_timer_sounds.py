#!/usr/bin/env python3
"""
Demo: Test custom timer sounds.

Plays all available timer sounds to verify they work.
"""

import sys
import time
import sounddevice as sd
import numpy as np
import wave
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from saga_assistant.timer_sounds import TimerSoundManager


def play_wav(wav_path: str):
    """Play a WAV file."""
    try:
        with wave.open(wav_path, 'rb') as wav_file:
            sample_rate = wav_file.getframerate()
            n_channels = wav_file.getnchannels()
            audio_data = wav_file.readframes(wav_file.getnframes())

            # Convert to numpy array
            if wav_file.getsampwidth() == 2:  # 16-bit
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
            else:
                print(f"❌ Unsupported WAV format: {wav_file.getsampwidth()} bytes per sample")
                return

            # Convert to float
            audio_array = audio_array.astype(np.float32) / 32768.0

            # Handle stereo (convert to mono if needed)
            if n_channels == 2:
                audio_array = audio_array.reshape(-1, 2).mean(axis=1)

            # Play audio
            sd.play(audio_array, samplerate=sample_rate)
            sd.wait()

            print("   ✅ Sound played")

    except Exception as e:
        print(f"❌ Failed to play WAV: {e}")


def main():
    """Test all timer sounds."""
    print("=" * 60)
    print("🔊 TIMER SOUNDS DEMO")
    print("=" * 60)
    print()

    manager = TimerSoundManager()

    # Get all available sounds
    sounds = manager.get_available_sounds()

    print(f"Found {len(sounds)} timer sounds:")
    print()

    for sound in sounds:
        print(f"🔔 {sound['name'].upper()}")
        print(f"   📝 {sound['description']}")
        print(f"   🔊 Playing...")

        play_wav(sound['path'])

        print()
        time.sleep(0.5)  # Brief pause between sounds

    print("=" * 60)
    print("✅ All sounds tested!")
    print("=" * 60)
    print()

    # Test database mappings
    print("🗄️  DATABASE MAPPINGS")
    print("=" * 60)
    print()

    timer_types = [
        'laundry', 'tea', 'meditation', 'cooking', 'kitchen',
        'workout', 'bike', 'pomodoro', 'parking'
    ]

    for timer_type in timer_types:
        sound_path = manager.get_sound_for_timer(timer_type)
        if sound_path:
            sound_name = Path(sound_path).stem
            print(f"  {timer_type:15} → {sound_name}")
        else:
            print(f"  {timer_type:15} → (not assigned)")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
