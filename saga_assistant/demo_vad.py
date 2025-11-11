#!/usr/bin/env python3
"""Demo script for Voice Activity Detection (VAD) using Silero VAD.

Tests dynamic voice detection to replace fixed-duration recording.
"""

import logging
import sys
import time
import json
from pathlib import Path
from collections import deque
from datetime import datetime, timezone

import numpy as np
import sounddevice as sd
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
EMEET_DEVICE_NAME = "EMEET"
SAMPLE_RATE = 16000  # Silero VAD requires 8kHz or 16kHz
# Silero VAD requires exactly 512 samples (32ms) at 16kHz per chunk
# Model builds confidence over multiple chunks
CHUNK_SIZE = 512  # 32ms chunks at 16kHz
CHUNK_DURATION_MS = int(CHUNK_SIZE / SAMPLE_RATE * 1000)  # 32ms

# VAD parameters
SPEECH_THRESHOLD = 0.5  # Confidence threshold for speech detection
MIN_SPEECH_DURATION_MS = 250  # Minimum speech duration to start recording
MIN_SILENCE_DURATION_MS = 700  # Silence duration to stop recording
MAX_RECORDING_DURATION_S = 10  # Maximum recording length (safety)


def update_task_status(
    task_name: str,
    status: str,
    progress_percent: int = None,
    current_step: str = None,
    message: str = None,
    needs_attention: bool = False,
    status_file: Path = Path.home() / '.claude-monitor' / 'home_assistant.json'
):
    """Update Claude task monitoring status file."""
    # Ensure directory exists
    status_file.parent.mkdir(parents=True, exist_ok=True)

    data = {
        'task_name': task_name,
        'status': status,
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    if progress_percent is not None:
        data['progress_percent'] = progress_percent
    if current_step:
        data['current_step'] = current_step
    if message:
        data['message'] = message
    if needs_attention:
        data['needs_attention'] = needs_attention

    with open(status_file, 'w') as f:
        json.dump(data, f, indent=2)


class VoiceActivityDetector:
    """Voice Activity Detector using Silero VAD."""

    def __init__(self, sample_rate: int = 16000, threshold: float = 0.5):
        """Initialize VAD.

        Args:
            sample_rate: Audio sample rate (8000 or 16000)
            threshold: Speech confidence threshold (0.0-1.0)
        """
        self.sample_rate = sample_rate
        self.threshold = threshold

        logger.info("🔊 Loading Silero VAD model...")

        # Load Silero VAD model
        model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )

        self.model = model
        self.get_speech_timestamps = utils[0]
        self.save_audio = utils[1]
        self.read_audio = utils[2]
        self.VADIterator = utils[3]
        self.collect_chunks = utils[4]

        # Create VAD iterator for streaming
        self.vad_iterator = self.VADIterator(model, threshold=threshold)

        logger.info(f"   ✅ Silero VAD loaded (threshold={threshold})")

    def is_speech(self, audio_chunk: np.ndarray) -> float:
        """Check if audio chunk contains speech.

        Args:
            audio_chunk: Audio data (int16)

        Returns:
            Speech confidence (0.0-1.0)
        """
        # Convert int16 to float32 [-1, 1]
        audio_float = audio_chunk.astype(np.float32) / 32768.0

        # Convert to torch tensor
        audio_tensor = torch.from_numpy(audio_float)

        # Get speech probability
        speech_dict = self.vad_iterator(audio_tensor, return_seconds=False)

        if speech_dict:
            return speech_dict.get('speech_prob', 0.0)

        return 0.0

    def reset(self):
        """Reset VAD state."""
        self.vad_iterator.reset_states()


def find_emeet_device() -> int:
    """Find EMEET audio input device.

    Returns:
        Device index

    Raises:
        RuntimeError: If device not found
    """
    devices = sd.query_devices()

    for idx, device in enumerate(devices):
        if EMEET_DEVICE_NAME.lower() in device['name'].lower():
            if device['max_input_channels'] > 0:
                return idx

    raise RuntimeError(f"EMEET audio device not found")


