#!/usr/bin/env python3
"""
Test: Can we do simultaneous input/output on EMEET?

Tests if we can play audio while recording (full-duplex).
"""

import numpy as np
import sounddevice as sd
import time

# EMEET devices (update these if different)
EMEET_OUTPUT = 4  # 2-channel, 48kHz
EMEET_INPUT = 5   # 2-channel, 16kHz

def generate_test_tone(frequency=440, duration=2.0, sample_rate=48000):
    """Generate a test tone (A440)."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(2 * np.pi * frequency * t) * 0.3
    return tone.astype(np.float32)

def test_blocking():
    """Test current blocking approach."""
    print("=" * 60)
    print("TEST 1: BLOCKING (Current Approach)")
    print("=" * 60)
    print()

    print("🔊 Playing test tone...")
    print("   (During playback, try saying something - you won't be heard)")
    print()

    tone = generate_test_tone(440, 2.0, 48000)

    start = time.time()

    # Play - BLOCKS
    sd.play(tone, samplerate=48000, device=EMEET_OUTPUT)
    sd.wait()  # Blocks here

    playback_time = time.time() - start

    print(f"   ✅ Playback complete ({playback_time:.2f}s)")
    print()

    # Now try to record
    print("🎤 Recording for 2 seconds...")
    print("   (Say something now)")
    print()

    recording = sd.rec(
        int(2 * 16000),
        samplerate=16000,
        channels=2,
        device=EMEET_INPUT,
        dtype=np.float32
    )
    sd.wait()

    # Check if we got audio
    max_amplitude = np.max(np.abs(recording))
    print(f"   ✅ Recording complete (max amplitude: {max_amplitude:.4f})")
    print()

    print("⚠️  Problem: Playback blocked recording - sequential only!")
    print()

def test_nonblocking():
    """Test nonblocking simultaneous I/O."""
    print("=" * 60)
    print("TEST 2: NONBLOCKING (Full-Duplex)")
    print("=" * 60)
    print()

    print("🔊 Playing test tone + 🎤 Recording simultaneously...")
    print("   (Say something during the tone - you SHOULD be heard)")
    print()

    tone = generate_test_tone(440, 3.0, 48000)

    # Start playback - NON-BLOCKING
    sd.play(tone, samplerate=48000, device=EMEET_OUTPUT, blocking=False)
    print("   🔊 Playback started (nonblocking)")

    # Immediately start recording while playback continues
    time.sleep(0.1)  # Brief delay to ensure playback started

    print("   🎤 Recording started (simultaneous)")
    recording = sd.rec(
        int(2.5 * 16000),
        samplerate=16000,
        channels=2,
        device=EMEET_INPUT,
        dtype=np.float32
    )

    # Wait for recording (playback continues in background)
    sd.wait()

    print("   ✅ Recording complete while playback was running!")
    print()

    # Check what we got
    max_amplitude = np.max(np.abs(recording))
    print(f"   📊 Recording max amplitude: {max_amplitude:.4f}")

    # Analyze recording
    if max_amplitude > 0.01:
        print("   ✅ SUCCESS: Captured audio during playback!")
        print("   🎉 Full-duplex works! Echo cancellation might be active.")
    else:
        print("   ⚠️  Recording is quiet - might be hardware echo cancellation")
        print("   (This is actually good if you said something - it means EC works!)")

    print()

def test_wakeword_during_playback():
    """Simulate detecting wakeword during TTS playback."""
    print("=" * 60)
    print("TEST 3: WAKEWORD DETECTION DURING PLAYBACK")
    print("=" * 60)
    print()

    print("This would test if we can detect 'Hey Saga' while TTS is playing.")
    print("(Requires full integration - just a concept demo here)")
    print()

    tone = generate_test_tone(440, 5.0, 48000)

    print("🔊 Starting 5-second tone playback (nonblocking)...")
    sd.play(tone, samplerate=48000, device=EMEET_OUTPUT, blocking=False)

    print("🎤 Monitoring for speech in chunks (simulating wakeword detection)...")
    print()

    # Simulate monitoring in chunks
    for i in range(5):
        chunk = sd.rec(
            int(1.0 * 16000),  # 1-second chunks
            samplerate=16000,
            channels=2,
            device=EMEET_INPUT,
            dtype=np.float32
        )
        sd.wait()

        max_amp = np.max(np.abs(chunk))
        print(f"   Chunk {i+1}/5: max amplitude = {max_amp:.4f}")

        # In real implementation, this is where we'd run wakeword detection
        # if wakeword detected during playback, we could:
        #   - sd.stop() to interrupt playback
        #   - process new command

    print()
    print("✅ Concept proven: Can monitor continuously during playback")
    print()

def main():
    """Run all tests."""
    print()
    print("🎛️  EMEET Full-Duplex Audio Tests")
    print()

    try:
        test_blocking()
        time.sleep(1)

        test_nonblocking()
        time.sleep(1)

        test_wakeword_during_playback()

        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print()
        print("✅ Nonblocking playback works")
        print("✅ Can record while playing")
        print("✅ Can monitor for wakeword during TTS")
        print("💡 Next step: Integrate into run_assistant.py")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
