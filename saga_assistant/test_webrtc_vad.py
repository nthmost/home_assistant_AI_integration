#!/usr/bin/env python3
"""Simple WebRTC VAD test."""

import numpy as np
import sounddevice as sd
import webrtcvad

EMEET_DEVICE_NAME = "EMEET"
SAMPLE_RATE = 16000
# WebRTC VAD accepts 10, 20, or 30ms frames
FRAME_DURATION_MS = 30  # 30ms frames
CHUNK_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)  # 480 samples

# Find EMEET
print("🔍 Finding EMEET...")
devices = sd.query_devices()
emeet_input = None

for idx, device in enumerate(devices):
    if EMEET_DEVICE_NAME.lower() in device['name'].lower():
        if device['max_input_channels'] > 0:
            emeet_input = idx
            print(f"✅ Found: {device['name']} (device {idx})")
            break

if emeet_input is None:
    print("❌ EMEET not found!")
    exit(1)

# Create WebRTC VAD
print("\n🔊 Loading WebRTC VAD...")
vad = webrtcvad.Vad()
vad.set_mode(2)  # Aggressiveness: 0 (least) to 3 (most). 2 is balanced.
print("✅ VAD loaded (mode=2, balanced)")

# Test audio input
print(f"\n🎤 Testing audio input (10 seconds)...")
print("   SPEAK NOW to see if VAD detects speech\n")

try:
    with sd.InputStream(
        device=emeet_input,
        channels=1,
        samplerate=SAMPLE_RATE,
        dtype='int16',
        blocksize=CHUNK_SIZE
    ) as stream:

        speech_count = 0  # Track consecutive speech detections

        for i in range(333):  # ~10 seconds (333 chunks * 30ms)
            # Read audio
            audio_chunk, overflowed = stream.read(CHUNK_SIZE)

            if overflowed:
                print("⚠️  Buffer overflow!")

            # Check audio levels
            audio_flat = audio_chunk.flatten()
            max_level = np.max(np.abs(audio_flat))

            # Convert to bytes for WebRTC VAD
            audio_bytes = audio_flat.tobytes()

            # Run VAD
            try:
                is_speech = vad.is_speech(audio_bytes, SAMPLE_RATE)

                # Track speech detection
                if is_speech:
                    speech_count += 1
                else:
                    speech_count = 0

            except Exception as e:
                print(f"VAD error: {e}")
                is_speech = False
                speech_count = 0

            # Show status every 10 chunks (~0.3s)
            if i % 10 == 0:
                level_bar = "█" * min(int(max_level / 1000), 20)
                speech_indicator = "🗣️ SPEECH" if speech_count > 3 else "🔇 silence"
                speech_bar = "█" * min(speech_count, 20)

                print(f"{speech_indicator} | Chunk {i:3d} | Level: {max_level:5d} {level_bar:20s} | "
                      f"Speech: {is_speech!s:5s} {speech_bar:20s} | Count: {speech_count}")

except KeyboardInterrupt:
    print("\n⏹️  Stopped\n")
except Exception as e:
    print(f"\n❌ Error: {e}\n")
    import traceback
    traceback.print_exc()

print("\n✅ Test complete!")