def record_with_vad(
    device_idx: int,
    vad: VoiceActivityDetector,
    min_speech_ms: int = 250,
    min_silence_ms: int = 700,
    max_duration_s: int = 10
) -> np.ndarray:
    """Record audio with dynamic VAD-based stopping.

    Args:
        device_idx: Audio device index
        vad: Voice activity detector
        min_speech_ms: Minimum speech duration to start recording
        min_silence_ms: Silence duration to stop recording
        max_duration_s: Maximum recording duration (safety)

    Returns:
        Recorded audio as numpy array
    """
    logger.info("🎤 Listening... (speak when ready)")

    vad.reset()

    # State tracking
    chunks_since_speech = 0
    chunks_since_silence = 0
    is_recording = False
    audio_buffer = []
    pre_speech_buffer = deque(maxlen=10)  # Keep recent chunks before speech

    chunks_per_speech_check = int(min_speech_ms / CHUNK_DURATION_MS)
    chunks_per_silence_check = int(min_silence_ms / CHUNK_DURATION_MS)
    max_chunks = int(max_duration_s * 1000 / CHUNK_DURATION_MS)

    chunk_count = 0
    start_time = None

    try:
        with sd.InputStream(
            device=device_idx,
            channels=1,
            samplerate=SAMPLE_RATE,
            dtype='int16',
            blocksize=CHUNK_SIZE
        ) as stream:

            while chunk_count < max_chunks:
                # Read audio chunk
                audio_chunk, _ = stream.read(CHUNK_SIZE)
                audio_chunk = audio_chunk.flatten()
                chunk_count += 1

                # Check for speech
                speech_prob = vad.is_speech(audio_chunk)

                if speech_prob >= vad.threshold:
                    # Speech detected
                    chunks_since_speech += 1
                    chunks_since_silence = 0

                    if not is_recording:
                        if chunks_since_speech >= chunks_per_speech_check:
                            # Start recording
                            logger.info("   🔴 Speech detected, recording...")
                            is_recording = True
                            start_time = time.time()

                            # Add pre-speech buffer
                            audio_buffer.extend(pre_speech_buffer)
                            audio_buffer.append(audio_chunk)
                    else:
                        # Continue recording
                        audio_buffer.append(audio_chunk)

                else:
                    # Silence detected
                    chunks_since_silence += 1
                    chunks_since_speech = 0

                    if is_recording:
                        # Still recording, add chunk
                        audio_buffer.append(audio_chunk)

                        if chunks_since_silence >= chunks_per_silence_check:
                            # Enough silence, stop recording
                            duration = time.time() - start_time
                            logger.info(f"   ⏹️  Recording complete ({duration:.1f}s)")
                            break
                    else:
                        # Not recording, add to pre-speech buffer
                        pre_speech_buffer.append(audio_chunk)

            else:
                # Max duration reached
                logger.warning(f"   ⚠️  Max duration reached ({max_duration_s}s)")

    except KeyboardInterrupt:
        logger.info("\n   ⏹️  Recording interrupted")

    # Convert to numpy array
    if audio_buffer:
        audio_array = np.concatenate(audio_buffer)
        logger.info(f"   📊 Recorded {len(audio_array)} samples ({len(audio_array)/SAMPLE_RATE:.2f}s)")
        return audio_array
    else:
        logger.warning("   ⚠️  No audio recorded")
        return np.array([], dtype=np.int16)


def demo_continuous_monitoring(device_idx: int, vad: VoiceActivityDetector):
    """Demo continuous speech monitoring (visualization mode).

    Args:
        device_idx: Audio device index
        vad: Voice activity detector
    """
    logger.info("\n" + "="*60)
    logger.info("🎤 Continuous Speech Monitoring")
    logger.info("   Speak to see real-time speech detection")
    logger.info("   Press Ctrl+C to stop")
    logger.info("="*60 + "\n")

    vad.reset()

    try:
        with sd.InputStream(
            device=device_idx,
            channels=1,
            samplerate=SAMPLE_RATE,
            dtype='int16',
            blocksize=CHUNK_SIZE
        ) as stream:

            while True:
                # Read audio chunk
                audio_chunk, _ = stream.read(CHUNK_SIZE)
                audio_chunk = audio_chunk.flatten()

                # Check for speech
                speech_prob = vad.is_speech(audio_chunk)

                # Visual indicator
                if speech_prob >= vad.threshold:
                    bar_length = int(speech_prob * 40)
                    bar = "█" * bar_length
                    print(f"\r🗣️  Speech: {bar:<40} {speech_prob:.2f}", end="", flush=True)
                else:
                    bar_length = int(speech_prob * 40)
                    bar = "░" * bar_length
                    print(f"\r🔇 Silence: {bar:<40} {speech_prob:.2f}", end="", flush=True)

    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped\n")


