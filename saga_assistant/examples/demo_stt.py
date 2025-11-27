#!/usr/bin/env python3
"""
Demo script for testing faster-whisper STT with EMEET microphone.

Tests speech-to-text transcription with various recording durations
to find optimal balance of accuracy and latency.
"""

import argparse
import logging
import sys
import time
from pathlib import Path

import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Audio configuration (EMEET microphone specs)
SAMPLE_RATE = 16000  # EMEET supports 16kHz
CHANNELS = 1  # Mono for STT
EMEET_DEVICE_NAME = "EMEET"  # Look for devices with "EMEET" in name


class SpeechToText:
    """Faster-whisper STT engine."""

    def __init__(self, model_size: str = "base", device: str = "cpu"):
        """
        Initialize STT engine.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to run on (cpu, cuda, auto)
        """
        logger.info(f"🔊 Loading Whisper model: {model_size} on {device}")
        start = time.time()

        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type="int8"  # Quantized for speed
        )

        load_time = time.time() - start
        logger.info(f"✅ Model loaded in {load_time:.2f}s")

    def transcribe(self, audio: np.ndarray) -> tuple[str, float]:
        """
        Transcribe audio to text.

        Args:
            audio: Audio data as numpy array (int16)

        Returns:
            Tuple of (transcribed_text, inference_time_ms)
        """
        # Convert int16 to float32 normalized to [-1, 1]
        audio_float = audio.astype(np.float32) / 32768.0

        start = time.time()
        segments, info = self.model.transcribe(
            audio_float,
            language="en",
            beam_size=1,  # Faster, less accurate (default: 5)
            vad_filter=True,  # Voice activity detection
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        # Collect all segments
        text = " ".join(segment.text for segment in segments).strip()

        inference_time = (time.time() - start) * 1000  # Convert to ms

        return text, inference_time


def find_emeet_device() -> tuple[int, dict] | None:
    """
    Find EMEET microphone device.

    Returns:
        Tuple of (device_index, device_info) or None if not found
    """
    devices = sd.query_devices()

    for idx, device in enumerate(devices):
        if EMEET_DEVICE_NAME.lower() in device['name'].lower():
            # Must have input channels
            if device['max_input_channels'] > 0:
                return (idx, device)

    return None


def record_audio(duration: float, device_index: int, countdown: bool = True) -> np.ndarray:
    """
    Record audio from microphone.

    Args:
        duration: Recording duration in seconds
        device_index: Audio device index
        countdown: Show countdown before recording

    Returns:
        Audio data as numpy array (int16)
    """
    if countdown:
        print(f"\n{'='*60}")
        print("🎤 GET READY TO SPEAK!")
        print(f"{'='*60}")
        for i in range(3, 0, -1):
            print(f"   Starting in {i}...", flush=True)
            time.sleep(1)
        print("   🔴 RECORDING NOW - speak clearly into the EMEET microphone!\n")
    else:
        logger.info(f"🎤 Recording for {duration}s...")

    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype='int16',
        device=device_index
    )

    sd.wait()  # Wait for recording to finish

    print(f"   ⏹️  Recording complete!")

    return audio.flatten()


def main():
    parser = argparse.ArgumentParser(
        description="Test faster-whisper STT with EMEET microphone",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic test (3 second recording)
  python demo_stt.py

  # Longer recording for testing sentences
  python demo_stt.py --duration 5

  # Multiple runs to test consistency
  python demo_stt.py --runs 3

  # Use faster but less accurate model
  python demo_stt.py --model tiny
        """
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=5.0,
        help="Recording duration in seconds (default: 5.0)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of test runs (default: 1)"
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List all audio devices and exit"
    )

    args = parser.parse_args()

    # Print banner
    print("\n" + "="*60)
    print("🎤 FASTER-WHISPER STT TEST")
    print("="*60)

    # List devices mode
    if args.list_devices:
        print("\nAvailable audio devices:\n")
        devices = sd.query_devices()
        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                marker = "🎤" if EMEET_DEVICE_NAME.lower() in device['name'].lower() else "  "
                print(f"{marker} [{idx}] {device['name']}")
                print(f"       {device['max_input_channels']} input channels, {device['default_samplerate']} Hz")
        print()
        return 0

    # Find EMEET device
    logger.info("🔍 Looking for EMEET microphone...")
    emeet = find_emeet_device()

    if emeet is None:
        logger.error("❌ EMEET microphone not found!")
        logger.info("\n💡 Troubleshooting:")
        logger.info("   1. Check that EMEET device is plugged in")
        logger.info("   2. Check macOS Sound Settings (System Preferences > Sound > Input)")
        logger.info("   3. Run with --list-devices to see all available devices")
        logger.info("   4. Try running: python demo_audio_devices.py")
        return 1

    device_idx, device_info = emeet
    logger.info(f"✅ Found EMEET device: {device_info['name']}")
    logger.info(f"   Device index: {device_idx}")
    logger.info(f"   Sample rate: {device_info['default_samplerate']} Hz")
    logger.info(f"   Channels: {device_info['max_input_channels']}")

    # Initialize STT
    try:
        logger.info(f"\n📦 Initializing Whisper model: {args.model}")
        logger.info("   (First run will download the model - may take a minute)")
        stt = SpeechToText(model_size=args.model)
    except Exception as e:
        logger.error(f"❌ Failed to initialize STT: {e}")
        return 1

    # Run test recordings
    logger.info(f"\n{'='*60}")
    logger.info(f"🎯 Running {args.runs} test(s) - {args.duration}s recording each")
    logger.info(f"{'='*60}")

    total_inference_time = 0
    successful_transcriptions = 0

    for i in range(args.runs):
        if args.runs > 1:
            print(f"\n{'─'*60}")
            print(f"Test {i+1} of {args.runs}")
            print(f"{'─'*60}")

        try:
            # Record audio (with countdown on first run)
            audio = record_audio(args.duration, device_idx, countdown=(i == 0))

            # Transcribe
            print("\n   🧠 Transcribing...", flush=True)
            text, inference_time = stt.transcribe(audio)
            total_inference_time += inference_time

            # Display results
            print(f"\n{'─'*60}")
            print(f"⏱️  Inference time: {inference_time:.0f}ms")
            print(f"📝 Transcription:")
            print(f"   \"{text}\"")
            print(f"{'─'*60}")

            if text:
                successful_transcriptions += 1
            else:
                logger.warning("\n⚠️  No speech detected - try speaking louder or closer to mic")

            # Pause between runs
            if i < args.runs - 1:
                print("\n   ⏸️  Pausing 2 seconds before next test...")
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
    print(f"   Tests completed: {successful_transcriptions}/{args.runs}")

    if successful_transcriptions > 0:
        avg_inference = total_inference_time / successful_transcriptions
        print(f"   Average inference time: {avg_inference:.0f}ms")
        print(f"   Target for voice assistant: ~200ms")

        if avg_inference < 200:
            print(f"   ✅ Under target! Great performance.")
        elif avg_inference < 300:
            print(f"   ✅ Close to target. Acceptable for voice assistant.")
        else:
            print(f"   ⚠️  Above target. Consider using 'tiny' model.")

    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
