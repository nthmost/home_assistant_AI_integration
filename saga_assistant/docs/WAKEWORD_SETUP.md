# Wakeword Detection Setup - OpenWakeWord

## Summary

Successfully set up OpenWakeWord for custom wakeword detection on macOS M4 (Mac mini) with the EMEET OfficeCore M0 Plus audio device.

## System Configuration

### Hardware
- **Audio Input:** EMEET OfficeCore M0 Plus (Device 2)
- **Audio Output:** EMEET OfficeCore M0 Plus (Device 1)
- **Processing:** Mac mini M4
- **Python Version:** 3.13.9 (downgraded from 3.14.0 for OpenWakeWord compatibility)

### Software Stack
- **OpenWakeWord:** v0.6.0
- **Inference Framework:** ONNX Runtime (onnxruntime)
- **Audio Library:** sounddevice + pyaudio
- **Python Environment:** pipenv

## Installation Steps Completed

1. ✅ **Audio Device Verification**
   - Created `demo_audio_devices.py` to test EMEET microphone and speaker
   - Verified input at 16kHz (perfect for speech recognition)
   - Verified output at 48kHz

2. ✅ **Python Environment Setup**
   - Downgraded from Python 3.14 to Python 3.13 (OpenWakeWord requirement)
   - Updated `Pipfile` with `python_version = "3.13"`
   - Installed Python 3.13 via Homebrew

3. ✅ **OpenWakeWord Installation**
   - Installed `openwakeword` package
   - Installed `onnxruntime` for ARM64 macOS inference
   - Downloaded all pre-trained models (6 total)

4. ✅ **Testing**
   - Created `demo_wakeword.py` for live wakeword detection
   - Successfully loaded all 6 pre-trained models
   - System running and ready to detect wakewords

## Pre-Trained Models Available

The following models are ready to use:

| Model Name | Detects |
|------------|---------|
| `alexa` | "alexa" |
| `hey_mycroft` | "hey mycroft" |
| `hey_jarvis` | "hey jarvis" |
| `hey_rhasspy` | "hey rhasspy" |
| `timer` | "set a timer" |
| `weather` | "what's the weather" |

## Usage

### Test Audio Devices
```bash
pipenv run python demo_audio_devices.py
```

### Run Wakeword Detection
```bash
pipenv run python demo_wakeword.py
```

The demo will:
- Automatically find the EMEET input device
- Load all pre-trained models
- Listen for 60 seconds
- Report any detected wakewords with confidence scores

## Next Steps: Custom "Hey Saga" Training

### Training Process

1. **Use Google Colab Notebook** (Recommended for first attempt)
   - URL: https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb?usp=sharing
   - Simple interface, produces model in <1 hour
   - No development experience required

2. **Training Requirements**
   - Generate synthetic training data using TTS (text-to-speech)
   - Collect negative examples (audio without the wakeword)
   - Train small classification layer on top of frozen feature extractor

3. **Alternative Wakewords to Test**
   - Primary: "Hey Saga"
   - Alternative 1: "Hey Eris"
   - Alternative 2: "Hey Cera"

### Custom Model Usage

Once trained, the custom model can be loaded:

```python
from openwakeword.model import Model

# Load custom model
oww = Model(
    wakeword_models=["path/to/hey_saga.onnx"],
    inference_framework="onnx"
)
```

## Key Technical Details

### Audio Configuration
- **Sample Rate:** 16kHz (OpenWakeWord requirement)
- **Channels:** Mono (1 channel)
- **Chunk Size:** 1280 samples (80ms)
- **Format:** int16

### Detection Parameters
- **Threshold:** 0.5 (adjustable for sensitivity)
  - Lower = more sensitive (more false positives)
  - Higher = less sensitive (fewer false positives)
- **False-reject rate target:** <5%
- **False-accept rate target:** <0.5 per hour

### Performance Characteristics
- **Latency:** ~80ms per chunk
- **CPU Usage:** Minimal (runs on CPU with ONNX)
- **Memory:** ~10MB per model
- **Offline:** 100% local processing once models are downloaded

## Files Created

- `demo_audio_devices.py` - Audio device verification tool
- `demo_wakeword.py` - Live wakeword detection demo
- `WAKEWORD_SETUP.md` - This documentation
- `CLAUDE.md` - Updated with voice assistant requirements

## Troubleshooting

### Common Issues

1. **"No module named tflite_runtime"**
   - Solution: Use `inference_framework="onnx"` when creating Model
   - ONNX Runtime is properly installed and works on macOS ARM64

2. **"No EMEET device found"**
   - Solution: Run `demo_audio_devices.py` to check device status
   - Verify EMEET is plugged in and recognized by macOS

3. **Models not found**
   - Solution: Run `import openwakeword; openwakeword.utils.download_models()`
   - Downloads all pre-trained models to the package directory

4. **Audio buffer overflow**
   - Solution: Reduce system load, close other audio applications
   - Consider increasing chunk size if persistent

## Dependencies

Key packages in Pipfile:
```
openwakeword
onnxruntime
sounddevice
pyaudio
numpy
```

All installed and working on Python 3.13.9 / macOS ARM64.

---

**Status:** ✅ System ready for custom model training
**Next Action:** Train "Hey Saga" model using Google Colab notebook
**Date:** 2025-11-09
