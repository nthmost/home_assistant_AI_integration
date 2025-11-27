# Saga Voice Assistant - Product Requirements Document

**Version:** 1.1
**Last Updated:** November 2025
**Status:** Phase 3 - Conversational Context & Follow-Up Questions (COMPLETE)

---

## Overview

Saga is a 100% LAN-based voice assistant for Home Assistant integration with custom wakeword detection, natural language understanding, and local LLM capabilities.

### Core Design Principles

1. **Privacy First**: All processing happens on LAN - no cloud dependencies after initial setup
2. **Voice Optimized**: Short, conversational responses (1-2 sentences max)
3. **Multi-tiered Intelligence**: Power phrases → Intent parsing → LLM fallback
4. **SF-Specific Features**: Built-in parking & street sweeping awareness

---

## System Architecture

### Hardware Components

| Component | Device | Purpose |
|-----------|--------|---------|
| **Audio I/O** | EMEET OfficeCore M0 Plus | Microphone (16kHz) + Speaker (48kHz) |
| **Processing** | Mac mini M4 | Wakeword, STT, TTS orchestration |
| **LLM Inference** | loki.local (RTX 4080) | Ollama with qwen2.5:7b |
| **Home Automation** | Home Assistant | Device control, state queries |

### Software Stack

| Layer | Technology | Model/Version |
|-------|-----------|---------------|
| **Wakeword Detection** | OpenWakeWord v0.6.0 | `hey_saga_noisy.onnx` (custom trained) |
| **STT** | faster-whisper | `small` model (CPU, int8) |
| **LLM** | Ollama via OpenAI API | qwen2.5:7b on loki.local |
| **TTS** | Piper | en_GB-semaine-medium |
| **VAD** | WebRTC VAD | Mode 2 (balanced) |

---

## Feature Set

### 1. Wakeword Detection ✅

**Status:** Complete (Phase 1)

**Capabilities:**
- Custom "Hey Saga" wakeword trained with noisy tier (competing speech tolerance)
- Threshold: 0.5 confidence
- Post-detection confirmation beep (600Hz → 800Hz, 150ms)
- 3-chunk (~4 second) cooldown to prevent TTS echo triggering

**Performance:**
- Detection latency: <1.3 seconds
- Robust to background noise and conversation
- No false positives from TTS playback

---

### 2. Voice Activity Detection (VAD) ✅

**Status:** Complete (Phase 1)

**Capabilities:**
- Dynamic recording duration based on speech detection
- Pre-speech buffering (600ms) to capture first syllables
- Automatic stop after 700ms of silence
- Maximum recording duration: 10 seconds (safety)

**Parameters:**
- VAD Mode: 2 (balanced aggressiveness)
- Frame duration: 30ms
- Min speech chunks: 3 (~90ms) to start
- Min silence chunks: 23 (~700ms) to stop

**Performance:**
- Successfully captures first syllables (no cutoff)
- Natural stop points in conversational speech
- Handles pauses without premature cutoff

---

### 3. Speech-to-Text (STT) ✅

**Status:** Complete (Phase 1)

**Capabilities:**
- Local transcription via faster-whisper
- VAD-based filtering for cleaner transcription
- Automatic language detection (English default)

**Configuration:**
- Model: `small` (best speed/accuracy balance)
- Beam size: 1 (faster decoding)
- VAD filter: Enabled (min_silence_duration_ms=500)
- Device: CPU (int8 quantization)

**Performance:**
- Transcription latency: ~1 second for typical commands
- High accuracy for conversational English

---

### 4. Response Intelligence (Multi-Tiered)

#### 4.1 Power Phrases ⚡ (Tier 1 - Instant)

**Status:** Complete

**Purpose:** Zero-latency responses for common queries

**Categories:**

1. **Greetings & Courtesy**
   - "hi", "hello", "hey" → "Hello!"
   - "thank you", "thanks" → "You're welcome!"

2. **Time & Date**
   - "what time is it" → `<TIME>` (reads system time)
   - "what's the date" → `<DATE>` (reads system date)

3. **Weather Queries**
   - "what's the weather" → `<WEATHER:now>`
   - "will it rain today" → `<RAIN:today>`
   - "how windy is it" → `<WIND>`
   - Location-aware: "what's the weather in Seattle"

