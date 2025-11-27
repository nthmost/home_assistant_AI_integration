# Saga Assistant Features

Complete feature documentation for the Saga voice assistant system.

**Last Updated:** 2025-11-26

---

## 🎙️ Core Voice Pipeline

### Wakeword Detection
- **Model:** Custom "Hey Saga" (OpenWakeWord v0.6.0)
- **Training:** Noisy tier (robust to background speech)
- **Performance:** ~80ms latency per chunk
- **Bounce Prevention:** 3-chunk cooldown (~4s) prevents duplicate triggers
- **Location:** `models/hey_saga_noisy.onnx`

### Speech-to-Text (STT)
- **Engine:** faster-whisper (medium model, 769M params)
- **Dynamic VAD:** WebRTC-based voice activity detection
- **Auto-stop:** Intelligent silence detection (no fixed duration)
- **Pre-speech Buffering:** 600ms to capture first syllables
- **Latency:** ~300-500ms
- **Demo:** `examples/demo_stt.py`

### Language Model (LLM)
- **Model:** qwen2.5:7b running on loki.local
- **API:** OpenAI-compatible via Ollama
- **Latency:** ~672ms average
- **Personality:** Conversational, brief, voice-optimized
- **Demo:** `examples/demo_llm.py`

### Text-to-Speech (TTS)
- **Engine:** Piper TTS
- **Default Voice:** en_GB-semaine-medium (British, multi-speaker)
- **Latency:** ~84ms synthesis
- **Voices Available:** 6 (alba, semaine, cori preferred)
- **Demo:** `examples/demo_tts.py`

### TTS Formatting
- **Module:** `tts_formatter.py`
- **Features:**
  - Strips markdown formatting for clean speech
  - Expands abbreviations (N, NE → north, northeast)
  - Removes bullet points and special characters
  - Preserves natural conversation flow

---

## 🌤️ Weather System (V2)

**Architecture:** Multi-location support with smart geocoding

### Core Functions
- `get_weather(location, when)` - Current/forecast weather for any location
- `get_week_summary(location)` - 5-day forecast summary
- `will_it_rain(location, when)` - Precipitation forecast
- `get_wind_info(location)` - Current wind conditions
- `compare_locations(locations, when)` - Multi-location comparison for biking

### Supported Queries
```
"What's the weather?"                    → San Francisco current
"What's the weather in Big Sur tomorrow?" → Any location, any day
"Will it rain today?"                     → Precipitation check
"How windy is it?"                        → Wind speed/direction
"Weather in Paris this week?"             → 5-day summary
```

### Location Support
- **Cached locations:** SF, Marin City, Oakland, Berkeley (via OpenWeatherMap)
- **On-demand locations:** Any city worldwide (via wttr.in geocoding)
- **No ZIP required:** wttr.in handles location name → coordinates

### API Architecture
- **Primary (cached):** OpenWeatherMap (ZIP codes, best data quality)
- **Fallback:** wttr.in (location names, worldwide coverage)
- **No retries:** Fail fast (5s timeout), try next API
- **Caching:** SQLite cache (`~/.saga_assistant/weather.db`)

### Features
- **5-day forecasts:** High/low temps, conditions, rain chance, wind
- **Time queries:** now, today, tomorrow, Monday-Sunday
- **Voice-optimized:** Compass directions spelled out (WNW → "west northwest")
- **Power phrases:** Instant weather responses without LLM

**Documentation:** `docs/WEATHER_SERVICE.md`

---

## 🏠 Home Assistant Integration

### HA Client (`ha_client.py`)
- REST API connection to homeassistant.local
- Device discovery and control
- Entity search and status queries
- Custom exception handling

### Intent Parser (`intent_parser.py`)
- Natural language → Home Assistant commands
- Action detection: turn_on, turn_off, toggle, status
- Entity type/name parsing with confidence scoring
- Smart entity resolution

### Supported Commands
```
"Turn on the TV light"
"Turn off the aqua lights"
"Toggle the power strip"
"Is the TV light on?"
```

### Architecture
- **Fast path:** HA commands bypass LLM (instant execution)
- **Fallback:** LLM handles complex or ambiguous requests
- **Error handling:** Graceful degradation if HA unavailable

**Demo:** `examples/demo_ha_control.py`

---

## ⏱️ Timers & Reminders

### Timer System (`timers.py`)
- **Word number support:** "five minutes", "twenty seconds"
- **Background threading:** Timers run independently
- **Custom sounds:** Different sounds per timer type (see Timer Sounds)
- **Multiple timers:** Simultaneous timer support

### Commands
```
"Set a timer for 5 minutes"
"Set a laundry timer for 30 minutes"
"How much time is left?"
"Cancel the timer"
```

