#!/usr/bin/env python3
"""
Download speech samples for use as competing background noise during training.
Uses LibriSpeech test-clean dataset (diverse speakers, high quality).
"""

import os
import sys
import subprocess
import hashlib
from pathlib import Path
import urllib.request
import tarfile
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Target directory for speech noise
SPEECH_NOISE_DIR = Path("data/speech_noise")

# LibriSpeech test-clean - small subset with diverse speakers
# This is a standard speech recognition dataset (public domain)
LIBRISPEECH_URL = "https://www.openslr.org/resources/12/test-clean.tar.gz"
LIBRISPEECH_ARCHIVE = "test-clean.tar.gz"
LIBRISPEECH_MD5 = "39fde525e59672dc6d1551919b1478f8"  # MD5 checksum for verification

def calculate_md5(file_path):
    """Calculate MD5 checksum of a file"""
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def download_file(url, destination, expected_md5=None):
    """Download a file with progress and checksum verification"""
    # Check if file already exists with correct checksum
    if destination.exists():
        if expected_md5:
            logger.info(f"Checking existing file: {destination}")
            actual_md5 = calculate_md5(destination)
            if actual_md5 == expected_md5:
                logger.info(f"✅ File already exists with correct checksum")
                return True
            else:
                logger.warning(f"⚠️  File exists but checksum mismatch, re-downloading...")
                destination.unlink()
        else:
            logger.info(f"✅ File already exists: {destination}")
            return True

    logger.info(f"Downloading {url}")
    try:
        urllib.request.urlretrieve(url, destination)

        # Verify checksum if provided
        if expected_md5:
            actual_md5 = calculate_md5(destination)
            if actual_md5 != expected_md5:
                logger.error(f"❌ Checksum mismatch! Expected {expected_md5}, got {actual_md5}")
                destination.unlink()
                return False

        logger.info(f"✅ Downloaded to {destination}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to download {url}: {e}")
        return False