4. **Timers & Reminders**
   - "set a timer for 5 minutes" → Timer creation
   - "how much time left" → Timer status
   - "cancel timer" → Timer cancellation
   - "remind me in 10 minutes to X" → Reminder creation
   - Accepts both digit and word numbers (1-60)

**Response Format:**
```
💬⚡ (0.01s): "Hello!"
```

**Performance:**
- Latency: <10ms (regex matching only)
- No network calls, no LLM inference

---

#### 4.2 Intent Parsing 🧠 (Tier 2 - Structured)

**Status:** Complete (Phase 2)

**Purpose:** Structured command handling for Home Assistant and parking

**Supported Intents:**

##### Home Assistant Intents

| Intent | Patterns | Examples |
|--------|----------|----------|
| `turn_on` | "turn on", "switch on", "enable", "open" | "turn on the TV light" |
| `turn_off` | "turn off", "switch off", "disable", "close" | "turn off the aqua lights" |
| `toggle` | "toggle", "flip", "switch" | "toggle the power strip" |
| `status` | "status", "is", "what's" | "what's the TV light status" |
| `brightness` | "brightness", "dim", "brighten" | "dim the lights" |

**Entity Resolution:**
- Type-based filtering (light, switch, cover, fan, lock)
- Name-based fuzzy matching using device aliases
- Confidence scoring (0.0-1.0)
- Minimum confidence threshold: 0.6

**Device Aliases:**
- TV: ["tv", "television"]
- Aqua: ["aqua", "aquarium", "fish"]
- Strip: ["strip", "power strip"]
- Candelabra: ["candelabra", "candle"]
- Tube: ["tube", "tube lamp"]

**Response Format:**
```
💬🏠 (0.12s): "Okay, I've turned on the TV light."
```

##### Parking Intents 🚗

| Intent | Patterns | Examples |
|--------|----------|----------|
| `save_parking` | "i parked", "my car is", "i moved the car" | "I parked on Valencia" |
| `where_parked` | "where did i park", "where's my car" | "where did I park?" |
| `when_to_move` | "when do i move", "street sweeping" | "when is street sweeping?" |

**Features:**

1. **Natural Language Location Parsing**
   - Supports: "north side of Anza between 7th and 8th ave"
   - Handles: Street names, cross streets, sides (north/south/east/west)
   - Fuzzy matching for street names (handles typos)

2. **SF Street Sweeping Integration**
   - 37,878 records covering 1,453 SF streets
   - Week-of-month calculation (1st, 2nd, 3rd, 4th, 5th)
   - Block-level precision with side-specific schedules
   - Next sweeping lookup (14 days ahead)

3. **TTS Pronunciation Optimization**
   - Abbreviation expansion:
     - St → Street
     - Ave → Avenue
     - Blvd → Boulevard
     - Dr → Drive
     - Rd → Road
     - Ct → Court
     - Ln → Lane
     - Pl → Place
   - Ordinal dates: "December 2nd" not "December 2"
   - Natural formatting: "between X and Y" not "X - Y"

4. **Data Sync**
   - Source: SF DataSF Socrata API
   - Update mechanism: Metadata timestamp comparison
   - Storage: Local JSON cache (15MB)
   - Sync trigger: Home Assistant automation (weekly)

**Response Format:**
```
💬🚗 (0.11s): "Parked on Balboa Street between 7th Avenue and 8th Avenue. Next sweeping: Monday, December 1st 8am-10am"
```

**Known Limitations:**
- ⚠️ **Missing side information handling**: If user doesn't specify side, system doesn't ask for clarification
- ⚠️ **Ambiguous sweeping info**: Different sides may have different schedules
- ⚠️ **No follow-up question capability**: Cannot request missing critical information

---

#### 4.3 LLM Fallback 🤖 (Tier 3 - Conversational)

**Status:** Complete (Phase 1)

**Purpose:** Handle conversational queries, general questions, improv interactions

**Configuration:**
- Model: qwen2.5:7b (Ollama on loki.local)
- Max tokens: 30 (aggressive brevity for voice)
- Temperature: 0.8 (balanced creativity)
- Endpoint: http://loki.local:11434/v1

