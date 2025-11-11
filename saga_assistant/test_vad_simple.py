#!/usr/bin/env python3
"""Simple VAD test to debug audio input issue."""

import numpy as np
import sounddevice as sd
import torch

EMEET_DEVICE_NAME = "EMEET"
SAMPLE_RATE = 16000
# Silero VAD requires exactly 512 samples (32ms) at 16kHz
CHUNK_SIZE = 512  # 32ms at 16kHz

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

# Load Silero VAD
print("\n🔊 Loading Silero VAD...")
model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    force_reload=False,
    onnx=False
)
vad_iterator = utils[3](model, threshold=0.5)
print("✅ VAD loaded")

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

        for i in range(312):  # ~10 seconds (312 chunks * 32ms)
            # Read audio
            audio_chunk, overflowed = stream.read(CHUNK_SIZE)

            if overflowed:
                print("⚠️  Buffer overflow!")

            # Check audio levels
            audio_flat = audio_chunk.flatten()
            max_level = np.max(np.abs(audio_flat))

            # Convert to float32 for VAD
            audio_float = audio_flat.astype(np.float32) / 32768.0
            audio_tensor = torch.from_numpy(audio_float)

            # Run VAD
            speech_dict = vad_iterator(audio_tensor, return_seconds=False)
            speech_prob = speech_dict.get('speech_prob', 0.0) if speech_dict else 0.0

            # Track speech detection
            if speech_prob > 0.3:  # Lower threshold for tracking
                speech_count += 1
            else:
                speech_count = 0

            # Show status every 10 chunks (~0.32s)
            if i % 10 == 0:
                level_bar = "█" * min(int(max_level / 1000), 20)
                speech_bar = "█" * min(int(speech_prob * 40), 20)
                status = "🗣️ SPEECH" if speech_count > 3 else "🔇 silence"

                print(f"{status} | Chunk {i:3d} | Level: {max_level:5d} {level_bar:20s} | "
                      f"Speech: {speech_prob:.2f} {speech_bar:20s} | Count: {speech_count}")

except KeyboardInterrupt:
    print("\n⏹️  Stopped\n")
except Exception as e:
    print(f"\n❌ Error: {e}\n")
    import traceback
    traceback.print_exc()

print("\n✅ Test complete!")