### Reminder System
- **Verbose announcements:** Full reminder message on expiration
- **Background operation:** No blocking

### Commands
```
"Remind me in 20 minutes to check the laundry"
"Remind me in 5 minutes to call mom"
```

**Demo:** `examples/demo_timer_sounds.py`

---

## 🔔 Timer Sounds

**Module:** `timer_sounds.py`

### Custom Sound System
- **Meditation timer:** Bowl gong chime
- **Tea timer:** Soft temple bells
- **Laundry timer:** Gentle xylophone
- **Default timer:** Standard beep

### Sound Files
- Location: `sounds/`
- Format: WAV, mono, 48kHz
- Generated via: Sonic Pi synthesis scripts

### Features
- Type-based sound selection
- Pleasant, non-jarring tones
- Voice assistant announces timer type on completion

**Documentation:** `docs/TIMER_SOUNDS.md`

---

## 🧠 Memory System (Phase 1)

**Architecture:** SQLite-based preference and fact storage

### Components
- **Database:** `memory/database.py` (SQLite schema)
- **Preferences:** `memory/preferences.py` (user preferences)
- **Context Builder:** `memory/context_builder.py` (LLM context injection)

### Preference Storage
```python
# Save preference
preference_manager.save_preference(
    category="communication",
    preference_key="formality",
    preference_value="casual and brief"
)

# Retrieve preferences
prefs = preference_manager.get_all_preferences()
```

### Commands (via intent_parser.py)
```
"I prefer casual responses"           → Saves preference
"Remember that I like brief answers"  → Stores fact
"What are my preferences?"            → Lists preferences
"Forget my preferences"               → Clears memory (with confirmation)
```

### Features
- **Category-based:** Organize preferences by domain
- **Context injection:** Automatically adds preferences to LLM prompts
- **Persistent:** SQLite database at `~/.saga_assistant/memory.db`

**Documentation:** `docs/MEMORY_ARCHITECTURE.md`
**Demo:** `examples/demo_memory.py`

---

## 🚗 Parking Assistant

**Advanced San Francisco street sweeping integration**

### Components
- **Parking Manager:** `parking.py` (location parsing, schedule lookup)
- **Reminders:** `parking_reminders.py` (proactive notifications)
- **Sync Script:** `sync_street_sweeping.py` (updates from SF data)

### Features
- **Location parsing:** "I parked on Valencia between 18th and 19th, south side"
- **Schedule lookup:** SF Open Data API (real street sweeping schedules)
- **Smart reminders:** Notifications before street sweeping
- **Side detection:** Validates street side (north/south/east/west)

### Commands
```
"I parked on Valencia between 18th and 19th"
"Where did I park?"
"When do I need to move my car?"
"Forget where I parked"
```

### Data Source
- **SF Open Data:** Street sweeping schedules
- **Updates:** Via `sync_street_sweeping.py`
- **Storage:** `~/.saga_assistant/parking.json`

**Documentation:** `docs/PARKING_FEATURE.md`
**Voice Commands:** `docs/PARKING_VOICE_COMMANDS.md`

---

## 😈 Minnie Blame Feature

**Module:** `minnie_model.py`

### Purpose
Humorous scapegoat for household mishaps

### Minnie Lore
- Species: Chihuahua (small, mischievous)
- Personality: Chaotic, blame-worthy
- Capabilities: Mysterious household destruction

### Commands
```
"Whose fault is this?"
"Who made this mess?"
"Was it Minnie?"
"What did Minnie do?"
```

### Responses
- Generates creative Minnie-related explanations
- Voice-optimized humor
- Consistent character personality

**Documentation:** `docs/MINNIE_FEATURE.md`

---

## 🎯 Power Phrases

**Fast responses without LLM processing**

### Categories

**Greetings & Social:**
- "Hi", "Hello", "Hey"
- "Thank you", "Thanks"
- "Good morning", "Good night"

**Time & Date:**
- "What time is it?"
- "What's the date?"

**Weather:** (See Weather System)
- Instant weather responses
- Location-based queries
- Forecast and conditions

**Timers:** (See Timers & Reminders)
- Timer management
- Reminder creation

### Performance
- **Latency:** <10ms (regex pattern matching)
- **No LLM:** Direct responses
- **Extensible:** Easy to add new patterns

---

## 🎤 Audio Configuration

### Hardware
- **Input:** EMEET OfficeCore M0 Plus (Device 2, 16kHz)
- **Output:** EMEET OfficeCore M0 Plus (Device 1, 48kHz)

### Processing
- **Wakeword/STT/TTS:** Mac mini M4 (16GB RAM)
- **LLM:** loki.local (RTX 4080 16GB, Ollama)

### Audio Settings
- **Sample Rate:** 16kHz (wakeword), 48kHz (TTS output)
- **Channels:** Mono (wakeword/STT), Stereo (TTS)
- **Chunk Size:** 1280 samples (80ms)
- **Format:** int16

