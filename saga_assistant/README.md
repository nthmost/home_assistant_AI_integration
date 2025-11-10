# Saga Assistant - Custom Wakeword Voice Assistant

A LAN-only voice assistant with custom wakeword detection for Home Assistant integration.

## Overview

Saga Assistant is a privacy-focused voice assistant that runs entirely on your local network with no cloud dependencies during runtime. It uses OpenWakeWord for custom wakeword detection with "Hey Saga" as the primary wake phrase.

## Goals

- ✅ **100% LAN-based operation** - No internet required after initial setup
- ✅ **Custom wakeword** - "Hey Saga" (with "Hey Eris" and "Hey Cera" as alternatives)
- 🔄 **Voice pipeline** - Wake word → STT → LLM → TTS (in development)
- 🔄 **Home Assistant integration** - Control smart home with voice commands

## Current Status

### ✅ Completed: Wakeword Detection

- OpenWakeWord v0.6.0 installed and configured
- ONNX Runtime for macOS ARM64 inference
- EMEET OfficeCore M0 Plus audio device configured
- 6 pre-trained models working (alexa, hey_jarvis, hey_mycroft, etc.)
- Demo scripts ready for testing

### 🔄 In Progress: Custom Model Training

- **Next:** Train "Hey Saga" model using Google Colab
- **Notebook:** https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb

### 📋 Planned: Full Voice Pipeline

1. **STT (Speech-to-Text)** - faster-whisper (local inference)
2. **LLM (Intent Processing)** - Ollama on loki.local (qwen2.5:7b)
3. **TTS (Text-to-Speech)** - Piper (local synthesis)
4. **Home Assistant Integration** - REST API for device control

## Hardware Setup

### Audio Devices
- **Input:** EMEET OfficeCore M0 Plus (Device 2, 16kHz, 2 channels)
- **Output:** EMEET OfficeCore M0 Plus (Device 1, 48kHz, 2 channels)

### Processing
- **Wakeword/STT/TTS:** Mac mini M4 (16GB RAM)
- **LLM Inference:** loki.local (AMD Ryzen 7 2700X, RTX 4080 16GB, 62GB RAM)

## Quick Start

### Test Audio Devices

```bash
pipenv run python saga_assistant/demo_audio_devices.py
```

This will:
- List all audio devices (EMEET highlighted)
- Test recording from EMEET microphone
- Test playback to EMEET speaker
- Save a test recording

### Run Wakeword Detection

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
└── models/                     # Custom trained models (future)
    └── hey_saga.onnx          # Custom "Hey Saga" model (to be trained)
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
- [ ] Custom "Hey Saga" model training

### Phase 2: Speech-to-Text 📋
- [ ] Install faster-whisper
- [ ] Test STT latency
- [ ] Optimize for <300ms transcription

### Phase 3: LLM Integration 📋
- [ ] Connect to Ollama on loki.local
- [ ] Intent classification
- [ ] Home Assistant command parsing

### Phase 4: Text-to-Speech 📋
- [ ] Install Piper TTS
- [ ] Voice selection
- [ ] Optimize for <200ms synthesis

### Phase 5: Home Assistant Integration 📋
- [ ] REST API connection
- [ ] Device control commands
- [ ] Status queries
- [ ] Automation triggers

### Phase 6: Complete Pipeline 📋
- [ ] Full wake → speak → respond flow
- [ ] Error handling
- [ ] Latency optimization (<2s total)
- [ ] Production deployment

## Links & Resources

- **OpenWakeWord GitHub:** https://github.com/dscripka/openWakeWord
- **Training Notebook:** https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb
- **WAKEWORD_SETUP.md:** Detailed technical setup guide
- **Project CLAUDE.md:** Voice assistant requirements and architecture

---

**Project Started:** 2025-11-09
**Current Phase:** Phase 1 - Wakeword Detection
**Next Milestone:** Train custom "Hey Saga" model