def main():
    """Run VAD demo."""
    update_task_status(
        task_name="Phase 4: VAD Demo Testing",
        status="in_progress",
        progress_percent=0,
        current_step="Starting VAD demo",
        message="Testing dynamic voice activity detection"
    )

    print("\n" + "="*60)
    print("  🎙️  Voice Activity Detection Demo")
    print("="*60 + "\n")

    try:
        # Find audio device
        logger.info("🔍 Looking for EMEET audio device...")
        update_task_status(
            task_name="Phase 4: VAD Demo Testing",
            status="in_progress",
            progress_percent=10,
            current_step="Finding audio device"
        )
        device_idx = find_emeet_device()
        logger.info(f"   ✅ Found device: {sd.query_devices(device_idx)['name']}")

        # Initialize VAD
        update_task_status(
            task_name="Phase 4: VAD Demo Testing",
            status="in_progress",
            progress_percent=30,
            current_step="Loading Silero VAD model"
        )
        vad = VoiceActivityDetector(
            sample_rate=SAMPLE_RATE,
            threshold=SPEECH_THRESHOLD
        )

        # Interactive menu
        update_task_status(
            task_name="Phase 4: VAD Demo Testing",
            status="in_progress",
            progress_percent=50,
            current_step="Ready for testing",
            message="VAD loaded and ready. Waiting for user selection."
        )

        print("\n" + "="*60)
        print("  Choose demo mode:")
        print("="*60)
        print("\n  1. Continuous monitoring (visualization)")
        print("  2. VAD-based recording (single utterance)")
        print("  3. Multiple recordings with VAD")
        print("  0. Exit\n")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            update_task_status(
                task_name="Phase 4: VAD Demo Testing",
                status="in_progress",
                progress_percent=60,
                current_step="Running continuous monitoring",
                message="Real-time speech visualization active"
            )
            demo_continuous_monitoring(device_idx, vad)

        elif choice == "2":
            update_task_status(
                task_name="Phase 4: VAD Demo Testing",
                status="in_progress",
                progress_percent=60,
                current_step="Testing single VAD recording",
                message="Recording single utterance with VAD"
            )
            print("\n" + "="*60)
            print("  Single VAD Recording")
            print("="*60 + "\n")

            audio = record_with_vad(
                device_idx,
                vad,
                min_speech_ms=MIN_SPEECH_DURATION_MS,
                min_silence_ms=MIN_SILENCE_DURATION_MS,
                max_duration_s=MAX_RECORDING_DURATION_S
            )

            if len(audio) > 0:
                # Save to file
                output_file = Path(__file__).parent / "test_vad_recording.wav"
                import scipy.io.wavfile as wav
                wav.write(output_file, SAMPLE_RATE, audio)
                logger.info(f"   💾 Saved to: {output_file}")

        elif choice == "3":
            print("\n" + "="*60)
            print("  Multiple VAD Recordings")
            print("  Press Ctrl+C to stop")
            print("="*60 + "\n")

            recording_num = 1
            try:
                while True:
                    print(f"\n--- Recording {recording_num} ---")
                    audio = record_with_vad(
                        device_idx,
                        vad,
                        min_speech_ms=MIN_SPEECH_DURATION_MS,
                        min_silence_ms=MIN_SILENCE_DURATION_MS,
                        max_duration_s=MAX_RECORDING_DURATION_S
                    )

                    if len(audio) > 0:
                        duration = len(audio) / SAMPLE_RATE
                        print(f"✅ Recorded {duration:.2f}s of audio")

                    recording_num += 1
                    time.sleep(0.5)

            except KeyboardInterrupt:
                print("\n\n⏹️  Stopped\n")

        elif choice == "0":
            print("\nExiting...\n")
            update_task_status(
                task_name="Phase 4: VAD Demo Testing",
                status="completed",
                progress_percent=100,
                message="VAD demo completed successfully"
            )

        else:
            print("\n❌ Invalid choice\n")
            update_task_status(
                task_name="Phase 4: VAD Demo Testing",
                status="completed",
                progress_percent=100,
                message="VAD demo exited"
            )

    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"\n❌ Error: {e}\n")
        update_task_status(
            task_name="Phase 4: VAD Demo Testing",
            status="error",
            current_step="Error occurred",
            message=f"VAD demo failed: {str(e)}",
            needs_attention=True
        )
        return 1

    update_task_status(
        task_name="Phase 4: VAD Demo Testing",
        status="completed",
        progress_percent=100,
        message="VAD demo session complete"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
