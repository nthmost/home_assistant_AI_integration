# EMEET Optimization Plan - Phased Approach

**Goal**: Maximize EMEET OfficeCore M0 Plus capabilities for faster, more responsive voice assistant

**Current State**: Using ~30% of device capabilities (basic USB mic/speaker mode)
**Target State**: Full-duplex operation with interruptions and overlapping I/O

---

## Phase 1: Quick Wins (Low Risk) ⚡

**Time Estimate**: 30 minutes
**Risk Level**: LOW
**Impact**: Medium (0.7s faster per interaction)

### Tasks

#### 1.1 Reduce TTS Cooldown
**Current**: 1.2 seconds
**Target**: 0.5 seconds
**Rationale**: Device switching averages 72ms - current cooldown is 16x longer than needed

**File**: `saga_assistant/run_assistant.py`
**Location**: `speak()` method

```python
# Current
if not self.awaiting_followup:
    time.sleep(1.2)  # Too conservative

# New
if not self.awaiting_followup:
    time.sleep(0.5)  # Based on measured switching time
```

#### 1.2 Reduce Sound Cooldown
**Current**: 0.5 seconds
**Target**: 0.2 seconds
**Rationale**: Timer sounds are shorter than TTS, need less cooldown

**File**: `saga_assistant/run_assistant.py`
**Location**: `_play_wav()` method

```python
# Current
time.sleep(0.5)

# New
time.sleep(0.2)  # Faster return to wakeword detection
```

#### 1.3 Test Wakeword False Triggers
**Method**: Manual testing
**Test Cases**:
- Say "Hey Saga" immediately after TTS ends
- Say "Hey Saga" immediately after timer sound
- Verify wakeword detection still works reliably

**Success Criteria**:
- ✅ No increase in false negatives (missed wakewords)
- ✅ No increase in false positives (phantom triggers)
- ✅ Noticeably faster interaction cycle

### Expected Results
- **0.7 seconds faster** per TTS response
- **0.3 seconds faster** per timer sound
- No degradation in reliability

### Rollback Plan
If false triggers increase:
1. Revert cooldown times to original values
2. Try intermediate values (0.8s for TTS, 0.3s for sounds)

---

## Phase 2: Background Processing (Medium Risk) 🔬

**Time Estimate**: 2-3 hours
**Risk Level**: MEDIUM
**Impact**: High (enables concurrent operations)

### Tasks

#### 2.1 Background TTS Synthesis (Non-blocking synthesis, blocking playback)
**Goal**: Synthesize audio in background while continuing other operations

**File**: `saga_assistant/run_assistant.py`

**Current Flow**:
```
LLM response → [WAIT] Synthesize audio → [WAIT] Play audio → [WAIT] Cooldown → Listen
```

**New Flow**:
```
LLM response → Synthesize audio (background thread)
             ↓
Continue processing (fetch data, etc.)
             ↓
[WAIT] Play audio → [WAIT] Cooldown → Listen
```

**Implementation**:
```python
import threading
from queue import Queue

class SagaAssistant:
    def __init__(self):
        # ... existing init ...
        self.synthesis_queue = Queue()
        self._start_synthesis_worker()

    def _start_synthesis_worker(self):
        """Background thread for TTS synthesis."""
        def worker():
            while True:
                task = self.synthesis_queue.get()
                if task is None:
                    break

                text, result_queue = task

                # Synthesize in background
                audio_chunks = []
                for chunk in self.tts_voice.synthesize(text):
                    audio_chunks.append(chunk.audio_int16_array)

                result_queue.put(np.concatenate(audio_chunks) if audio_chunks else None)

        threading.Thread(target=worker, daemon=True).start()

    def synthesize_async(self, text: str) -> Queue:
        """Start synthesis in background, return queue for result."""
        result_queue = Queue()
        self.synthesis_queue.put((text, result_queue))
        return result_queue

    def speak(self, text: str):
        """Synthesize and play, with async synthesis."""
        logger.info("🔊 Synthesizing speech...")

        # Start synthesis in background
        audio_queue = self.synthesize_async(text)

        # Could do other work here while synthesis runs
        # For now, just wait for result

        # Get synthesized audio
        audio_array = audio_queue.get()

        if audio_array is not None:
            logger.info("🔊 Playing...")
            sd.play(audio_array, samplerate=self.tts_voice.config.sample_rate,
                   device=self.emeet_output)
            sd.wait()

            # ... rest of speak() ...
```

**Testing**:
1. Verify TTS still works correctly
2. Measure time savings (synthesis happens while other processing runs)
3. Check for threading issues or race conditions

