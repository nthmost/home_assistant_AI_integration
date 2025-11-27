#!/usr/bin/env python3
"""
Demo script for testing Piper TTS with EMEET speaker.

Tests text-to-speech synthesis and audio playback with Northern English voice.
"""

import argparse
import io
import logging
import sys
import time
import wave
from pathlib import Path

import sounddevice as sd
import numpy as np

try:
    from piper import PiperVoice
except ImportError:
    print("ERROR: piper-tts not installed. Run: pipenv install piper-tts")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Audio configuration (EMEET speaker)
EMEET_DEVICE_NAME = "EMEET"
SAMPLE_RATE = 22050  # Piper default sample rate

# Voice configuration
# Preferred voices: semaine (default), alba, cori (all British, fast, pleasant)
DEFAULT_VOICE = "en_GB-semaine-medium"
VOICE_BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main"


def find_emeet_output() -> tuple[int, dict] | None:
    """
    Find EMEET speaker device.

    Returns:
        Tuple of (device_index, device_info) or None if not found
    """
    devices = sd.query_devices()

    for idx, device in enumerate(devices):
        if EMEET_DEVICE_NAME.lower() in device['name'].lower():
            # Must have output channels
            if device['max_output_channels'] > 0:
                return (idx, device)

    return None


def download_voice(voice_name: str, models_dir: Path) -> tuple[Path, Path]:
    """
    Download Piper voice model if not already present.

    Args:
        voice_name: Voice identifier (e.g., "en_GB-northern_english_male-medium")
        models_dir: Directory to store models

    Returns:
        Tuple of (model_path, config_path)
    """
    models_dir.mkdir(parents=True, exist_ok=True)

    model_file = models_dir / f"{voice_name}.onnx"
    config_file = models_dir / f"{voice_name}.onnx.json"

    # Check if already downloaded
    if model_file.exists() and config_file.exists():
        logger.info(f"✅ Voice already downloaded: {voice_name}")
        return (model_file, config_file)

    logger.info(f"📥 Downloading voice: {voice_name}")
    logger.info("   This may take a minute on first run...")

    import urllib.request

    # Parse voice name: en_GB-northern_english_male-medium
    # -> en/en_GB/northern_english_male/medium/en_GB-northern_english_male-medium.onnx
    parts = voice_name.split('-', 2)  # Split into max 3 parts
    if len(parts) >= 3:
        lang = parts[0]  # en_GB
        voice = '-'.join(parts[1:-1]) if len(parts) > 3 else parts[1]  # northern_english_male
        quality = parts[-1]  # medium

        # Construct path: en/en_GB/northern_english_male/medium/
        lang_code = lang.split('_')[0]  # en
        path = f"{lang_code}/{lang}/{voice}/{quality}"
    else:
        raise ValueError(f"Invalid voice name format: {voice_name}")

    # Download model
    model_url = f"{VOICE_BASE_URL}/{path}/{voice_name}.onnx"
    logger.info(f"   Downloading model from: {model_url}")
    urllib.request.urlretrieve(model_url, model_file)

    # Download config
    config_url = f"{VOICE_BASE_URL}/{path}/{voice_name}.onnx.json"
    logger.info(f"   Downloading config from: {config_url}")
    urllib.request.urlretrieve(config_url, config_file)

    logger.info(f"✅ Voice downloaded successfully")

    return (model_file, config_file)


class TextToSpeech:
    """Piper TTS engine."""

    def __init__(self, voice_name: str = DEFAULT_VOICE):
        """
        Initialize TTS engine.

        Args:
            voice_name: Voice identifier
        """
        logger.info(f"🔊 Loading Piper voice: {voice_name}")
        start = time.time()

        # Download voice if needed
        models_dir = Path.home() / ".local" / "share" / "piper" / "voices"
        model_path, config_path = download_voice(voice_name, models_dir)

        # Load voice
        self.voice = PiperVoice.load(str(model_path), config_path=str(config_path))
        self.sample_rate = self.voice.config.sample_rate

        load_time = time.time() - start
        logger.info(f"✅ Voice loaded in {load_time:.2f}s")
        logger.info(f"   Sample rate: {self.sample_rate} Hz")

    def synthesize(self, text: str) -> tuple[np.ndarray, float]:
        """
        Synthesize text to speech.

        Args:
            text: Text to speak

        Returns:
            Tuple of (audio_data, synthesis_time_ms)
        """
        start = time.time()

        # Synthesize directly to audio samples
        # Piper's synthesize() returns a generator of AudioChunk objects
        audio_chunks = []
        for i, audio_chunk in enumerate(self.voice.synthesize(text)):
            # Debug: check what we actually got
            if i == 0:
                logger.info(f"   AudioChunk type: {type(audio_chunk)}")
                logger.info(f"   AudioChunk attributes: {dir(audio_chunk)}")

            # AudioChunk has audio_int16_array property (not a method!)
            audio_chunks.append(audio_chunk.audio_int16_array)

        # Concatenate all chunks
        if audio_chunks:
            audio_array = np.concatenate(audio_chunks)
        else:
            audio_array = np.array([], dtype=np.int16)

        synthesis_time = (time.time() - start) * 1000  # Convert to ms

        # Debug info
        duration = len(audio_array) / self.sample_rate if len(audio_array) > 0 else 0
        logger.info(f"   Generated {len(audio_array)} audio samples ({duration:.2f}s)")

        return audio_array, synthesis_time


