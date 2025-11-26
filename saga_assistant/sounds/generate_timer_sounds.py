#!/usr/bin/env python3
"""
Generate iconic timer sounds for Saga Assistant.

Creates a library of recognizable, pleasant sounds for different timer types.
"""

import numpy as np
import wave
import struct
from pathlib import Path


def save_wav(filename: str, samples: np.ndarray, sample_rate: int = 44100):
    """Save audio samples to WAV file."""
    # Normalize to 16-bit range
    samples = np.clip(samples, -1.0, 1.0)
    samples = (samples * 32767).astype(np.int16)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())

    print(f"✅ Generated: {filename}")


def generate_sine_tone(frequency: float, duration: float, sample_rate: int = 44100) -> np.ndarray:
    """Generate a pure sine wave."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return np.sin(2 * np.pi * frequency * t)


def apply_envelope(samples: np.ndarray, attack: float = 0.01, release: float = 0.1) -> np.ndarray:
    """Apply ADSR envelope (simplified to AR)."""
    n = len(samples)
    envelope = np.ones(n)

    # Attack
    attack_samples = int(len(samples) * attack)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Release
    release_samples = int(len(samples) * release)
    envelope[-release_samples:] = np.linspace(1, 0, release_samples)

    return samples * envelope


def kitchen_timer():
    """Classic kitchen timer bell - three dings."""
    sr = 44100
    dings = []

    # Three bell tones
    for i in range(3):
        # Bell is a mix of fundamental and harmonics
        fundamental = 880  # A5
        tone = (
            generate_sine_tone(fundamental, 0.3, sr) * 0.5 +
            generate_sine_tone(fundamental * 2, 0.3, sr) * 0.3 +
            generate_sine_tone(fundamental * 3, 0.3, sr) * 0.2
        )
        tone = apply_envelope(tone, attack=0.01, release=0.4)

        dings.append(tone)

        # Silence between dings
        if i < 2:
            dings.append(np.zeros(int(sr * 0.15)))

    return np.concatenate(dings)


def tea_kettle():
    """Tea kettle whistle - rising then steady."""
    sr = 44100
    duration = 1.5

    # Whistle starts at 1500 Hz and rises to 2000 Hz
    t = np.linspace(0, duration, int(sr * duration), False)
    freq = np.linspace(1500, 2000, len(t))

    # Generate swept sine
    phase = 2 * np.pi * np.cumsum(freq) / sr
    whistle = np.sin(phase)

    # Add some harmonics for richness
    whistle += 0.3 * np.sin(phase * 2)

    # Apply envelope
    whistle = apply_envelope(whistle, attack=0.1, release=0.3)

    return whistle * 0.7


def meditation_bowl():
    """Singing bowl / meditation chime."""
    sr = 44100
    duration = 2.5

    # Singing bowl is a complex tone around 440 Hz with inharmonic partials
    fundamental = 440

    bowl = (
        generate_sine_tone(fundamental, duration, sr) * 0.4 +
        generate_sine_tone(fundamental * 2.1, duration, sr) * 0.3 +
        generate_sine_tone(fundamental * 3.7, duration, sr) * 0.2 +
        generate_sine_tone(fundamental * 5.2, duration, sr) * 0.1
    )

    # Long decay
    bowl = apply_envelope(bowl, attack=0.02, release=0.7)

    return bowl * 0.6


def laundry_chime():
    """Pleasant two-tone chime (doorbell style)."""
    sr = 44100

    # First tone: E6 (1318.5 Hz)
    tone1 = generate_sine_tone(1319, 0.4, sr)
    tone1 = apply_envelope(tone1, attack=0.01, release=0.3)

    # Brief pause
    pause = np.zeros(int(sr * 0.05))

    # Second tone: C6 (1046.5 Hz) - lower, ending tone
    tone2 = generate_sine_tone(1047, 0.6, sr)
    tone2 = apply_envelope(tone2, attack=0.01, release=0.4)

    return np.concatenate([tone1, pause, tone2]) * 0.7


def cooking_timer():
    """Friendly triple beep."""
    sr = 44100
    beeps = []

    freq = 800  # Pleasant mid-tone

    for i in range(3):
        beep = generate_sine_tone(freq, 0.15, sr)
        beep = apply_envelope(beep, attack=0.01, release=0.5)
        beeps.append(beep)

        # Silence between beeps
        if i < 2:
            beeps.append(np.zeros(int(sr * 0.1)))

    return np.concatenate(beeps) * 0.7


def workout_timer():
    """Energetic ascending beeps."""
    sr = 44100
    beeps = []

    # Three ascending tones
    freqs = [600, 800, 1000]

    for freq in freqs:
        beep = generate_sine_tone(freq, 0.15, sr)
        beep = apply_envelope(beep, attack=0.01, release=0.3)
        beeps.append(beep)
        beeps.append(np.zeros(int(sr * 0.05)))

    return np.concatenate(beeps) * 0.8


def bike_timer():
    """Bike bell - two short dings."""
    sr = 44100
    dings = []

    # Bright bell tone
    fundamental = 1200

    for i in range(2):
        tone = (
            generate_sine_tone(fundamental, 0.2, sr) * 0.5 +
            generate_sine_tone(fundamental * 2, 0.2, sr) * 0.4 +
            generate_sine_tone(fundamental * 3, 0.2, sr) * 0.2
        )
        tone = apply_envelope(tone, attack=0.005, release=0.4)

        dings.append(tone)

        if i < 1:
            dings.append(np.zeros(int(sr * 0.1)))

    return np.concatenate(dings) * 0.7


def pomodoro_timer():
    """Work timer - single decisive tone."""
    sr = 44100

    # Strong single tone
    fundamental = 700

    tone = (
        generate_sine_tone(fundamental, 0.5, sr) * 0.6 +
        generate_sine_tone(fundamental * 2, 0.5, sr) * 0.3
    )

    tone = apply_envelope(tone, attack=0.01, release=0.4)

    return tone * 0.8


def parking_meter():
    """Urgent alert - fast triple beep."""
    sr = 44100
    beeps = []

    freq = 1000  # Attention-getting

    for i in range(3):
        beep = generate_sine_tone(freq, 0.1, sr)
        beep = apply_envelope(beep, attack=0.005, release=0.2)
        beeps.append(beep)

        if i < 2:
            beeps.append(np.zeros(int(sr * 0.08)))

    return np.concatenate(beeps) * 0.9


def default_timer():
    """Generic pleasant beep."""
    sr = 44100

    # Simple two-tone
    tone1 = generate_sine_tone(800, 0.3, sr)
    tone1 = apply_envelope(tone1, attack=0.01, release=0.3)

    pause = np.zeros(int(sr * 0.1))

    tone2 = generate_sine_tone(800, 0.3, sr)
    tone2 = apply_envelope(tone2, attack=0.01, release=0.3)

    return np.concatenate([tone1, pause, tone2]) * 0.7


def main():
    """Generate all timer sounds."""
    output_dir = Path(__file__).parent / "timers"
    output_dir.mkdir(exist_ok=True)

    print("🎵 Generating timer sounds...")
    print()

    sounds = {
        "kitchen": (kitchen_timer(), "Classic kitchen timer bell - three dings"),
        "tea": (tea_kettle(), "Tea kettle whistle"),
        "meditation": (meditation_bowl(), "Singing bowl / meditation chime"),
        "laundry": (laundry_chime(), "Pleasant two-tone doorbell chime"),
        "cooking": (cooking_timer(), "Friendly triple beep"),
        "workout": (workout_timer(), "Energetic ascending beeps"),
        "bike": (bike_timer(), "Bike bell - two short dings"),
        "pomodoro": (pomodoro_timer(), "Work timer - single decisive tone"),
        "parking": (parking_meter(), "Urgent alert - fast triple beep"),
        "default": (default_timer(), "Generic pleasant two-tone beep"),
    }

    for name, (samples, description) in sounds.items():
        filename = output_dir / f"{name}.wav"
        save_wav(str(filename), samples)
        print(f"   📝 {description}")
        print()

    print("✅ All timer sounds generated!")
    print(f"📁 Location: {output_dir}")


if __name__ == "__main__":
    main()