def convert_flac_to_16khz_wav(flac_file, output_dir, skip_existing=True):
    """Convert FLAC to 16kHz mono WAV using sox (faster than ffmpeg)"""
    output_file = output_dir / f"{flac_file.stem}.wav"

    # Skip if already exists
    if skip_existing and output_file.exists():
        return output_file

    cmd = [
        'sox', str(flac_file),
        '-r', '16000',  # 16kHz sample rate
        '-c', '1',      # Mono
        str(output_file)
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_file
    except FileNotFoundError:
        # Fallback to ffmpeg if sox not available
        cmd = [
            'ffmpeg', '-i', str(flac_file),
            '-ar', '16000', '-ac', '1', '-y',
            str(output_file)
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return output_file
        except FileNotFoundError:
            logger.error("❌ Neither sox nor ffmpeg found. Install one: apt install sox OR apt install ffmpeg")
            return None
    except subprocess.CalledProcessError:
        return None

def main():
    logger.info("="*70)
    logger.info("Downloading Speech Noise Samples (LibriSpeech)")
    logger.info("="*70)
    logger.info("")
    logger.info("This downloads ~350MB of diverse speech samples")
    logger.info("Estimated time: 2-5 minutes")
    logger.info("")

    # Create directories
    SPEECH_NOISE_DIR.mkdir(parents=True, exist_ok=True)
    temp_dir = Path("data/temp_librispeech")
    temp_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Output directory: {SPEECH_NOISE_DIR}")
    logger.info("")

    # Check if we already have processed files
    existing_files = list(SPEECH_NOISE_DIR.glob("*.wav"))
    if len(existing_files) >= 100:
        logger.info(f"✅ Speech noise already exists: {len(existing_files)} files")
        logger.info(f"   Location: {SPEECH_NOISE_DIR}")
        logger.info("")

        # Ask user if they want to re-download
        try:
            response = input("Re-download and convert files? [y/N]: ").strip().lower()
            if response not in ['y', 'yes']:
                logger.info("Skipping download (using existing files)")
                return 0
            else:
                logger.info("Removing existing files and re-downloading...")
                import shutil
                shutil.rmtree(SPEECH_NOISE_DIR)
                SPEECH_NOISE_DIR.mkdir(parents=True, exist_ok=True)
        except (EOFError, KeyboardInterrupt):
            logger.info("\nSkipping download (using existing files)")
            return 0

    # Check if we have a partial conversion (some files but not 100)
    elif len(existing_files) > 0:
        logger.info(f"⚠️  Found {len(existing_files)} existing files (expected 100)")
        logger.info(f"   Location: {SPEECH_NOISE_DIR}")
        logger.info("")

        try:
            response = input("Continue from where we left off? [Y/n]: ").strip().lower()
            if response in ['n', 'no']:
                logger.info("Removing partial files and starting fresh...")
                import shutil
                shutil.rmtree(SPEECH_NOISE_DIR)
                SPEECH_NOISE_DIR.mkdir(parents=True, exist_ok=True)
            else:
                logger.info("Continuing from existing files...")
        except (EOFError, KeyboardInterrupt):
            logger.info("\nContinuing from existing files...")


    # Download LibriSpeech test-clean
    archive_path = temp_dir / LIBRISPEECH_ARCHIVE

    logger.info("Downloading LibriSpeech test-clean dataset...")
    if not download_file(LIBRISPEECH_URL, archive_path, LIBRISPEECH_MD5):
        logger.error("Download failed!")
        return 1

    # Extract tar.gz
    logger.info("Extracting archive...")
    try:
        with tarfile.open(archive_path, 'r:gz') as tar:
            tar.extractall(temp_dir)
        logger.info("✅ Extracted")
    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}")
        return 1

    # Find all FLAC files and convert to 16kHz WAV
    logger.info("Converting FLAC files to 16kHz WAV...")
    flac_files = list((temp_dir / "LibriSpeech" / "test-clean").rglob("*.flac"))
    logger.info(f"Found {len(flac_files)} audio files in archive")

    # Check how many are already converted
    target_count = 100
    files_to_convert = []
    already_converted = []

    for flac_file in flac_files[:target_count]:
        wav_filename = f"{flac_file.stem}.wav"
        wav_path = SPEECH_NOISE_DIR / wav_filename
        if wav_path.exists():
            already_converted.append(wav_path)
        else:
            files_to_convert.append(flac_file)

    if already_converted:
        logger.info(f"  Already converted: {len(already_converted)} files")

    if not files_to_convert:
        logger.info(f"✅ All {len(already_converted)} files already converted, skipping conversion")
    else:
        logger.info(f"  Converting {len(files_to_convert)} new files...")
        converted_count = 0
        for flac_file in files_to_convert:
            wav_file = convert_flac_to_16khz_wav(flac_file, SPEECH_NOISE_DIR, skip_existing=False)
            if wav_file:
                converted_count += 1
                if converted_count % 10 == 0:
                    logger.info(f"    Progress: {converted_count}/{len(files_to_convert)} files...")

        logger.info(f"✅ Converted {converted_count} new files to 16kHz WAV")

    # Clean up
    logger.info("Cleaning up temporary files...")
    import shutil
    shutil.rmtree(temp_dir)

    # Summary
    wav_files = list(SPEECH_NOISE_DIR.glob("*.wav"))
    logger.info("")
    logger.info("="*70)
    logger.info(f"✅ Downloaded and processed {len(wav_files)} speech samples")
    logger.info(f"   Location: {SPEECH_NOISE_DIR}")
    logger.info(f"   Total duration: ~{len(wav_files) * 5 / 60:.0f} minutes of speech")
    logger.info("")
    logger.info("These files will be used as background noise for 'noisy' tier training.")
    logger.info("="*70)

    return 0

if __name__ == "__main__":
    sys.exit(main())
