#!/usr/bin/env python3
"""
Audio Device Verification Script

Tests audio input/output capabilities and helps identify the EMEET device.
Includes recording and playback tests.
"""

import logging
import sys
import time
import wave
from pathlib import Path

import sounddevice as sd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def list_audio_devices():
    """List all available audio devices with detailed information."""
    logger.info("🔍 Scanning for audio devices...")
    print("\n" + "="*80)
    print("AVAILABLE AUDIO DEVICES")
    print("="*80)

    devices = sd.query_devices()

    for idx, device in enumerate(devices):
        device_type = []
        if device['max_input_channels'] > 0:
            device_type.append(f"INPUT ({device['max_input_channels']} ch)")
        if device['max_output_channels'] > 0:
            device_type.append(f"OUTPUT ({device['max_output_channels']} ch)")

        type_str = " | ".join(device_type)

        # Highlight EMEET devices
        is_emeet = 'emeet' in device['name'].lower()
        marker = "🎤 EMEET → " if is_emeet else "   "

        print(f"\n{marker}[{idx}] {device['name']}")
        print(f"    Type: {type_str}")
        print(f"    Sample Rate: {device['default_samplerate']} Hz")
        print(f"    Host API: {sd.query_hostapis(device['hostapi'])['name']}")

    print("\n" + "="*80 + "\n")

    # Find EMEET devices
    emeet_devices = [(idx, dev) for idx, dev in enumerate(devices)
                     if 'emeet' in dev['name'].lower()]

    if emeet_devices:
        logger.info(f"✅ Found {len(emeet_devices)} EMEET device(s)")
        for idx, dev in emeet_devices:
            logger.info(f"   Device {idx}: {dev['name']}")
        return emeet_devices
    else:
        logger.warning("⚠️  No EMEET devices found")
        return []


def test_recording(device_id, duration=3, sample_rate=16000):
    """
    Record audio from specified device.

    Args:
        device_id: Device index to record from
        duration: Recording duration in seconds
        sample_rate: Sample rate in Hz (16kHz is good for speech)

    Returns:
        numpy array of recorded audio or None if failed
    """
    logger.info(f"🎙️  Testing recording from device {device_id} for {duration}s...")

    try:
        device_info = sd.query_devices(device_id)
        logger.info(f"   Device: {device_info['name']}")
        logger.info(f"   Sample rate: {sample_rate} Hz")
        logger.info(f"   Channels: 1 (mono)")

        # Record
        logger.info("   🔴 Recording started - please speak!")
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            device=device_id,
            dtype='int16'
        )
        sd.wait()  # Wait until recording is finished
        logger.info("   ⏹️  Recording stopped")

        # Check if we got audio
        max_amplitude = np.max(np.abs(recording))
        logger.info(f"   Max amplitude: {max_amplitude}")

        if max_amplitude > 100:  # Arbitrary threshold
            logger.info("   ✅ Recording successful - audio detected!")
            return recording
        else:
            logger.warning("   ⚠️  Recording too quiet - check microphone")
            return recording

    except Exception as e:
        logger.error(f"   ❌ Recording failed: {e}")
        return None


def test_playback(device_id, audio_data, sample_rate=16000):
    """
    Play audio to specified device.

    Args:
        device_id: Device index to play to
        audio_data: numpy array of audio data
        sample_rate: Sample rate in Hz
    """
    logger.info(f"🔊 Testing playback on device {device_id}...")

    try:
        device_info = sd.query_devices(device_id)
        logger.info(f"   Device: {device_info['name']}")

        logger.info("   ▶️  Playing back recording...")
        sd.play(audio_data, samplerate=sample_rate, device=device_id)
        sd.wait()  # Wait until playback is finished
        logger.info("   ✅ Playback complete")
        return True

    except Exception as e:
        logger.error(f"   ❌ Playback failed: {e}")
        return False


def save_recording(audio_data, filename, sample_rate=16000):
    """Save recording to WAV file."""
    filepath = Path(filename)
    logger.info(f"💾 Saving recording to {filepath}...")

    try:
        with wave.open(str(filepath), 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())

        logger.info(f"   ✅ Saved to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"   ❌ Save failed: {e}")
        return None


def main():
    """Main test sequence."""
    logger.info("🎵 Audio Device Verification Tool")
    logger.info("="*50)

    # Step 1: List all devices
    emeet_devices = list_audio_devices()

    if not emeet_devices:
        logger.error("❌ No EMEET devices found. Please check connection.")
        logger.info("💡 Tip: Make sure the EMEET device is plugged in and recognized by macOS")
        return 1

    # Step 2: Test each EMEET device
    for device_idx, device_info in emeet_devices:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing EMEET device: {device_info['name']}")
        logger.info(f"{'='*50}")

        # Test input if available
        if device_info['max_input_channels'] > 0:
            logger.info("\n📥 INPUT TEST")
            recording = test_recording(device_idx, duration=3)

            if recording is not None:
                # Save the recording
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                save_recording(
                    recording,
                    f"test_recording_{timestamp}.wav"
                )

                # Test playback if output is available
                if device_info['max_output_channels'] > 0:
                    logger.info("\n📤 OUTPUT TEST")
                    test_playback(device_idx, recording)

        elif device_info['max_output_channels'] > 0:
            # Output-only device - generate test tone
            logger.info("\n📤 OUTPUT TEST (test tone)")
            duration = 1.0
            frequency = 440  # A4 note
            sample_rate = 16000

            t = np.linspace(0, duration, int(sample_rate * duration), False)
            test_tone = np.sin(frequency * 2 * np.pi * t) * 0.3
            test_tone = (test_tone * 32767).astype(np.int16)

            test_playback(device_idx, test_tone, sample_rate)

    logger.info("\n" + "="*50)
    logger.info("✅ Audio device verification complete!")
    logger.info("="*50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