**Documentation:** `docs/EMEET_CAPABILITIES.md`

---

## 📁 Directory Structure

```
saga_assistant/
├── Core Modules
│   ├── run_assistant.py          # Main entry point
│   ├── ha_client.py               # Home Assistant client
│   ├── intent_parser.py           # NLU intent parsing
│   ├── weather_v2.py              # Weather V2 system
│   ├── parking.py                 # Parking manager
│   ├── parking_reminders.py       # Parking reminders
│   ├── minnie_model.py            # Minnie blame model
│   ├── timers.py                  # Timer management
│   ├── timer_sounds.py            # Custom timer sounds
│   ├── tts_formatter.py           # TTS text formatting
│   └── sync_street_sweeping.py    # Street sweeping sync
│
├── examples/                      # Demo scripts
│   ├── demo_audio_devices.py
│   ├── demo_wakeword.py
│   ├── demo_stt.py
│   ├── demo_tts.py
│   ├── demo_llm.py
│   ├── demo_ha_control.py
│   ├── demo_memory.py
│   ├── demo_timer_sounds.py
│   ├── demo_weather_v2.py
│   └── README.md
│
├── docs/                          # Documentation
│   ├── FEATURES.md                # This file
│   ├── WEATHER_SERVICE.md         # Weather architecture
│   ├── WAKEWORD_SETUP.md          # Wakeword training
│   ├── MEMORY_ARCHITECTURE.md     # Memory system
│   ├── PARKING_FEATURE.md         # Parking assistant
│   ├── TIMER_SOUNDS.md            # Timer sounds
│   └── ... (20+ docs)
│
├── services/                      # Background services
│   ├── weather_apis_v2.py         # Weather API adapters
│   ├── weather_cache_v2.py        # Weather caching
│   ├── weather_fetcher_v2.py      # Weather background service
│   └── README_V2.md
│
├── memory/                        # Memory system
│   ├── database.py
│   ├── preferences.py
│   └── context_builder.py
│
├── models/                        # Wakeword models
│   └── hey_saga_noisy.onnx        # Custom trained model
│
├── sounds/                        # Audio files
│   ├── meditation_timer.wav
│   ├── tea_timer.wav
│   └── laundry_timer.wav
│
└── training_scripts/              # Model training
    └── ... (wakeword training pipeline)
```

---

## 🚀 Quick Start

### Run the Full Assistant
```bash
pipenv run python saga_assistant/run_assistant.py
```

### Test Individual Components
```bash
# Audio devices
PYTHONPATH=. pipenv run python saga_assistant/examples/demo_audio_devices.py

# Wakeword detection
PYTHONPATH=. pipenv run python saga_assistant/examples/demo_wakeword.py

# Speech-to-text
PYTHONPATH=. pipenv run python saga_assistant/examples/demo_stt.py

# Text-to-speech
PYTHONPATH=. pipenv run python saga_assistant/examples/demo_tts.py

# Weather V2
PYTHONPATH=. pipenv run python saga_assistant/examples/demo_weather_v2.py
```

---

## 📊 Performance Metrics

### End-to-End Latency
- **Wakeword detection:** ~80ms/chunk
- **Recording:** 2-4s (VAD auto-stop)
- **STT transcription:** ~300-500ms
- **LLM inference:** ~672ms
- **TTS synthesis:** ~84ms
- **Total:** ~4-5 seconds (wakeword → speech output)

### Resource Usage
- **CPU (Mac mini M4):** Minimal (wakeword, STT, TTS)
- **GPU (loki.local RTX 4080):** ~672ms per LLM query
- **Memory:** ~500MB total (all components)
- **Disk:** ~2GB (models, voices, dependencies)

---

## 🔧 Configuration Files

- **Weather cache:** `~/.saga_assistant/weather.db`
- **Memory database:** `~/.saga_assistant/memory.db`
- **Parking state:** `~/.saga_assistant/parking.json`
- **Models:** `saga_assistant/models/`
- **Sounds:** `saga_assistant/sounds/`

---

## 📚 Documentation Index

- **Setup & Training:** `docs/WAKEWORD_SETUP.md`
- **Weather System:** `docs/WEATHER_SERVICE.md`
- **Memory System:** `docs/MEMORY_ARCHITECTURE.md`
- **Parking Feature:** `docs/PARKING_FEATURE.md`
- **Timer Sounds:** `docs/TIMER_SOUNDS.md`
- **Performance:** `docs/PERFORMANCE_TUNING.md`
- **Deployment:** `docs/DEPLOYMENT.md`
- **Quick Start:** `docs/QUICKSTART.md`

---

**Complete.** All current features documented as of 2025-11-26.