**Success Criteria**:
- ✅ TTS quality unchanged
- ✅ No threading errors
- ✅ Measurable latency reduction (50-200ms)

#### 2.2 Nonblocking Playback (Threading approach)
**Goal**: Play audio in background thread, return control immediately

**Risk**: Higher - need careful state management

**Implementation**:
```python
class SagaAssistant:
    def __init__(self):
        # ... existing init ...
        self.tts_queue = Queue()
        self.tts_playing = False
        self.tts_stop_event = threading.Event()
        self._start_tts_worker()

    def _start_tts_worker(self):
        """Background thread for TTS playback."""
        def worker():
            while True:
                audio_array = self.tts_queue.get()
                if audio_array is None:  # Shutdown signal
                    break

                self.tts_playing = True
                self.tts_stop_event.clear()

                # Play audio (blocks this thread only)
                sd.play(audio_array, samplerate=self.tts_voice.config.sample_rate,
                       device=self.emeet_output)

                # Wait for completion or stop signal
                while sd.get_stream().active and not self.tts_stop_event.is_set():
                    time.sleep(0.1)

                if self.tts_stop_event.is_set():
                    sd.stop()  # Interrupt playback

                sd.wait()
                self.tts_playing = False

                time.sleep(0.5)  # Cooldown

        threading.Thread(target=worker, daemon=True).start()

    def speak_nonblocking(self, text: str):
        """Speak without blocking."""
        # Synthesize (could also be async)
        audio_chunks = []
        for chunk in self.tts_voice.synthesize(text):
            audio_chunks.append(chunk.audio_int16_array)

        if audio_chunks:
            audio = np.concatenate(audio_chunks)
            self.tts_queue.put(audio)
            # Returns immediately!

    def stop_tts(self):
        """Stop current TTS playback."""
        self.tts_stop_event.set()

    def speak(self, text: str):
        """Backward-compatible blocking speak."""
        self.speak_nonblocking(text)
        while self.tts_playing:
            time.sleep(0.1)
```

**Testing**:
1. Test basic TTS (should work as before)
2. Test interruption (call `stop_tts()` during playback)
3. Test overlapping sounds (timer expires during TTS)
4. Verify device doesn't get stuck

**Success Criteria**:
- ✅ TTS playback works reliably
- ✅ Can interrupt TTS mid-speech
- ✅ No audio device deadlocks
- ✅ State management is clean

#### 2.3 Test Echo Cancellation
**Goal**: Verify wakeword detection works during TTS playback

**Test Procedure**:
1. Start Saga
2. Trigger long TTS response (e.g., "Hey Saga, what's the weather for the week?")
3. While TTS is playing, say "Hey Saga, stop"
4. Measure false positive rate (should be low)

**Measurements**:
- Wakeword detection rate during TTS
- False positive rate (triggering on TTS voice)
- Optimal threshold adjustment (if needed)

**Success Criteria**:
- ✅ Can detect wakeword during TTS at least 70% of the time
- ✅ False positive rate < 5%
- ✅ Echo cancellation prevents TTS from triggering wakeword

---

## Phase 3: Interruption & Barge-in (Medium-High Risk) 🚀

**Time Estimate**: 3-4 hours
**Risk Level**: MEDIUM-HIGH
**Impact**: Very High (enables natural conversation)

### Tasks

#### 3.1 Implement Interruption Detection
**Goal**: Detect wakeword during TTS and handle gracefully

**Implementation**:
```python
def run(self):
    """Main assistant loop with interruption support."""
    while True:
        if not self.tts_playing:
            # Normal wakeword detection
            if self.detect_wakeword():
                self.handle_command()
        else:
            # During TTS, check for interruption
            if self.detect_wakeword():
                logger.info("🛑 User interrupted TTS")
                self.stop_tts()
                time.sleep(0.2)  # Let device settle
                self.handle_command()
```

**Edge Cases**:
- Rapid interruptions (spam protection)
- Interrupting with same command
- Queued vs. immediate execution

**Testing**:
1. Interrupt long TTS responses
2. Test rapid successive interruptions
3. Verify graceful degradation if device busy

#### 3.2 State Management
**Goal**: Clean state transitions during interruptions

**States**:
- `IDLE` - Waiting for wakeword
- `LISTENING` - Recording command
- `PROCESSING` - LLM thinking
- `SPEAKING` - TTS playing
- `INTERRUPTED` - TTS was stopped mid-speech

