# Saga Assistant - Custom Wakeword Voice Assistant

A LAN-only voice assistant with custom wakeword detection for Home Assistant integration.

## Recent Updates (Latest Session)

**2025-11-18**: Phase 4 Complete - Power Phrases & Utilities
- ✅ Weather integration (wttr.in API with voice-optimized responses)
- ✅ Timer system with word number support ("five minutes", "twenty seconds")
- ✅ Reminder system with verbose announcements
- ✅ Wakeword bounce prevention (3-chunk cooldown)
- ✅ Fixed audio device conflicts with timing delays
- ✅ Compass direction conversion for wind (WNW → "west northwest")
- ✅ Rain forecast voice optimization (simplified multi-period responses)

## Overview

Saga Assistant is a privacy-focused voice assistant that runs entirely on your local network with no cloud dependencies during runtime. It uses OpenWakeWord for custom wakeword detection with "Hey Saga" as the primary wake phrase.

## Goals

- ✅ **100% LAN-based operation** - No internet required after initial setup
- ✅ **Custom wakeword** - "Hey Saga" trained with noisy tier
- ✅ **Complete voice pipeline** - Wake word → STT → LLM → TTS
- ✅ **Home Assistant integration** - Control smart home with voice commands
- ✅ **Power phrases** - Instant responses for common queries (weather, time, timers)

## Current Status

### ✅ Phase 1 Complete: Wakeword Detection

- OpenWakeWord v0.6.0 installed and configured
- Custom "Hey Saga" model trained with noisy tier (robust to background speech)
- EMEET OfficeCore M0 Plus audio device configured
- Demo: `pipenv run python demo_wakeword.py`

### ✅ Phase 2 Complete: Full Voice Pipeline

**All components working:**

1. ✅ **STT (Speech-to-Text)** - faster-whisper medium model (769M params)
   - Demo: `pipenv run python demo_stt.py`
   - Auto-detects EMEET microphone
   - Dynamic VAD-based recording (no fixed duration!)
   - Upgraded from base → small → medium for accuracy

2. ✅ **LLM (Language Model)** - qwen2.5:7b on loki.local (~672ms)
   - Demo: `pipenv run python demo_llm.py`
   - OpenAI-compatible API via Ollama
   - Conversational responses optimized for voice

3. ✅ **TTS (Text-to-Speech)** - Piper (~84ms synthesis)
   - Demo: `pipenv run python demo_tts.py`
   - **Default voice:** `en_GB-semaine-medium` (British multi-speaker)
   - **Preferred voices:** alba, semaine, cori (all British, fast, pleasant)
   - 6 voices downloaded and ready

4. ✅ **Complete Integration** - Full voice assistant working!
   - Run: `pipenv run python run_assistant.py`
   - **Total latency:** ~4-5 seconds (wakeword → TTS playback)
   - State machine: idle → listening → processing → speaking
   - **Dynamic VAD:** WebRTC VAD with intelligent auto-stop
   - **Pre-speech buffering:** 600ms to capture first syllables

### ✅ Phase 3 Complete: Home Assistant Integration

**All components working:**

1. ✅ **HA Client** - REST API connection (`saga_assistant/ha_client.py`)
   - Device discovery and control
   - Entity search and status queries
   - Proper error handling with custom exceptions

2. ✅ **Intent Parser** - Natural language → HA commands (`saga_assistant/intent_parser.py`)
   - Action detection (turn_on, turn_off, toggle, status)
   - Entity type and name parsing
   - Smart entity resolution with confidence scoring
   - Demo: `pipenv run python saga_assistant/intent_parser.py`

3. ✅ **Voice Assistant Integration** - HA commands via voice
   - Fast path for HA commands (no LLM needed!)
   - Intelligent routing: HA intent → direct execution, else → LLM
   - Natural spoken responses
   - Graceful fallback if HA unavailable

**Example Commands:**
- "Turn on the TV light"
- "Turn off the aqua lights"
- "Toggle the power strip"
- "What's the weather?" (fallback to LLM)

### ✅ Phase 4 Complete: Power Phrases & Utilities

**Power Phrases System** - Instant responses without LLM processing (`saga_assistant/power_phrases.json`)

1. ✅ **Greetings & Social**
   - "Hi", "Hello", "Hey"
   - "Thank you", "Thanks"
   - "Good morning", "Good night"

2. ✅ **Time & Date**
   - "What time is it?"
   - "What's the date?"

3. ✅ **Weather Integration** (`saga_assistant/weather.py`)
   - Current: "What's the weather?", "How's the weather?"
   - Time-based: "What's the weather this morning/afternoon/tonight?"
   - Forecast: "What's the weather tomorrow?"
   - Rain: "Will it rain today/tomorrow?", "Is it going to rain?"
   - Wind: "How windy is it?", "Is there much wind?"
   - Uses wttr.in API (San Francisco, zip 94118)
   - Voice-optimized responses (compass directions spelled out, simplified rain forecasts)

