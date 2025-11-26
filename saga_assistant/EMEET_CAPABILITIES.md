# EMEET OfficeCore M0 Plus - Capabilities Analysis

**Device:** EMEET OfficeCore M0 Plus
**Date:** 2025-11-24
**Question:** Are we making good use of EMEET's capabilities?
**Answer:** Not fully - significant optimization opportunities exist!

## Hardware Capabilities

### Multi-Microphone Array
- **4 microphones** arranged for 360° omnidirectional pickup
- **6-meter pickup range** - can hear across a room
- **Built-in DSP**: Beamforming, echo cancellation, noise reduction, AGC
- **VoiceIA Technology**: AI-enhanced voice pickup

### USB Audio Interface
- **Input**: 2-channel stereo @ 16kHz (voice-optimized)
- **Output**: 2-channel stereo @ 48kHz (high-quality audio)
- **Latency**: 7.25ms input, 3.4ms output (very low!)
- **Full-duplex capable**: Separate input/output devices

## Current Utilization

### What We're Using ❌
- ❌ Mono input (ignoring stereo/spatial data from 4-mic array)
- ❌ Blocking I/O (`sd.wait()` freezes all processing)
- ❌ Software-only VAD (not leveraging hardware DSP)
- ❌ Sequential operation (play then listen, never simultaneous)
- ✅ Low-latency output (but not taking advantage of it)

### What We're Missing
1. **Nonblocking audio** - Can't interrupt TTS, can't overlap operations
2. **Hardware echo cancellation** - Should enable barge-in during TTS
3. **Stereo/spatial audio** - Throwing away directional information
4. **Full-duplex operation** - Not using simultaneous I/O capability

## Test Results

### Threading Approach ✅ SUCCESS

**Test**: Play audio in one thread, record in another thread simultaneously

**Result**:
```
✅ Recording during playback works!
   Max amplitude: 0.0044 (quiet, suggesting echo cancellation active)
```

**Finding**: Threading enables simultaneous I/O despite device serialization

### Sequential Switching Speed ✅ FAST

**Test**: Measure time to switch from playback to recording

**Result**:
```
Average switching time: 72ms
```

**Finding**: Device handoff is reasonably fast for sequential operation

### Duplex Stream ❌ NOT POSSIBLE

**Test**: Create single duplex stream with simultaneous I/O

**Result**: Blocked by different sample rates (16kHz input, 48kHz output)

## Echo Cancellation Evidence

The low recording amplitude (0.0044) during simultaneous playback suggests:

1. **Hardware echo cancellation is active** ✅
   - EMEET's DSP is removing playback from microphone input
   - This is exactly what we need for barge-in!

2. **Or**: Perfect timing coincidence (unlikely)

3. **Or**: No speech during test (possible but we got *some* signal)

**Conclusion**: Hardware EC appears to be working!

## Optimization Opportunities

### 1. Nonblocking TTS Playback (HIGH PRIORITY)

**Current**:
```python
sd.play(audio, samplerate=48000, device=output)
sd.wait()  # ⏸️ Blocks everything
```

**Improved**:
```python
def speak_nonblocking(self, text: str):
    def play_thread():
        audio = self.synthesize(text)
        sd.play(audio, samplerate=48000, device=output, blocking=False)
        # Return immediately - continue wakeword detection!

    threading.Thread(target=play_thread, daemon=True).start()
```

**Benefits**:
- Enable interruptions ("Hey Saga, stop!")
- Continue wakeword detection during TTS
- Overlapping operations (timer sound while speaking)
- More natural, conversational feel

**Risks**:
- Need to prevent overlapping TTS (queue or cancel)
- State management complexity
- Potential for audio device contention

### 2. Barge-in During TTS (MEDIUM PRIORITY)

**Concept**: Detect wakeword while Saga is speaking