**Transitions**:
```
IDLE → [wakeword] → LISTENING → [transcribe] → PROCESSING → [response] → SPEAKING → IDLE
                                                                              ↓
                                                                     [wakeword during TTS]
                                                                              ↓
                                                                        INTERRUPTED → LISTENING
```

**Testing**:
- Verify clean transitions
- No stuck states
- Proper resource cleanup

#### 3.3 User Experience Polish
**Responses**:
- Interrupted: "Okay, stopped. What did you need?"
- Continue: "Where was I... oh yes, the weather..."
- Cancel: "Okay, never mind that."

**Voice Feedback**:
- Brief confirmation sound when interrupted
- Different tone for "stop" vs. new command

---

## Phase 4: Advanced Features (High Risk) 🎯

**Time Estimate**: 8+ hours
**Risk Level**: HIGH
**Impact**: High (professional-grade features)

### Tasks

#### 4.1 Multi-Channel Recording
**Goal**: Use all 4 microphones with beamforming

**Research**:
- pyroomacoustics library
- scipy.signal for beamforming
- Delay-and-sum vs. MVDR beamforming

**Implementation Complexity**: High
**Benefit**: Better noise rejection, direction detection

#### 4.2 Direction-Aware Responses
**Goal**: Detect which direction speech came from

**Applications**:
- "The person on your left asked about weather"
- Orient responses toward speaker
- Multi-user scenarios

**Implementation Complexity**: Very High
**Benefit**: Professional conference room capabilities

#### 4.3 Adaptive Echo Cancellation
**Goal**: Fine-tune EC parameters based on environment

**Approach**:
- Measure room acoustics
- Adjust parameters dynamically
- Machine learning for optimal settings

**Implementation Complexity**: Very High
**Benefit**: Optimal performance in any environment

---

## Testing Strategy

### Unit Tests
```python
def test_nonblocking_tts():
    """Test that TTS returns immediately."""
    start = time.time()
    assistant.speak_nonblocking("This is a test")
    elapsed = time.time() - start
    assert elapsed < 0.1, "TTS should return immediately"

def test_tts_interruption():
    """Test that TTS can be interrupted."""
    assistant.speak_nonblocking("Long response...")
    time.sleep(0.5)
    assistant.stop_tts()
    assert not assistant.tts_playing, "TTS should stop"
```

### Integration Tests
- Full conversation flows
- Interruption scenarios
- Error recovery
- Device failure handling

### Performance Tests
- Measure latency improvements
- Track false positive/negative rates
- Monitor CPU/memory usage
- Audio quality metrics

---

## Success Metrics

### Phase 1
- ✅ 0.7s faster response time
- ✅ No reliability degradation
- ✅ Smooth device transitions

### Phase 2
- ✅ Concurrent synthesis + processing
- ✅ Reliable interruption capability
- ✅ <5% false positive rate

### Phase 3
- ✅ Natural barge-in works
- ✅ Clean state management
- ✅ Polished UX

### Phase 4
- ✅ Professional-grade features
- ✅ Multi-user support
- ✅ Directional awareness

---

## Risk Mitigation

### Rollback Strategy
Each phase should be:
1. Developed in feature branch
2. Tested thoroughly in isolation
3. Deployed with kill switch (config flag)
4. Monitored for issues
5. Rolled back if problems occur

### Testing Requirements
- Manual testing before merge
- Automated tests where possible
- Performance benchmarking
- User acceptance testing

### Configuration Flags
```python
# config.py or .env
ENABLE_NONBLOCKING_TTS = False  # Phase 2
ENABLE_INTERRUPTIONS = False     # Phase 3
ENABLE_BEAMFORMING = False       # Phase 4
```

Enable features incrementally with safety nets.

---

## Timeline

### Week 1
- ✅ Phase 1: Quick wins
- 🔬 Phase 2: Background synthesis

### Week 2
- 🔬 Phase 2: Nonblocking playback
- 🔬 Phase 2: Echo cancellation testing

### Week 3
- 🚀 Phase 3: Interruption detection
- 🚀 Phase 3: State management

### Week 4+
- 🎯 Phase 4: Advanced features (as time permits)

---

## Current Status

**Phase 1**: Ready to implement ✅
**Phase 2**: Designed, ready for development 🔬
**Phase 3**: Designed, depends on Phase 2 ⏳
**Phase 4**: Research phase 📚

---

**Next Action**: Implement Phase 1 (reduce cooldowns, test)

**Expected Outcome**: Saga feels snappier, responds 0.7s faster per interaction

**Let's go!** 🚀