4. ✅ **Timers & Reminders** (`saga_assistant/timers.py`)
   - Set: "Set a timer for 5 minutes", "Timer for 30 seconds"
   - Check: "How much time is left?", "Check the timer"
   - Cancel: "Cancel the timer", "Stop the timer"
   - Reminders: "Remind me in 20 minutes to check the laundry"
   - **Supports word numbers**: "one", "five", "twenty", etc.
   - **Background threading**: Timers run independently, announce when complete
   - **Verbose reminders**: Announces full reminder message on expiration

5. ✅ **Wakeword Bounce Prevention**
   - 3-chunk cooldown (~4 seconds) prevents duplicate detections
   - Eliminates false triggers from audio buffer overlap

**Example Commands:**
- "What time is it?" → instant response
- "What's the weather tomorrow?" → wttr.in forecast
- "Is it going to rain today?" → precipitation check
- "Set a timer for five minutes" → background timer with announcement
- "Remind me in twenty minutes to take out the trash" → verbose reminder

## Hardware Setup

### Audio Devices
- **Input:** EMEET OfficeCore M0 Plus (Device 2, 16kHz, 2 channels)
- **Output:** EMEET OfficeCore M0 Plus (Device 1, 48kHz, 2 channels)

### Processing
- **Wakeword/STT/TTS:** Mac mini M4 (16GB RAM)
- **LLM Inference:** loki.local (AMD Ryzen 7 2700X, RTX 4080 16GB, 62GB RAM)

## Quick Start

### Run the Full Voice Assistant

```bash
pipenv run python saga_assistant/run_assistant.py
```

This starts the complete voice assistant with all features:
- Wakeword detection ("Hey Saga")
- Speech-to-text (faster-whisper)
- Power phrases (weather, timers, greetings)
- Home Assistant control
- LLM responses (qwen2.5:7b on loki.local)
- Text-to-speech (Piper)

**Try these commands:**
- "Hey Saga" → "What's the weather?"
- "Hey Saga" → "Set a timer for five minutes"
- "Hey Saga" → "Remind me in twenty minutes to check the laundry"
- "Hey Saga" → "Turn on the TV light"
- "Hey Saga" → "What time is it?"
- "Hey Saga" → "Will it rain today?"

### Test Audio Devices

```bash
pipenv run python saga_assistant/demo_audio_devices.py
```

This will:
- List all audio devices (EMEET highlighted)
- Test recording from EMEET microphone
- Test playback to EMEET speaker
- Save a test recording

### Run Wakeword Detection Only

```bash
pipenv run python saga_assistant/demo_wakeword.py
```

This will:
- Load all 6 pre-trained models
- Listen for wakewords using EMEET microphone
- Report detections with confidence scores
- Run for 60 seconds (or press Ctrl+C to stop)

**Try saying:**
- "Alexa"
- "Hey Jarvis"
- "Hey Mycroft"
- "Hey Rhasspy"
- "Set a timer"
- "What's the weather"

## Directory Structure

```
saga_assistant/
├── README.md                    # This file
├── WAKEWORD_SETUP.md           # Detailed setup documentation
├── demo_audio_devices.py       # Audio device testing tool
├── demo_wakeword.py            # Live wakeword detection demo
├── demo_stt.py                 # Speech-to-text testing (faster-whisper)
├── demo_llm.py                 # LLM integration testing (qwen2.5:7b)
├── demo_tts.py                 # Text-to-speech testing (Piper)
├── demo_ha_control.py          # Home Assistant control demo
├── ha_client.py                # Home Assistant REST API client
├── intent_parser.py            # Natural language intent parser
├── run_assistant.py            # ⭐ Complete voice assistant (main entry point)
├── power_phrases.json          # Power phrase patterns for instant responses
├── weather.py                  # Weather integration (wttr.in API)
├── timers.py                   # Timer and reminder system
├── models/                     # Custom trained models
│   ├── hey_saga.onnx          # Custom "Hey Saga" model (basic tier)
│   └── hey_saga_noisy.onnx    # Custom "Hey Saga" model (noisy tier, default)
└── training_scripts/           # Training pipeline with tier support
```

## Training Custom "Hey Saga" Model

### Using Google Colab (Recommended)

1. **Open the notebook:** https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb
2. **Enter your wakeword:** "Hey Saga"
3. **Generate training data** using TTS (automated)
4. **Train the model** (takes ~30-60 minutes)
5. **Download the model** (`hey_saga.onnx`)
6. **Copy to:** `saga_assistant/models/`

### Loading Custom Model

```python
from openwakeword.model import Model

# Load custom "Hey Saga" model
oww = Model(
    wakeword_models=["saga_assistant/models/hey_saga.onnx"],
    inference_framework="onnx"
)

# Use in detection loop
predictions = oww.predict(audio_chunk)
if predictions.get("hey_saga", 0) > 0.5:
    print("Hey Saga detected!")
```

## Technical Details

