#!/usr/bin/env python3
"""Demo script for Voice Activity Detection (VAD) using WebRTC VAD.

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
import webrtcvad
import scipy.io.wavfile as wav

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
EMEET_DEVICE_NAME = "EMEET"
SAMPLE_RATE = 16000  # WebRTC VAD supports 8kHz, 16kHz, 32kHz, 48kHz
# WebRTC VAD accepts 10, 20, or 30ms frames
FRAME_DURATION_MS = 30
CHUNK_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)  # 480 samples

# VAD parameters
VAD_MODE = 2  # Aggressiveness: 0 (least) to 3 (most). 2 is balanced.
MIN_SPEECH_CHUNKS = 8  # Minimum speech chunks to start recording (~240ms)
MIN_SILENCE_CHUNKS = 23  # Silence chunks to stop recording (~700ms)
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
    """Voice Activity Detector using WebRTC VAD."""

    def __init__(self, mode: int = 2):
        """Initialize VAD.

        Args:
            mode: Aggressiveness mode 0-3 (0=least, 3=most aggressive)
        """
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(mode)
        self.mode = mode

        logger.info(f"🔊 WebRTC VAD loaded (mode={mode})")

    def is_speech(self, audio_chunk: np.ndarray, sample_rate: int) -> bool:
        """Check if audio chunk contains speech.

        Args:
            audio_chunk: Audio data (int16)
            sample_rate: Sample rate (8000, 16000, 32000, or 48000)

        Returns:
            True if speech detected
        """
        # Convert to bytes for WebRTC VAD
        audio_bytes = audio_chunk.tobytes()

        # Get speech detection
        try:
            return self.vad.is_speech(audio_bytes, sample_rate)
        except Exception as e:
            logger.warning(f"VAD error: {e}")
            return False


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
    min_speech_chunks: int = 8,
    min_silence_chunks: int = 23,
    max_duration_s: int = 10
) -> np.ndarray:
    """Record audio with dynamic VAD-based stopping.

    Args:
        device_idx: Audio device index
        vad: Voice activity detector
        min_speech_chunks: Minimum speech chunks to start recording
        min_silence_chunks: Silence chunks to stop recording
        max_duration_s: Maximum recording duration (safety)

    Returns:
        Recorded audio as numpy array
    """
    logger.info("🎤 Listening... (speak when ready)")

    # State tracking
    speech_chunk_count = 0
    silence_chunk_count = 0
    is_recording = False
    audio_buffer = []
    pre_speech_buffer = deque(maxlen=10)  # Keep recent chunks before speech

    max_chunks = int(max_duration_s * 1000 / FRAME_DURATION_MS)
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
                audio_chunk, overflowed = stream.read(CHUNK_SIZE)
                if overflowed:
                    logger.warning("⚠️  Audio buffer overflow")

                audio_chunk = audio_chunk.flatten()
                chunk_count += 1

                # Check for speech
                is_speech = vad.is_speech(audio_chunk, SAMPLE_RATE)

                if is_speech:
                    # Speech detected
                    speech_chunk_count += 1
                    silence_chunk_count = 0

                    if not is_recording:
                        if speech_chunk_count >= min_speech_chunks:
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
                    silence_chunk_count += 1
                    speech_chunk_count = 0

                    if is_recording:
                        # Still recording, add chunk
                        audio_buffer.append(audio_chunk)

                        if silence_chunk_count >= min_silence_chunks:
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

    try:
        with sd.InputStream(
            device=device_idx,
            channels=1,
            samplerate=SAMPLE_RATE,
            dtype='int16',
            blocksize=CHUNK_SIZE
        ) as stream:

            speech_count = 0

            while True:
                # Read audio chunk
                audio_chunk, _ = stream.read(CHUNK_SIZE)
                audio_chunk = audio_chunk.flatten()

                # Check for speech
                is_speech = vad.is_speech(audio_chunk, SAMPLE_RATE)

                # Track consecutive speech
                if is_speech:
                    speech_count += 1
                else:
                    speech_count = 0

                # Visual indicator
                max_level = np.max(np.abs(audio_chunk))
                level_bar = "█" * min(int(max_level / 1000), 20)
                speech_bar = "█" * min(speech_count, 20)

                if speech_count > 3:
                    print(f"\r🗣️  Speech: {speech_bar:<20} | Level: {max_level:5d} {level_bar:<20}", end="", flush=True)
                else:
                    print(f"\r🔇 Silence: {speech_bar:<20} | Level: {max_level:5d} {level_bar:<20}", end="", flush=True)

    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped\n")


def main():
    """Run VAD demo."""
    update_task_status(
        task_name="Phase 4: WebRTC VAD Demo Testing",
        status="in_progress",
        progress_percent=0,
        current_step="Starting VAD demo",
        message="Testing dynamic voice activity detection with WebRTC VAD"
    )

    print("\n" + "="*60)
    print("  🎙️  Voice Activity Detection Demo (WebRTC VAD)")
    print("="*60 + "\n")

    try:
        # Find audio device
        logger.info("🔍 Looking for EMEET audio device...")
        update_task_status(
            task_name="Phase 4: WebRTC VAD Demo Testing",
            status="in_progress",
            progress_percent=10,
            current_step="Finding audio device"
        )
        device_idx = find_emeet_device()
        logger.info(f"   ✅ Found device: {sd.query_devices(device_idx)['name']}")

        # Initialize VAD
        update_task_status(
            task_name="Phase 4: WebRTC VAD Demo Testing",
            status="in_progress",
            progress_percent=30,
            current_step="Loading WebRTC VAD"
        )
        vad = VoiceActivityDetector(mode=VAD_MODE)

        # Interactive menu
        update_task_status(
            task_name="Phase 4: WebRTC VAD Demo Testing",
            status="in_progress",
            progress_percent=50,
            current_step="Ready for testing",
            message="WebRTC VAD loaded and ready. Waiting for user selection."
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
                task_name="Phase 4: WebRTC VAD Demo Testing",
                status="in_progress",
                progress_percent=60,
                current_step="Running continuous monitoring",
                message="Real-time speech visualization active"
            )
            demo_continuous_monitoring(device_idx, vad)

        elif choice == "2":
            update_task_status(
                task_name="Phase 4: WebRTC VAD Demo Testing",
                status="in_progress",
                progress_percent=60,
                current_step="Testing single VAD recording",
                message="Recording single utterance with WebRTC VAD"
            )
            print("\n" + "="*60)
            print("  Single VAD Recording")
            print("="*60 + "\n")

            audio = record_with_vad(
                device_idx,
                vad,
                min_speech_chunks=MIN_SPEECH_CHUNKS,
                min_silence_chunks=MIN_SILENCE_CHUNKS,
                max_duration_s=MAX_RECORDING_DURATION_S
            )

            if len(audio) > 0:
                # Save to file
                output_file = Path(__file__).parent / "test_vad_recording.wav"
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
                        min_speech_chunks=MIN_SPEECH_CHUNKS,
                        min_silence_chunks=MIN_SILENCE_CHUNKS,
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
                task_name="Phase 4: WebRTC VAD Demo Testing",
                status="completed",
                progress_percent=100,
                message="VAD demo completed successfully"
            )

        else:
            print("\n❌ Invalid choice\n")
            update_task_status(
                task_name="Phase 4: WebRTC VAD Demo Testing",
                status="completed",
                progress_percent=100,
                message="VAD demo exited"
            )

    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"\n❌ Error: {e}\n")
        update_task_status(
            task_name="Phase 4: WebRTC VAD Demo Testing",
            status="error",
            current_step="Error occurred",
            message=f"VAD demo failed: {str(e)}",
            needs_attention=True
        )
        return 1

    update_task_status(
        task_name="Phase 4: WebRTC VAD Demo Testing",
        status="completed",
        progress_percent=100,
        message="WebRTC VAD demo session complete"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