def play_audio(device_index: int, audio_data: np.ndarray, sample_rate: int) -> float:
    """
    Play audio through speaker.

    Args:
        device_index: Audio device index
        audio_data: Audio data as numpy array (int16)
        sample_rate: Sample rate in Hz

    Returns:
        Playback duration in seconds
    """
    logger.info("🔊 Playing audio...")

    start = time.time()
    sd.play(audio_data, samplerate=sample_rate, device=device_index)
    sd.wait()  # Wait until playback finishes

    playback_time = time.time() - start

    return playback_time


def main():
    parser = argparse.ArgumentParser(
        description="Test Piper TTS with EMEET speaker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic test
  python demo_tts.py

  # Custom text
  python demo_tts.py --text "Turn on the living room lights"

  # Different voice (if you want to try others)
  python demo_tts.py --voice en_GB-alba-medium

Available Northern English voices:
  - en_GB-northern_english_male-medium (default)
        """
    )
    parser.add_argument(
        "--text",
        type=str,
        default="Hello, I am Saga, your voice assistant.",
        help="Text to synthesize"
    )
    parser.add_argument(
        "--voice",
        type=str,
        default=DEFAULT_VOICE,
        help=f"Voice identifier (default: {DEFAULT_VOICE})"
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List all audio devices and exit"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of test runs (default: 1)"
    )

    args = parser.parse_args()

    # Print banner
    print("\n" + "="*60)
    print("🔊 PIPER TTS TEST")
    print("="*60)

    # List devices mode
    if args.list_devices:
        print("\nAvailable audio output devices:\n")
        devices = sd.query_devices()
        for idx, device in enumerate(devices):
            if device['max_output_channels'] > 0:
                marker = "🔊" if EMEET_DEVICE_NAME.lower() in device['name'].lower() else "  "
                print(f"{marker} [{idx}] {device['name']}")
                print(f"       {device['max_output_channels']} output channels, {device['default_samplerate']} Hz")
        print()
        return 0

    # Find EMEET device
    logger.info("🔍 Looking for EMEET speaker...")
    emeet = find_emeet_output()

    if emeet is None:
        logger.error("❌ EMEET speaker not found!")
        logger.info("\n💡 Troubleshooting:")
        logger.info("   1. Check that EMEET device is plugged in")
        logger.info("   2. Check macOS Sound Settings (System Preferences > Sound > Output)")
        logger.info("   3. Run with --list-devices to see all available devices")
        return 1

    device_idx, device_info = emeet
    logger.info(f"✅ Found EMEET device: {device_info['name']}")
    logger.info(f"   Device index: {device_idx}")
    logger.info(f"   Sample rate: {device_info['default_samplerate']} Hz")
    logger.info(f"   Channels: {device_info['max_output_channels']}")

    # Initialize TTS
    try:
        logger.info(f"\n📦 Initializing Piper TTS: {args.voice}")
        logger.info("   (First run will download the voice - may take a minute)")
        tts = TextToSpeech(voice_name=args.voice)
    except Exception as e:
        logger.error(f"❌ Failed to initialize TTS: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Run test synthesis
    logger.info(f"\n{'='*60}")
    logger.info(f"🎯 Running {args.runs} test(s)")
    logger.info(f"{'='*60}")
    logger.info(f"📝 Text: \"{args.text}\"")
    logger.info(f"{'='*60}\n")

    total_synthesis_time = 0
    total_playback_time = 0

    for i in range(args.runs):
        if args.runs > 1:
            print(f"\n{'─'*60}")
            print(f"Test {i+1} of {args.runs}")
            print(f"{'─'*60}")

        try:
            # Synthesize
            print("🧠 Synthesizing speech...", flush=True)
            audio, synthesis_time = tts.synthesize(args.text)
            total_synthesis_time += synthesis_time

            print(f"⏱️  Synthesis time: {synthesis_time:.0f}ms")

            # Play
            playback_time = play_audio(device_idx, audio, tts.sample_rate)
            total_playback_time += playback_time

            print(f"⏱️  Playback duration: {playback_time:.2f}s")
            print(f"✅ Test complete")

            # Pause between runs
            if i < args.runs - 1:
                print("\n⏸️  Pausing 2 seconds before next test...")
                time.sleep(2)

        except KeyboardInterrupt:
            logger.info("\n\n⏹️  Stopped by user")
            break
        except Exception as e:
            logger.error(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return 1

    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"   Tests completed: {args.runs}")

    if args.runs > 0:
        avg_synthesis = total_synthesis_time / args.runs
        avg_playback = total_playback_time / args.runs

        print(f"   Average synthesis time: {avg_synthesis:.0f}ms")
        print(f"   Average playback duration: {avg_playback:.2f}s")
        print(f"   Target synthesis time: ~200ms")

        if avg_synthesis < 200:
            print(f"   ✅ Under target! Great performance.")
        elif avg_synthesis < 300:
            print(f"   ✅ Close to target. Acceptable for voice assistant.")
        else:
            print(f"   ⚠️  Above target. May need optimization.")

    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