**System Prompt Highlights:**
```
- RESPONSE LENGTH: 1-2 sentences max (VOICE)
- Personality: Helpful first, playful second
- HOME AUTOMATION: "Done" or confirm (4-6 words)
- WEATHER: Local weather access (zip 94118)
- QUESTIONS: One helpful sentence, STOP
```

**Response Format:**
```
💬🤖 (1.23s): "Sure! The weather is sunny today."
```

**Performance:**
- Latency: 1-3 seconds (network + inference)
- Fallback for unrecognized patterns
- Natural conversation handling

---

### 5. Text-to-Speech (TTS) ✅

**Status:** Complete (Phase 1)

**Capabilities:**
- Local synthesis via Piper
- British English voice (natural, clear)
- Real-time streaming to EMEET speaker

**Configuration:**
- Voice: en_GB-semaine-medium
- Sample rate: 22050 Hz (voice config)
- Output device: EMEET (48kHz resampling)
- Post-speech cooldown: 1.2 seconds (prevents wakeword retrigger)

**Quality:**
- Natural prosody and pacing
- Clear pronunciation with abbreviation expansion
- No robotic artifacts

---

## Response Prioritization Flow

```
User Command
    ↓
┌───────────────────┐
│ Power Phrases     │ → Instant response (⚡)
│ (Regex matching)  │
└───────────────────┘
    ↓ (no match)
┌───────────────────┐
│ Intent Parser     │ → Structured response (🚗/🏠)
│ (Pattern + Entity)│
└───────────────────┘
    ↓ (no match or low confidence)
┌───────────────────┐
│ LLM Fallback      │ → Conversational response (🤖)
│ (qwen2.5:7b)      │
└───────────────────┘
```

**Confidence Thresholds:**
- Power Phrases: Exact match required
- Intent Parser: 0.6 minimum confidence
- LLM Fallback: Always accepts (last resort)

---

## Logging & Observability

### Response Logging Format

All responses use unified format:
```
💬[icon] (time): "response text"
```

**Icons:**
- `💬⚡` = Power phrase
- `💬🚗` = Parking command
- `💬🏠` = Home Assistant command
- `💬🤖` = LLM response

### Execution Flow Logging

```
👂 Listening for 'Hey Saga'...
✅ Wakeword detected! (score: 0.926)
🎤 Recording command (VAD auto-stop)...
   🔴 Speech detected, recording...
   ⏹️  Recording complete (2.4s)
🗣️  Transcribing...
   📝 You said: "turn on the lights"
🔍 Checking for intent command...
   ✅ HA command detected (confidence: 0.85)
   💬🏠 (0.12s): "Okay, I've turned on the TV light."
🔊 Speaking...
   ✅ Speech complete
```

### Task Monitoring

**Claude Monitor Integration:**
- Status file: `~/.claude-monitor/home_assistant.json`
- Updates during: Training, multi-step tasks, long operations
- Fields: task_name, status, progress_percent, current_step, message, needs_attention, updated_at

---

## Configuration Files

### Power Phrases (`saga_assistant/power_phrases.json`)

```json
{
  "greetings": {
    "hi|hello|hey": "Hello!"
  },
  "time": {
    "what time is it|time": "<TIME>"
  },
  "weather": {
    "what'?s? the weather|weather now": "<WEATHER:now>"
  },
  "timers": {
    "how much time|time left|timer status": "<TIMER:check>"
  }
}
```

### Device Aliases (`saga_assistant/intent_parser.py`)

Extensible device mapping for entity resolution.

### Street Sweeping Data (`saga_assistant/data/street_sweeping_sf.json`)

- 37,878 records
- Updated weekly via HA automation
- Metadata: `saga_assistant/data/sync_metadata.json`

---

## Performance Metrics

### Latency Targets

| Component | Target | Actual |
|-----------|--------|--------|
| Wakeword detection | <1.5s | ~1.3s |
| VAD recording | 1-5s | 2-4s (typical) |
| STT transcription | <2s | ~1s |
| Power phrase response | <0.05s | ~0.01s |
| Intent parsing | <0.5s | ~0.1s |
| LLM response | <5s | 1-3s |
| TTS synthesis | <1s | ~0.5s |

### End-to-End Latency

**Power Phrase Flow:**
- Wakeword → Response: ~4-6 seconds

**Intent Flow:**
- Wakeword → Response: ~5-7 seconds

**LLM Flow:**
- Wakeword → Response: ~7-10 seconds

