#!/usr/bin/env python3
"""
Check sample rates of generated clips to diagnose the issue
"""

import os
import wave
from pathlib import Path
from collections import Counter

def check_wav_sample_rate(wav_path):
    """Get sample rate from WAV file"""
    try:
        with wave.open(str(wav_path), 'rb') as wav:
            return wav.getframerate()
    except Exception as e:
        return f"Error: {e}"

def main():
    clips_dir = Path("my_custom_model/hey_saga")

    if not clips_dir.exists():
        print(f"❌ Directory not found: {clips_dir}")
        return 1

    print("🔍 Checking sample rates of generated clips...\n")

    # Check each subdirectory
    for subdir in ["positive_train", "positive_test", "negative_train", "negative_test"]:
        subdir_path = clips_dir / subdir
        if not subdir_path.exists():
            print(f"⚠️  {subdir}: Directory doesn't exist")
            continue

        wav_files = list(subdir_path.glob("*.wav"))
        if not wav_files:
            print(f"⚠️  {subdir}: No WAV files found")
            continue

        # Check first 10 files
        sample_rates = []
        for wav_file in wav_files[:10]:
            sr = check_wav_sample_rate(wav_file)
            sample_rates.append(sr)

        # Count sample rates
        rate_counts = Counter(sample_rates)

        print(f"📁 {subdir}:")
        print(f"   Total files: {len(wav_files)}")
        print(f"   Sample rates found:")
        for rate, count in rate_counts.items():
            status = "✅" if rate == 16000 else "❌"
            print(f"      {status} {rate} Hz ({count} files checked)")
        print()

    print("\n💡 OpenWakeWord requires 16000 Hz (16 kHz)")

if __name__ == "__main__":
    import sys
    sys.exit(main())