**Requirements**:
1. ✅ Nonblocking playback (from #1)
2. ✅ Echo cancellation (hardware, appears active)
3. ⚠️  Wakeword model robustness (might false-trigger on TTS)

**Implementation**:
```python
# Play TTS in background
self.speak_nonblocking("Here's a long weather forecast...")

# Meanwhile, continue wakeword detection loop
while tts_playing:
    if wakeword_detected():
        cancel_tts()
        process_interruption()
```

**Challenges**:
- Wakeword model might trigger on Saga's own voice
- Need careful testing and tuning
- May need wakeword threshold adjustment during TTS

### 3. Stereo Input Processing (LOW PRIORITY)

**Current**: Recording mono from 2-channel device

**Improved**: Use both channels for better audio quality

```python
# Record stereo
audio = sd.rec(frames, samplerate=16000, channels=2, device=input)

# Option A: Simple average (current implicit behavior)
mono = audio.mean(axis=1)

# Option B: Smart mixing based on amplitude
left, right = audio[:, 0], audio[:, 1]
# Use channel with better SNR, or adaptive mixing
```

**Benefits**: Marginal improvement, probably not worth complexity

### 4. Reduce Cooldown Times (QUICK WIN)

**Current**:
- Post-TTS cooldown: 1.2 seconds
- Post-sound cooldown: 0.5 seconds

**Analysis**: Sequential switching averages 72ms

**Recommendation**:
- Reduce post-TTS from 1.2s → 0.5s
- Reduce post-sound from 0.5s → 0.2s
- Test wakeword false-trigger rate

**Benefit**: Faster response, still safe

## Recommended Implementation Plan

### Phase 1: Low-Risk Optimizations ✅ DO THIS

1. **Reduce cooldown times** (30 min)
   - Change TTS cooldown: 1.2s → 0.5s
   - Change sound cooldown: 0.5s → 0.2s
   - Test for false wakeword triggers

2. **TTS synthesis in background** (1 hour)
   - Synthesize audio in thread while doing other work
   - Don't block on synthesis, only on playback
   - Reduce perceived latency

### Phase 2: Nonblocking Playback 🔬 EXPERIMENT

1. **Simple nonblocking TTS** (2 hours)
   - Implement threading playback
   - Add state management (prevent overlaps)
   - Test basic functionality

2. **Test echo cancellation** (1 hour)
   - Play TTS, try to trigger wakeword manually
   - Measure false-positive rate
   - Tune wakeword threshold if needed

3. **Add interruption detection** (2 hours)
   - Detect wakeword during TTS
   - Cancel playback gracefully
   - Handle new command

### Phase 3: Advanced Features 🚀 FUTURE

1. **Multi-channel beamforming** (8+ hours)
   - Research pyroomacoustics or similar
   - Implement directional audio processing
   - Test in real environment

2. **Direction-aware responses** (4 hours)
   - Determine speaker direction
   - Orient responses or report direction
   - "The person on your left asked..."

## Code Examples

### Nonblocking TTS (Minimal Implementation)

```python
import threading
from queue import Queue

class SagaAssistant:
    def __init__(self):
        # ... existing init ...
        self.tts_queue = Queue()
        self.tts_playing = False
        self._start_tts_worker()

    def _start_tts_worker(self):
        """Background thread for TTS playback."""
        def worker():
            while True:
                text = self.tts_queue.get()
                if text is None:  # Shutdown signal
                    break

                self.tts_playing = True

                # Synthesize
                audio_chunks = []
                for chunk in self.tts_voice.synthesize(text):
                    audio_chunks.append(chunk.audio_int16_array)

                if audio_chunks:
                    audio = np.concatenate(audio_chunks)

                    # Play (blocks this thread, not main thread)
                    sd.play(audio, samplerate=self.tts_voice.config.sample_rate,
                           device=self.emeet_output)
                    sd.wait()

                self.tts_playing = False
                time.sleep(0.5)  # Cooldown

        threading.Thread(target=worker, daemon=True).start()

    def speak_nonblocking(self, text: str):
        """Queue TTS without blocking."""
        logger.info(f"🔊 Queuing speech: {text[:50]}...")
        self.tts_queue.put(text)
        # Returns immediately!

    def speak(self, text: str):
        """Blocking TTS (for compatibility)."""
        self.speak_nonblocking(text)

        # Wait for completion
        while self.tts_playing:
            time.sleep(0.1)
```

### Interruption Detection

```python
def listen_for_wakeword(self):
    """Main wakeword detection loop with interruption support."""
    while True:
        # Record chunk
        audio = self.record_chunk(duration=0.1)

        # Check wakeword
        scores = self.wakeword_model.predict(audio)

        if scores['hey_saga'] > WAKEWORD_THRESHOLD:
            # Wakeword detected!

            if self.tts_playing:
                # Interrupt TTS
                logger.info("🛑 Interrupting TTS")
                self.stop_tts()
                time.sleep(0.2)  # Let device settle

            # Process command
            self.handle_command()
```

## Conclusion

**Are we making good use of EMEET capabilities?**

**Current**: ❌ No - we're using it as a basic USB mic/speaker

**Potential**: ✅ Yes - with nonblocking playback and better DSP utilization

**Quick Wins**:
1. Reduce cooldown times (5 min implementation)
2. Background TTS synthesis (30 min)
3. Simple nonblocking playback (2 hours)

**Big Wins**:
1. Barge-in/interruption (enables natural conversation)
2. Overlapping operations (faster, more responsive)
3. Full-duplex operation (maximal hardware utilization)

**Recommendation**: Start with Phase 1 (low-risk optimizations), then cautiously experiment with Phase 2 (nonblocking playback).

---

**Next Steps**:
1. ✅ Reduce cooldowns in `run_assistant.py`
2. Test wakeword false-positive rate with shorter cooldowns
3. Implement background TTS synthesis (non-blocking synthesis, still blocking playback)
4. If successful, progress to nonblocking playback with threading

**Risk Level**: Low → Medium → High as we progress through phases