---

## Conversational Follow-Up System

### Overview

Saga implements a sophisticated multi-turn conversation system that detects missing critical information and asks follow-up questions to gather complete data before taking action.

### Core Principle: Bottleneck Pattern

**Never answer with incomplete information.** Saga refuses to provide potentially incorrect answers and instead asks for missing details.

**Example:**
```
❌ BAD: User asks "when do I move?" without saved location
        → Saga: "No street sweeping scheduled" (WRONG - we don't know where!)

✅ GOOD: User asks "when do I move?" without saved location
         → Saga: "I don't know where you parked. Where is your car?"
         → User provides location
         → Saga asks for missing side
         → User provides side
         → Saga: "Street sweeping is Monday, December 1st from 8 AM to 10 AM"
```

### Conversation State Management

**State Variables:**
- `awaiting_followup` (bool): Are we waiting for a follow-up answer?
- `followup_type` (str): What type of follow-up (e.g., "parking_side", "no_parking_saved")
- `followup_data` (dict): Partial data from previous interaction

**Flow:**
1. User command triggers intent requiring information
2. System detects missing critical field
3. Sets `awaiting_followup = True` and stores partial data
4. Asks clarifying question
5. **Skips wakeword detection** on next loop iteration
6. Processes answer, updates data
7. If still missing info: chain another follow-up
8. If complete: execute intent and clear state

### Follow-Up Question Types

| Type | When | Question Example |
|------|------|------------------|
| `parking_side` | Saving location without side | "Which side - north or south?" |
| `parking_side_for_schedule` | Query schedule without side | "I need to know which side you're parked on - north or south?" |
| `no_parking_saved` | Query about parking with no data | "I don't know where you parked. Where is your car?" |

### Smart Side Detection

Instead of always asking "north, south, east, or west?", Saga queries the street sweeping database to determine valid sides for the specific street/block.

**Implementation** (`parking.py:210-244`):
```python
def get_valid_sides(street, block_limits) -> List[str]:
    # Query database for this street/block
    # Extract unique sides from records
    # Return ["North", "South"] (or whatever exists)
```

**Question Generation:**
- 2 sides: "north or south?"
- 3 sides: "north, south, or east?"
- 4 sides: "north, south, east, or west?"

**Example** (Balboa St between 7th-8th Ave):
```
Before: "Which side of the street - north, south, east, or west?"
After:  "Which side of the street - north or south?"
```

### Fast Follow-Up Listening

**Problem:** Original implementation had 2.2 seconds of delay between asking question and listening for answer.

**Solution** (`run_assistant.py:840-843, 891-892`):
- Skip 1.2s TTS echo prevention delay when `awaiting_followup=True` (no wakeword detection happening)
- Skip 1s end-of-loop delay when `awaiting_followup=True`
- Keep minimal 0.2s delay for audio device release

**Result:** **10x faster** (2.2s → 0.2s)

### Audio Cues

**Question Beep** (`run_assistant.py:338-366`):
- Frequency: 500Hz → 900Hz (rising, questioning tone)
- Duration: 120ms
- Volume: 25% (slightly softer than wakeword confirmation)
- Purpose: Signals "I'm ready for your answer"

**Timing:**
```
Saga: "Which side of the street - north or south?"
      [Speech complete]
      [0.2s device release delay]
      🔔 [Question beep: 500Hz→900Hz]
      🎤 Recording starts immediately
```

### Chained Follow-Ups

The system supports multiple sequential follow-up questions:

**Example:**
```
User: "When do I have to move my car?"
Saga: "I don't know where you parked. Where is your car?"
      [awaiting_followup = True, type = "no_parking_saved"]

User: "Balboa between 7th and 8th"
      [Parsed location, missing side]
Saga: "Which side - north or south?"
      [awaiting_followup = True, type = "parking_side"] ← Chained!

User: "North"
      [Complete information!]
Saga: "Street sweeping is Monday, December 1st from 8 AM to 10 AM."
      [awaiting_followup = False]
```

### Forget Parking Intent

Natural language commands to clear saved parking location:

**Patterns:**
- "forget where I parked"
- "forget my car"
- "clear parking"
- "I moved my car"
- "reset parking"

**Confidence:** 0.60+ (same as other parking intents)