### Audio Configuration
- **Sample Rate:** 16kHz (OpenWakeWord requirement)
- **Channels:** Mono (1 channel)
- **Chunk Size:** 1280 samples (80ms chunks)
- **Format:** int16

### Detection Parameters
- **Default Threshold:** 0.5
- **Adjustable for sensitivity:**
  - Lower (0.3-0.4) = More sensitive, more false positives
  - Higher (0.6-0.7) = Less sensitive, fewer false positives
- **Target False-Reject Rate:** <5%
- **Target False-Accept Rate:** <0.5 per hour

### Performance
- **Latency:** ~80ms per chunk
- **CPU Usage:** Minimal (ONNX on CPU)
- **Memory:** ~10MB per model
- **Offline:** 100% local processing

## Dependencies

All managed via pipenv (Python 3.13):

```
openwakeword          # Wakeword detection framework
onnxruntime          # ONNX inference (macOS ARM64)
sounddevice          # Audio I/O
pyaudio              # Audio backend
numpy                # Audio processing
faster-whisper       # Speech-to-text (Whisper base model)
openai               # LLM client (OpenAI-compatible API)
piper-tts            # Text-to-speech (Piper)
```

## Troubleshooting

### No EMEET Device Found
```bash
# Check audio devices
pipenv run python saga_assistant/demo_audio_devices.py
```

Verify EMEET is connected and recognized by macOS.

### Models Not Loading
```bash
# Download pre-trained models
pipenv run python -c "import openwakeword; openwakeword.utils.download_models()"
```

### TFLite Runtime Error
Make sure scripts use `inference_framework="onnx"` when creating Model instances. TFLite is not available on macOS ARM64.

## Development Roadmap

### Phase 1: Wakeword Detection ✅
- [x] OpenWakeWord setup
- [x] Audio device configuration
- [x] Pre-trained model testing
- [x] Custom "Hey Saga" model training (basic + noisy tiers)

### Phase 2: Full Voice Pipeline ✅
- [x] Install faster-whisper for STT
- [x] Test STT latency (~317ms with base model)
- [x] Install Piper TTS
- [x] Voice selection (semaine, alba, cori preferred)
- [x] Connect to Ollama on loki.local for LLM inference
- [x] Complete integration (run_assistant.py)
- [x] Total latency optimization (~1.2-1.3s, well under 2s target!)

### Phase 3: Home Assistant Integration ✅
- [x] REST API connection
- [x] Device control commands
- [x] Status queries
- [x] Natural language intent parsing
- [x] Voice assistant integration

### ✅ Phase 4 Complete: Advanced Features (VAD)
- [x] Dynamic VAD for variable-length utterances (WebRTC VAD)
- [x] Replaced fixed 5s recording with intelligent auto-stop
- [x] Pre-speech buffering (600ms) to capture first syllables
- [x] Audio error recovery with retry logic
- [x] Whisper model upgrade (base → medium) for accuracy
- [x] Personality tuning for brevity and conversational tone
- [ ] Intent classification (future)
- [ ] Context awareness across conversations (future)

### Phase 5: Production Deployment 📋
- [ ] System service configuration
- [ ] Auto-restart on failure
- [ ] Long-term stability testing
- [ ] Performance monitoring

## Links & Resources

- **OpenWakeWord GitHub:** https://github.com/dscripka/openWakeWord
- **Training Notebook:** https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb
- **WAKEWORD_SETUP.md:** Detailed technical setup guide
- **Project CLAUDE.md:** Voice assistant requirements and architecture

## Next Steps (Potential Enhancements)

**More Power Phrases:**
- "Turn on/off all the lights"
- Scene triggers ("Good morning", "Goodnight", "Movie mode")
- Music/media control ("Pause", "Volume up/down")
- Utilities ("Flip a coin", "Roll a die", "Tell me a joke")
- Shopping lists ("Add X to my shopping list")

**Timer/Reminder Enhancements:**
- Absolute time reminders: "Remind me at 3pm to call mom"
- Named timers: "Set a 5 minute timer called pizza"
- Multiple simultaneous timers
- Timer persistence across restarts

**Home Assistant Improvements:**
- Scene activation ("Movie mode", "Bedtime")
- Climate control ("Set temperature to 72")
- Device groups ("Turn on all the lights")
- Status queries ("What's the temperature?")

**Advanced Features:**
- Context awareness across conversations
- User preferences and personalization
- Multi-user support (voice recognition)
- System service for auto-start
- Web dashboard for monitoring

---

**Project Started:** 2025-11-09
**Phase 1 Complete:** 2025-11-09 (Wakeword Detection)
**Phase 2 Complete:** 2025-11-10 (Full Voice Pipeline)
**Phase 3 Complete:** 2025-11-10 (Home Assistant Integration)
**Phase 4 Complete:** 2025-11-18 (Power Phrases, Weather, Timers, Reminders)
**Current Status:** ✅ Fully Functional Voice Assistant
**Ready for:** Daily use, additional power phrases, production deployment
