# Saga Assistant

**A 100% LAN-based voice assistant with custom wakeword detection for Home Assistant integration.**

[![Status](https://img.shields.io/badge/status-production--ready-green)]()
[![Python](https://img.shields.io/badge/python-3.13-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

---

## Quick Start

```bash
# Run the full voice assistant
pipenv run python saga_assistant/run_assistant.py
```

**Say:** "Hey Saga" → "What's the weather in Big Sur tomorrow?"

---

## Overview

Saga is a privacy-focused voice assistant that runs entirely on your local network with **zero cloud dependencies** during runtime. All processing happens on-premises:

- 🎙️ **Wakeword:** Custom "Hey Saga" (OpenWakeWord)
- 🗣️ **STT:** faster-whisper (local Whisper model)
- 🧠 **LLM:** qwen2.5:7b on loki.local (Ollama)
- 🔊 **TTS:** Piper (local neural TTS)

**Total latency:** ~4-5 seconds from wake to response

---

## ✨ Features

### 🎯 Core Capabilities
- ✅ **Custom wakeword** - "Hey Saga" trained with noisy tier
- ✅ **Dynamic VAD** - Intelligent silence detection (no fixed duration)
- ✅ **Home Assistant** - Device control via voice commands
- ✅ **Weather V2** - Multi-location forecasts (any city worldwide)
- ✅ **Timers & Reminders** - Background timers with custom sounds
- ✅ **Memory System** - Preference storage and context injection
- ✅ **Parking Assistant** - SF street sweeping integration
- ✅ **Power Phrases** - Instant responses (<10ms, no LLM)

### 🌤️ Weather Queries (NEW!)
```
"What's the weather in Crescent City tomorrow?"
"Will it rain in Big Sur today?"
"What's the weather in Paris this week?"
```
- **Multi-location support** - Any city worldwide via wttr.in
- **5-day forecasts** - High/low temps, conditions, wind, rain
- **Smart caching** - Frequent locations cached for speed
- **No ZIP required** - Automatic geocoding for location names

### 🏠 Home Assistant
```
"Turn on the TV light"
"Is the aqua light on?"
"Toggle the power strip"
```

### ⏱️ Timers & Reminders
```
"Set a timer for five minutes"
"Set a laundry timer for 30 minutes"
"Remind me in 20 minutes to check the oven"
```

### 🚗 Parking (San Francisco)
```
"I parked on Valencia between 18th and 19th, south side"
"When do I need to move my car?"
"Where did I park?"
```

### 🧠 Memory
```
"I prefer casual responses"
"Remember that I like brief answers"
"What are my preferences?"
```

**Full feature documentation:** [`docs/FEATURES.md`](docs/FEATURES.md)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│  EMEET Microphone → Wakeword → STT → Intent Parser      │
│                                         ↓                │
│                            ┌────────────┴──────────────┐ │
│                            │ Power Phrases (instant)   │ │
│                            │ Home Assistant (fast)     │ │
│                            │ LLM (conversational)      │ │
│                            └────────────┬──────────────┘ │
│                                         ↓                │
│  EMEET Speaker ← TTS ← TTS Formatter ← Response         │
└─────────────────────────────────────────────────────────┘
```

**Hardware:**
- **Mac mini M4** - Wakeword, STT, TTS (local processing)
- **loki.local** - LLM inference (RTX 4080, Ollama)
- **EMEET M0 Plus** - Microphone + Speaker combo

**All processing is LAN-only** - No internet required during runtime

---

## 📁 Project Structure

```
saga_assistant/
├── run_assistant.py          # Main entry point ⭐
├── Core modules (11 files)
│   ├── ha_client.py          # Home Assistant integration
│   ├── intent_parser.py      # NLU intent parsing
│   ├── weather_v2.py         # Weather system
│   ├── parking.py            # Parking assistant
│   ├── timers.py             # Timers & reminders
│   └── ...
│
├── examples/                 # Demo scripts (9 files)
│   ├── demo_wakeword.py
│   ├── demo_stt.py
│   └── ...
│
├── docs/                     # Documentation (21 files)
│   ├── FEATURES.md           # Complete feature guide
│   ├── QUICKSTART.md         # Getting started
│   ├── WEATHER_SERVICE.md    # Weather architecture
│   └── ...
│
├── services/                 # Background services
│   └── weather_*_v2.py       # Weather V2 APIs
│
├── memory/                   # Memory system
├── models/                   # Wakeword models
└── sounds/                   # Timer sounds
```

---

## 🚀 Installation

### Prerequisites
- Python 3.13
- pipenv
- macOS (for EMEET device support)
- loki.local with Ollama running qwen2.5:7b

### Setup

```bash
# Install dependencies
pipenv install

# Test audio devices
PYTHONPATH=. pipenv run python saga_assistant/examples/demo_audio_devices.py

# Test wakeword detection
PYTHONPATH=. pipenv run python saga_assistant/examples/demo_wakeword.py

# Run full assistant
pipenv run python saga_assistant/run_assistant.py
```

**Full setup guide:** [`docs/QUICKSTART.md`](docs/QUICKSTART.md)

---

## 📊 Performance

| Component | Latency | Notes |
|-----------|---------|-------|
| Wakeword | ~80ms/chunk | Custom "Hey Saga" model |
| Recording | 2-4s | Dynamic VAD (auto-stop) |
| STT | ~300-500ms | faster-whisper medium |
| LLM | ~672ms | qwen2.5:7b on loki.local |
| TTS | ~84ms | Piper (en_GB-semaine) |
| **Total** | **~4-5s** | Wake → speech output |

**Power Phrases:** <10ms (regex matching, no LLM)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [`FEATURES.md`](docs/FEATURES.md) | Complete feature documentation |
| [`QUICKSTART.md`](docs/QUICKSTART.md) | Getting started guide |
| [`WEATHER_SERVICE.md`](docs/WEATHER_SERVICE.md) | Weather V2 architecture |
| [`WAKEWORD_SETUP.md`](docs/WAKEWORD_SETUP.md) | Wakeword training guide |
| [`MEMORY_ARCHITECTURE.md`](docs/MEMORY_ARCHITECTURE.md) | Memory system design |
| [`PARKING_FEATURE.md`](docs/PARKING_FEATURE.md) | Parking assistant details |
| [`PERFORMANCE_TUNING.md`](docs/PERFORMANCE_TUNING.md) | Optimization guide |

**See [`docs/`](docs/) for 20+ documentation files**

---

## 🎯 Current Status

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Wakeword detection |
| Phase 2 | ✅ Complete | Full voice pipeline (STT → LLM → TTS) |
| Phase 3 | ✅ Complete | Home Assistant integration |
| Phase 4 | ✅ Complete | Weather, timers, memory, parking |
| Phase 5 | 📋 Planned | Production deployment |

**Ready for:** Daily use, production deployment

---

## 🛠️ Development

### Run Examples
```bash
# All examples use PYTHONPATH=. for imports
PYTHONPATH=. pipenv run python saga_assistant/examples/demo_name.py
```

### Directory Organization (2025-11-26)
- **Root:** 11 core modules only
- **examples/:** 9 demo scripts with README
- **docs/:** 21 markdown documentation files
- **services/:** V2 weather services
- **memory/:** Preference storage system

**Reorganization:** All demos and docs moved to subdirectories for clarity

---

## 🔮 Roadmap

### Near Term
- [ ] System service for auto-start
- [ ] Web dashboard for monitoring
- [ ] Multi-user support (voice recognition)
- [ ] Absolute time reminders ("at 3pm")

### Future Enhancements
- [ ] Music/media control
- [ ] Shopping list management
- [ ] Scene triggers ("Movie mode")
- [ ] Climate control integration
- [ ] Context awareness across conversations

---

## 📝 Recent Updates

**2025-11-26**: Weather V2 + Directory Cleanup
- ✅ Multi-location weather support (any city worldwide)
- ✅ wttr.in API integration with automatic geocoding
- ✅ Directory reorganization (examples/, docs/)
- ✅ Comprehensive FEATURES.md documentation

**2025-11-23**: Memory System + Conversational AI
- ✅ Preference storage and context injection
- ✅ AI-to-AI conversation validation
- ✅ TTS formatter abstraction

**2025-11-18**: Power Phrases + Timers
- ✅ Weather integration with power phrases
- ✅ Timer system with custom sounds
- ✅ Parking assistant (SF street sweeping)

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **OpenWakeWord** - Custom wakeword detection
- **faster-whisper** - Efficient Whisper implementation
- **Piper** - High-quality neural TTS
- **Ollama** - Local LLM serving
- **Home Assistant** - Smart home platform

---

**Project Started:** 2025-11-09
**Current Version:** v1.0.0 (Production Ready)
**Maintainer:** Claude Code + nthmost

For questions, issues, or contributions, see [`docs/FEATURES.md`](docs/FEATURES.md) for detailed feature documentation.
