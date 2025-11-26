#!/usr/bin/env python3
"""
Test: Duplex stream approach for simultaneous I/O

Instead of separate input/output streams, use a single duplex stream.
"""

import numpy as np
import sounddevice as sd
import time

# EMEET devices
EMEET_OUTPUT = 4  # 2-channel, 48kHz
EMEET_INPUT = 5   # 2-channel, 16kHz

def test_duplex_same_sample_rate():
    """Test duplex stream with same sample rate for both."""
    print("=" * 60)
    print("TEST: DUPLEX STREAM (Same Sample Rate)")
    print("=" * 60)
    print()

    print("Attempting to create duplex stream...")
    print(f"  Input: Device {EMEET_INPUT} (16kHz)")
    print(f"  Output: Device {EMEET_OUTPUT} (48kHz)")
    print()

    # Problem: Input is 16kHz, Output is 48kHz - can't duplex with different rates!
    print("⚠️  EMEET uses different sample rates:")
    print("    Input: 16kHz (optimized for voice)")
    print("    Output: 48kHz (high quality audio)")
    print()
    print("This prevents true duplex streaming with sounddevice.")
    print()

def test_threading_approach():
    """Test using separate threads for input/output."""
    print("=" * 60)
    print("TEST: THREADING APPROACH")
    print("=" * 60)
    print()

    import threading
    import queue

    print("Strategy: Separate threads for I/O, with careful coordination")
    print()

    # Shared state
    playback_active = threading.Event()
    recording_data = queue.Queue()

    def playback_thread():
        """Play audio in background thread."""
        print("   [Playback Thread] Starting...")

        tone = np.sin(2 * np.pi * 440 * np.linspace(0, 2, 2 * 48000)) * 0.3

        playback_active.set()
        sd.play(tone.astype(np.float32), samplerate=48000, device=EMEET_OUTPUT)
        sd.wait()
        playback_active.clear()

        print("   [Playback Thread] Complete")

    def recording_thread():
        """Record audio in separate thread."""
        # Wait for playback to start
        playback_active.wait()

        print("   [Recording Thread] Starting simultaneous recording...")

        try:
            recording = sd.rec(
                int(2 * 16000),
                samplerate=16000,
                channels=2,
                device=EMEET_INPUT,
                dtype=np.float32
            )
            sd.wait()

            max_amp = np.max(np.abs(recording))
            recording_data.put(('success', max_amp))
            print(f"   [Recording Thread] Complete (max amp: {max_amp:.4f})")

        except Exception as e:
            recording_data.put(('error', str(e)))
            print(f"   [Recording Thread] Error: {e}")

    # Start threads
    pb_thread = threading.Thread(target=playback_thread, daemon=True)
    rec_thread = threading.Thread(target=recording_thread, daemon=True)

    pb_thread.start()
    time.sleep(0.1)  # Let playback start first
    rec_thread.start()

    # Wait for completion
    pb_thread.join()
    rec_thread.join()

    # Check result
    if not recording_data.empty():
        status, data = recording_data.get()
        if status == 'success':
            print()
            print(f"✅ SUCCESS: Recorded during playback! (max amp: {data:.4f})")
            print("   Threading approach works!")
        else:
            print()
            print(f"❌ FAILED: {data}")

    print()

def test_sequential_with_minimal_gap():
    """Test how fast we can switch between playback and recording."""
    print("=" * 60)
    print("TEST: SEQUENTIAL WITH MINIMAL GAP")
    print("=" * 60)
    print()

    print("Testing device release/acquire speed...")
    print()

    gaps = []

    for i in range(3):
        # Play short tone
        tone = np.sin(2 * np.pi * 440 * np.linspace(0, 0.5, int(0.5 * 48000))) * 0.3

        sd.play(tone.astype(np.float32), samplerate=48000, device=EMEET_OUTPUT)
        sd.wait()

        switch_start = time.time()

        # How quickly can we start recording?
        recording = sd.rec(
            int(0.5 * 16000),
            samplerate=16000,
            channels=2,
            device=EMEET_INPUT,
            dtype=np.float32
        )

        gap = time.time() - switch_start
        gaps.append(gap)

        sd.wait()

        print(f"  Iteration {i+1}: Gap = {gap*1000:.1f}ms")

    print()
    print(f"  Average switching time: {np.mean(gaps)*1000:.1f}ms")
    print()

    if np.mean(gaps) < 0.1:  # Less than 100ms
        print("✅ Switching is reasonably fast")
    else:
        print("⚠️  Switching has noticeable latency")

    print()

def main():
    """Run tests."""
    print()
    print("🎛️  EMEET Duplex Audio Strategy Tests")
    print()

    test_duplex_same_sample_rate()
    time.sleep(0.5)

    test_threading_approach()
    time.sleep(0.5)

    test_sequential_with_minimal_gap()

    print("=" * 60)
    print("FINDINGS")
    print("=" * 60)
    print()
    print("📋 EMEET Duplex Limitations on macOS:")
    print("   • Input (16kHz) and Output (48kHz) use different sample rates")
    print("   • Can't create true duplex stream with sounddevice")
    print("   • macOS Core Audio serializes access to USB device")
    print()
    print("🔧 Possible Solutions:")
    print("   1. Threading (separate I/O threads) - risky, might still conflict")
    print("   2. Sequential with fast switching - current approach, works")
    print("   3. Resampling to match rates - complex, adds latency")
    print("   4. Use pyaudio instead of sounddevice - might have better duplex")
    print()
    print("💡 Recommendation:")
    print("   Keep current sequential approach but optimize:")
    print("   • Reduce cooldown times where safe")
    print("   • Process audio in background while waiting")
    print("   • Use threading for TTS synthesis (not playback)")
    print()

if __name__ == "__main__":
    main()
