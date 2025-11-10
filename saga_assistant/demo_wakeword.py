#!/usr/bin/env python3
"""
Wakeword Detection Demo

Tests OpenWakeWord with pre-trained models using the EMEET microphone.
This script demonstrates basic wakeword detection before we train a custom "Hey Saga" model.
"""

import logging
import sys
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
from openwakeword.model import Model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def find_emeet_input_device():
    """Find the EMEET input device index."""
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if 'emeet' in device['name'].lower() and device['max_input_channels'] > 0:
            logger.info(f"✅ Found EMEET input device: {device['name']} (index {idx})")
            return idx
    logger.error("❌ No EMEET input device found")
    return None


def list_available_models():
    """List all available pre-trained models."""
    logger.info("📋 Checking available pre-trained models...")

    # Create a model instance with ONNX inference (works on macOS ARM64)
    oww_model = Model(inference_framework="onnx")

    logger.info(f"   Loaded {len(oww_model.models)} models:")
    for model_name in oww_model.models.keys():
        logger.info(f"   • {model_name}")

    return list(oww_model.models.keys())


def run_wakeword_detection(device_idx, duration=30, threshold=0.5, custom_model_path=None):
    """
    Run live wakeword detection.

    Args:
        device_idx: Audio input device index
        duration: How long to listen (seconds), 0 for infinite
        threshold: Detection threshold (0.0-1.0)
        custom_model_path: Path to custom trained model (optional)
    """
    logger.info(f"🎙️  Starting wakeword detection (threshold: {threshold})")
    logger.info(f"   Device: {sd.query_devices(device_idx)['name']}")
    logger.info(f"   Duration: {'Infinite' if duration == 0 else f'{duration}s'}")
    logger.info(f"   Press Ctrl+C to stop")
    logger.info("")

    # Initialize the model with pre-trained wakewords (using ONNX)
    logger.info("🔄 Loading OpenWakeWord models...")
    if custom_model_path:
        logger.info(f"   Loading custom model: {custom_model_path}")
        oww_model = Model(
            wakeword_models=[custom_model_path],
            inference_framework="onnx"
        )
    else:
        oww_model = Model(inference_framework="onnx")
    logger.info(f"✅ Loaded {len(oww_model.models)} models")

    # Audio configuration (OpenWakeWord expects 16kHz, mono)
    sample_rate = 16000
    chunk_size = 1280  # 80ms chunks (recommended by OpenWakeWord)

    logger.info(f"🎧 Listening for wakewords...")
    logger.info("="*60)

    detection_count = {model: 0 for model in oww_model.models.keys()}
    start_time = time.time()

    try:
        with sd.InputStream(
            device=device_idx,
            channels=1,
            samplerate=sample_rate,
            blocksize=chunk_size,
            dtype=np.int16
        ) as stream:

            while True:
                # Check duration
                if duration > 0 and (time.time() - start_time) > duration:
                    break

                # Read audio chunk
                audio_data, overflowed = stream.read(chunk_size)

                if overflowed:
                    logger.warning("⚠️  Audio buffer overflow - some data lost")

                # Convert to the format OpenWakeWord expects
                audio_data = audio_data.flatten()

                # Run prediction
                predictions = oww_model.predict(audio_data)

                # Check each model's predictions
                for model_name, score in predictions.items():
                    if score > threshold:
                        detection_count[model_name] += 1
                        elapsed = time.time() - start_time
                        logger.info(
                            f"🔔 DETECTED: '{model_name}' "
                            f"(score: {score:.3f}) at {elapsed:.1f}s"
                        )

    except KeyboardInterrupt:
        logger.info("\n⏹️  Stopped by user")

    except Exception as e:
        logger.error(f"❌ Error during detection: {e}")
        raise

    finally:
        # Print summary
        elapsed = time.time() - start_time
        logger.info("="*60)
        logger.info(f"📊 Detection Summary ({elapsed:.1f}s total)")
        logger.info("="*60)

        if any(detection_count.values()):
            for model_name, count in detection_count.items():
                if count > 0:
                    logger.info(f"   '{model_name}': {count} detections")
        else:
            logger.info("   No wakewords detected")

        logger.info("="*60)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Test wakeword detection with EMEET device")
    parser.add_argument(
        "--model",
        type=str,
        help="Path to custom trained model (e.g., models/hey_saga.onnx)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="How long to listen in seconds (default: 60)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Detection threshold 0.0-1.0 (default: 0.5)"
    )
    args = parser.parse_args()

    logger.info("🎵 OpenWakeWord Detection Demo")
    logger.info("="*60)

    # Find EMEET device
    device_idx = find_emeet_input_device()
    if device_idx is None:
        logger.error("Please connect the EMEET device and try again")
        return 1

    # If custom model specified, use only that
    if args.model:
        model_path = Path(args.model)
        if not model_path.exists():
            logger.error(f"❌ Model not found: {args.model}")
            return 1

        logger.info("")
        logger.info(f"📦 Using custom model: {args.model}")
        logger.info(f"   Model name: {model_path.stem}")
        logger.info("")
        logger.info("💡 Try saying:")
        logger.info(f"   • '{model_path.stem.replace('_', ' ')}'")
        logger.info("")

        run_wakeword_detection(
            device_idx,
            duration=args.duration,
            threshold=args.threshold,
            custom_model_path=str(model_path)
        )
    else:
        # List available models
        logger.info("")
        models = list_available_models()

        if not models:
            logger.error("❌ No models available. OpenWakeWord may not be properly installed.")
            return 1

        # Run detection
        logger.info("")
        logger.info("💡 Try saying:")
        for model in models:
            logger.info(f"   • '{model.replace('_', ' ')}'")
        logger.info("")

        run_wakeword_detection(
            device_idx,
            duration=args.duration,
            threshold=args.threshold
        )

    logger.info("")
    logger.info("✅ Demo complete!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
