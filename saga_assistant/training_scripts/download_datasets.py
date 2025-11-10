#!/usr/bin/env python3
"""
Download training datasets for OpenWakeWord
- Room impulse responses (MIT)
- Background audio (AudioSet, Free Music Archive)
- Pre-computed negative features (ACAV100M)
- Validation data
"""

import os
import logging
import subprocess
from pathlib import Path
from tqdm import tqdm
import scipy.io.wavfile
import numpy as np

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def download_mit_rirs():
    """Download MIT room impulse responses"""
    logger.info("📥 Downloading MIT Room Impulse Responses...")

    output_dir = Path("./mit_rirs")
    if not output_dir.exists():
        output_dir.mkdir()

    try:
        import datasets
        rir_dataset = datasets.load_dataset(
            "davidscripka/MIT_environmental_impulse_responses",
            split="train",
            streaming=True
        )

        logger.info("   Saving RIR files...")
        count = 0
        for row in tqdm(rir_dataset, desc="RIRs"):
            name = row['audio']['path'].split('/')[-1]
            output_path = output_dir / name
            if not output_path.exists():
                scipy.io.wavfile.write(
                    str(output_path),
                    16000,
                    (row['audio']['array'] * 32767).astype(np.int16)
                )
            count += 1
            if count >= 100:  # Limit for speed, can increase later
                break

        logger.info(f"   ✅ Downloaded {count} RIR files")
        return True

    except Exception as e:
        logger.error(f"   ❌ Failed: {e}")
        return False


def download_audioset():
    """Download a portion of AudioSet for background audio"""
    logger.info("📥 Downloading AudioSet (background audio)...")

    if not Path("audioset").exists():
        Path("audioset").mkdir()

    output_dir = Path("./audioset_16k")
    if not output_dir.exists():
        output_dir.mkdir()

    # Download one tar file from AudioSet
    fname = "bal_train09.tar"
    out_file = f"audioset/{fname}"

    if not Path(out_file).exists():
        link = f"https://huggingface.co/datasets/agkphysics/AudioSet/resolve/main/data/{fname}"
        logger.info(f"   📦 FILE: {fname} (~2GB)")
        logger.info(f"   🔗 URL: {link}")

        result = subprocess.run(
            ["wget", "-O", out_file, link],
            capture_output=False  # Show wget output
        )

        if result.returncode != 0:
            logger.error(f"   ❌ Download failed for {fname}")
            return False

        logger.info(f"   ✅ Downloaded {fname}")

    # Extract
    logger.info("   Extracting archive...")
    subprocess.run(
        ["tar", "-xf", fname],
        cwd="audioset",
        capture_output=True
    )

    # Convert to 16kHz
    logger.info("   Converting to 16kHz...")
    try:
        import datasets
        audio_files = list(Path("audioset/audio").glob("**/*.flac"))
        logger.info(f"   Found {len(audio_files)} files")

        audioset_dataset = datasets.Dataset.from_dict({
            "audio": [str(f) for f in audio_files[:500]]  # Limit for speed
        })
        audioset_dataset = audioset_dataset.cast_column(
            "audio",
            datasets.Audio(sampling_rate=16000)
        )

        for idx, row in enumerate(tqdm(audioset_dataset, desc="Converting")):
            name = row['audio']['path'].split('/')[-1].replace(".flac", ".wav")
            output_path = output_dir / name
            if not output_path.exists():
                scipy.io.wavfile.write(
                    str(output_path),
                    16000,
                    (row['audio']['array'] * 32767).astype(np.int16)
                )

        logger.info(f"   ✅ Converted {len(audioset_dataset)} files")
        return True

    except Exception as e:
        logger.error(f"   ❌ Failed: {e}")
        return False


def download_fma():
    """Download Free Music Archive samples"""
    logger.info("📥 Downloading Free Music Archive (music background)...")

    output_dir = Path("./fma")
    if not output_dir.exists():
        output_dir.mkdir()

    try:
        import datasets
        fma_dataset = datasets.load_dataset(
            "rudraml/fma",
            name="small",
            split="train",
            streaming=True
        )
        fma_dataset = fma_dataset.cast_column(
            "audio",
            datasets.Audio(sampling_rate=16000)
        )

        logger.info("   Downloading 1 hour of music clips...")
        n_hours = 1
        target_clips = n_hours * 3600 // 30  # 30-second clips

        for i, row in enumerate(tqdm(fma_dataset, desc="FMA", total=target_clips)):
            if i >= target_clips:
                break

            name = row['audio']['path'].split('/')[-1].replace(".mp3", ".wav")
            output_path = output_dir / name

            if not output_path.exists():
                scipy.io.wavfile.write(
                    str(output_path),
                    16000,
                    (row['audio']['array'] * 32767).astype(np.int16)
                )

        logger.info(f"   ✅ Downloaded {target_clips} music clips")
        return True

    except Exception as e:
        logger.error(f"   ❌ Failed: {e}")
        return False


def download_negative_features():
    """Download pre-computed negative features"""
    logger.info("📥 Downloading pre-computed negative features...")

    files = [
        ("openwakeword_features_ACAV100M_2000_hrs_16bit.npy",
         "https://huggingface.co/datasets/davidscripka/openwakeword_features/resolve/main/openwakeword_features_ACAV100M_2000_hrs_16bit.npy",
         "~17GB"),
        ("validation_set_features.npy",
         "https://huggingface.co/datasets/davidscripka/openwakeword_features/resolve/main/validation_set_features.npy",
         "~177MB")
    ]

    for filename, url, size in files:
        if Path(filename).exists():
            logger.info(f"   ✅ {filename} already exists")
            continue

        logger.info(f"   📦 FILE: {filename} ({size})")
        logger.info(f"   🔗 URL: {url}")
        result = subprocess.run(
            ["wget", "--show-progress", url],
            capture_output=False
        )

        if result.returncode == 0:
            logger.info(f"   ✅ Downloaded {filename}")
        else:
            logger.error(f"   ❌ Failed to download {filename}")
            return False

    return True


def main():
    logger.info("🚀 Downloading training datasets")
    logger.info("="*60)
    logger.info("This will download ~8GB of data and take ~30-60 minutes")
    logger.info("")

    # Download each dataset
    success = True

    success &= download_mit_rirs()
    logger.info("")

    success &= download_audioset()
    logger.info("")

    success &= download_fma()
    logger.info("")

    success &= download_negative_features()
    logger.info("")

    if success:
        logger.info("="*60)
        logger.info("✅ All datasets downloaded!")
        logger.info("="*60)
        logger.info("")
        logger.info("Next step: Run train_hey_saga.py")
        return 0
    else:
        logger.error("❌ Some downloads failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
