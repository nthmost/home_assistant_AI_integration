# Saga Assistant Examples

Demo scripts for testing and exploring Saga Assistant features.

## Audio & Voice

- **`demo_audio_devices.py`** - Test audio input/output devices (EMEET microphone/speaker)
- **`demo_wakeword.py`** - Live wakeword detection demo ("Hey Saga")
- **`demo_stt.py`** - Speech-to-text testing with faster-whisper
- **`demo_tts.py`** - Text-to-speech testing with Piper

## Core Features

- **`demo_ha_control.py`** - Home Assistant device control demos
- **`demo_llm.py`** - LLM integration testing (Ollama on loki.local)
- **`demo_memory.py`** - Memory system testing (preferences, facts)
- **`demo_timer_sounds.py`** - Custom timer sound testing

## Weather

- **`demo_weather_v2.py`** - Weather V2 system demo (multi-location, 5-day forecasts)

## Running Examples

All examples should be run from the project root with:

```bash
PYTHONPATH=. pipenv run python saga_assistant/examples/demo_name.py
```

Or from within the saga_assistant directory:

```bash
PYTHONPATH=. pipenv run python examples/demo_name.py
```
