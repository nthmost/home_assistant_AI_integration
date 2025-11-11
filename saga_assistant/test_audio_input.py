#!/usr/bin/env python3
"""Quick audio input diagnostic tool.

Tests if audio is being captured from EMEET microphone.
"""

import numpy as np
import sounddevice as sd

EMEET_DEVICE_NAME = "EMEET"
SAMPLE_RATE = 16000
DURATION = 3  # seconds

# Find EMEET device
print("🔍 Looking for EMEET device...\n")
devices = sd.query_devices()

emeet_input = None
for idx, device in enumerate(devices):
    if EMEET_DEVICE_NAME.lower() in device['name'].lower():
        if device['max_input_channels'] > 0:
            emeet_input = idx
            print(f"✅ Found: {device['name']}")
            print(f"   Device index: {idx}")
            print(f"   Channels: {device['max_input_channels']}")
            print(f"   Default sample rate: {device['default_samplerate']}")
            break

if emeet_input is None:
    print("❌ EMEET device not found!")
    exit(1)

print(f"\n🎤 Recording {DURATION} seconds from EMEET...")
print("   SPEAK NOW!\n")

# Record audio
audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype='int16',
    device=emeet_input
)
sd.wait()

print("✅ Recording complete\n")

# Analyze audio
audio_flat = audio.flatten()
max_val = np.max(np.abs(audio_flat))
rms = np.sqrt(np.mean(audio_flat.astype(float)**2))

print("📊 Audio Analysis:")
print(f"   Samples recorded: {len(audio_flat)}")
print(f"   Max amplitude: {max_val} (range: 0-32768)")
print(f"   RMS level: {rms:.1f}")
print(f"   Duration: {len(audio_flat)/SAMPLE_RATE:.2f}s")

# Check if we got audio
if max_val < 100:
    print("\n⚠️  WARNING: Very low audio levels!")
    print("   Possible issues:")
    print("   - Microphone is muted")
    print("   - Wrong input device selected")
    print("   - Microphone permissions not granted")
    print("   - Cable/connection issue")
elif max_val < 1000:
    print("\n⚠️  Audio levels are low (but present)")
    print("   Try speaking louder or closer to the microphone")
else:
    print("\n✅ Audio levels look good!")

# Show recent activity
print(f"\n📈 Last 0.5s of audio levels (should show your voice):")
recent_samples = audio_flat[-8000:]  # Last 0.5s
chunk_size = 1600  # 0.1s chunks
for i in range(0, len(recent_samples), chunk_size):
    chunk = recent_samples[i:i+chunk_size]
    chunk_max = np.max(np.abs(chunk))
    bar_length = int(chunk_max / 1000)
    bar = "█" * min(bar_length, 50)
    print(f"   {bar} {chunk_max}")

print("\n💾 Saving recording to test_audio.wav for inspection...")
import scipy.io.wavfile as wav
wav.write("test_audio.wav", SAMPLE_RATE, audio_flat)
print("   Saved! You can play it back to verify.\n")
