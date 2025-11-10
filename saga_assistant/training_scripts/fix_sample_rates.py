#!/usr/bin/env python3
"""
Fix sample rates of generated clips by resampling to 16kHz
"""

import os
import wave
import numpy as np
from pathlib import Path
from scipy import signal
from tqdm import tqdm

def resample_wav_file(input_path, output_path=None, target_rate=16000):
    """Resample a WAV file to target sample rate"""
    if output_path is None:
        output_path = input_path

    # Read original WAV
    with wave.open(str(input_path), 'rb') as wav:
        orig_rate = wav.getframerate()
        n_channels = wav.getnchannels()
        sampwidth = wav.getsampwidth()
        frames = wav.readframes(wav.getnframes())

    # If already at target rate, skip
    if orig_rate == target_rate:
        return False

    # Convert to numpy array
    if sampwidth == 2:  # 16-bit
        audio = np.frombuffer(frames, dtype=np.int16)
    else:
        raise ValueError(f"Unsupported sample width: {sampwidth}")

    # Handle stereo
    if n_channels == 2:
        audio = audio.reshape(-1, 2)
        audio = audio.mean(axis=1).astype(np.int16)  # Convert to mono
        n_channels = 1

    # Resample
    num_samples = int(len(audio) * target_rate / orig_rate)
    resampled = signal.resample(audio, num_samples).astype(np.int16)

    # Write resampled WAV
    with wave.open(str(output_path), 'wb') as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(target_rate)
        wav.writeframes(resampled.tobytes())

    return True

def main():
    clips_dir = Path("my_custom_model/hey_saga")

    if not clips_dir.exists():
        print(f"❌ Directory not found: {clips_dir}")
        return 1

    print("🔧 Fixing sample rates of generated clips...\n")

    total_fixed = 0

    # Process each subdirectory
    for subdir in ["positive_train", "positive_test", "negative_train", "negative_test"]:
        subdir_path = clips_dir / subdir
        if not subdir_path.exists():
            print(f"⚠️  Skipping {subdir}: Directory doesn't exist")
            continue

        wav_files = list(subdir_path.glob("*.wav"))
        if not wav_files:
            print(f"⚠️  Skipping {subdir}: No WAV files found")
            continue

        print(f"📁 Processing {subdir} ({len(wav_files)} files)...")

        fixed = 0
        for wav_file in tqdm(wav_files, desc=f"  {subdir}"):
            try:
                if resample_wav_file(wav_file):
                    fixed += 1
            except Exception as e:
                print(f"\n❌ Error processing {wav_file.name}: {e}")

        if fixed > 0:
            print(f"   ✅ Resampled {fixed} files to 16kHz")
        else:
            print(f"   ✅ All files already at 16kHz")

        total_fixed += fixed
        print()

    print(f"\n🎉 Complete! Resampled {total_fixed} files total.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