**Pattern Order:** Must come BEFORE `save_parking` in ACTION_PATTERNS to avoid false match on "parked"

---

## Current Development Phase

### Phase 1: Core Voice Pipeline ✅ COMPLETE
- Wakeword detection (custom trained)
- VAD-based recording
- STT transcription
- LLM integration
- TTS synthesis
- Audio device management

### Phase 2: Intent Parsing & Parking ✅ COMPLETE
- Home Assistant intent parser
- Entity resolution with confidence scoring
- SF parking location parsing
- Street sweeping schedule lookup
- TTS pronunciation optimization
- Unified response logging

### Phase 3: Conversational Context ✅ COMPLETE
- ✅ Missing information detection (bottleneck pattern)
- ✅ Follow-up question capability (multi-turn conversations)
- ✅ Conversation state management (awaiting_followup tracking)
- ✅ Context preservation between turns
- ✅ Chained follow-up questions (ask → answer → ask → answer)
- ✅ Smart side detection (only ask relevant sides based on street data)
- ✅ Fast follow-up listening (0.2s delay instead of 2.2s)
- ✅ Audio cues (question beep for follow-up listening)
- ✅ Forget parking intent (natural language clearing)

### Phase 4: Background Intelligence (Planned)
- Proactive street sweeping reminders
- Timer expiration notifications
- HA automation triggers
- Presence-based awareness

### Phase 5: Advanced Features (Planned)
- Multi-room audio
- Voice training & personalization
- Custom wakeword variants
- Multi-language support

---

## Known Issues & Limitations

### Critical
~~1. **No follow-up questions**: Cannot ask for missing information~~ ✅ FIXED (Phase 3)
~~2. **Ambiguous sweeping info**: May provide wrong schedule if side not specified~~ ✅ FIXED (Phase 3)

### Medium
~~1. **Single-turn only**: No conversation context between interactions~~ ✅ FIXED (Phase 3)
2. **No proactive reminders**: User must query manually
3. **Limited entity types**: Only supports light, switch, cover, fan, lock
4. **VAD over-filtering**: Sometimes removes all audio in very short follow-up responses

### Low
1. **No multi-user support**: Single voice profile
2. **No voice customization**: Fixed TTS voice
3. **Fixed wakeword**: Cannot change at runtime

---

## Success Metrics

### User Experience
- ✅ Response time: <10 seconds end-to-end
- ✅ First syllable capture: 100% success rate
- ✅ Wakeword accuracy: >95% detection, <1% false positives
- ✅ TTS clarity: Natural pronunciation with expansion

### System Reliability
- ✅ 100% LAN operation (no cloud dependencies)
- ✅ Automatic error recovery (audio device retries)
- ✅ Graceful degradation (HA unavailable = parking still works)

### Feature Completeness
- ✅ Home automation control
- ✅ Parking & street sweeping with smart validation
- ✅ Weather queries
- ✅ Timers & reminders
- ✅ Conversational clarification (multi-turn follow-ups)
- ✅ Fast, responsive follow-up listening (0.2s delay)
- ✅ Audio cues for conversation flow

---

## Future Considerations

### Short Term (Next 2 Sprints)
1. Implement follow-up question handling
2. Add conversation state management
3. Improve parking side disambiguation
4. Background reminder checking loop

### Medium Term (Next Quarter)
1. HA presence-based automation
2. Calendar integration
3. Shopping list management
4. Multi-room audio coordination

### Long Term (6-12 Months)
1. Voice biometrics (multi-user)
2. Emotional tone detection
3. Proactive suggestions
4. Custom skill plugins

---

## Dependencies

### Python Packages (via Pipfile)
- openwakeword==0.6.0
- faster-whisper
- openai (for Ollama API)
- piper-tts
- sounddevice
- webrtcvad
- numpy
- requests

### External Services
- Home Assistant API (optional, local)
- Ollama (loki.local:11434)
- SF DataSF API (sync only, not runtime)

### Hardware Requirements
- EMEET OfficeCore M0 Plus (or compatible USB speaker/mic)
- Mac mini M4 (or equivalent with 16GB+ RAM)
- RTX 4080 GPU (for LLM, remote OK)

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Nov 2025 | Initial PRD covering Phases 1-2 |

---

**Document Owner:** Saga Assistant Team
**Next Review:** After Phase 3 completion
