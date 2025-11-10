# Claude Code Guidelines for this Project

## Python Code Standards

### Dependency Management
- **Always use `pipenv`** for dependency management
- Use `Pipfile` and `Pipfile.lock` - never manual requirements.txt maintenance
- Run scripts with `pipenv run python script.py` or activate with `pipenv shell`
- Add dependencies with `pipenv install <package>` (production) or `pipenv install --dev <package>` (development)

### Exception Handling
- **Avoid long try-except blocks** - keep them focused and minimal
- **Never use generic `Exception`** - always catch specific exception types
- **Develop a shared exception hierarchy** across modules in this project
  - Create custom exceptions that inherit from a common base (e.g., `HomeAssistantError`)
  - Place exception classes in a central location (e.g., `ha_core/exceptions.py`)
  - Use specific exceptions for specific failure modes (e.g., `EntityNotFoundError`, `ServiceCallError`)
- Use multiple specific exception handlers rather than one broad catch-all

### Logging Standards
- **Build logging into scripts from the start** - it's not optional
- Follow proper log levels:
  - `INFO` - Key milestones, workflow progress, successful operations
  - `DEBUG` - Detailed diagnostic information, data dumps, trace info
  - `WARNING` - Something unexpected but recoverable happened
  - `ERROR` - Operation failed but application continues
  - `CRITICAL` - System-level failure

- **More logging is better than less**, but must be tunable
- Enable log level filtering so we can turn off the firehose when needed
- **Use colors, formatting, and emojis** to enhance log readability
  - Make logs human-friendly AND machine-parseable
  - This is a log-heavy project where logs will be consumed by other agents
  - Clear, well-formatted logs are critical for debugging complex orchestrations

### Log Consumption Pattern
- Logs will frequently be read and analyzed by other AI agents
- Lack of visibility into system state makes complex systems hard to debug
- Design logs with both human operators and automated analysis in mind

### File Naming Conventions
- **Never use `test_*.py` for demo/trial scripts** - this prefix is reserved for unit tests
- Use descriptive names like `demo_*.py`, `try_*.py`, `run_*.py`, or `example_*.py` for experimental scripts
- Keep `test_*.py` exclusively for proper unit tests in the `tests/` directory

### Code Organization
- **All imports at top of file, never in functions**
- Keep imports organized: stdlib, third-party, local modules
- Avoid lazy imports unless there's a strong performance reason

### Display Mode vs Headless Mode
- **ASCII displays: completely suppress logging when display is active**
- When running with interactive displays (curses, rich panels, etc.), logs interfere with the display
- **Simple rule: display mode = no logs, headless mode = normal logs**
- This ensures clean visual output without log noise
- Use `--display` flag pattern for scripts that offer visual modes

### Streamlit Development
- **`st.rerun()` calls are almost never necessary** - Streamlit's run model handles reruns automatically
- Every widget interaction triggers a natural rerun of the entire script
- Fetch fresh state at the top of the script - it runs on every interaction
- Let Streamlit's reactive model work for you - don't fight it with manual reruns
- Pattern: Fetch state → Render UI → Handle interactions → (Streamlit reruns automatically)

### Testing Strategy
- **Think test-driven development** - consider testability from the start
- **Prototyping vs Production**: We're prototyping until we're not
  - Use `demo_*.py`, `try_*.py` scripts for experimental/prototype code
  - When a feature is ready to formalize, ask the user before creating tests
  - Once formalized, create proper `pytest`-compatible tests in `tests/` directory
- **Test requirements**:
  - Use `pytest` as the testing framework
  - Place all tests in `tests/` directory with `test_*.py` naming
  - Write tests that are isolated, repeatable, and fast
  - Mock external dependencies (Home Assistant API, network calls, etc.)
  - Use fixtures for common test setup
- **Install test dependencies**: `pipenv install --dev pytest pytest-mock pytest-cov`

## Collaboration Style

### Decision Making
- **When asked "should we X?" - DO NOT implement X immediately**
- Wait for confirmation and discussion first
- Offer multiple solution options when available (within reason)
- Present trade-offs clearly

## Voice Assistant Requirements

### Core Constraints
- **100% LAN-based operation** - No remote API calls during runtime (internet-free after setup)
- **Custom wakeword detection** - Must work offline once trained
- **Wakeword training may use remote APIs** - One-time setup process acceptable

### Wakeword Options (in priority order)
1. **Primary:** "Hey Saga"
2. **Alternative 1:** "Hey Eris" (if primary doesn't work well)
3. **Alternative 2:** "Hey Cera" (fallback option)

### Architecture Requirements
- All speech-to-text (STT) processing on LAN
- All LLM inference on LAN (using loki.local GPU server)
- All text-to-speech (TTS) processing on LAN
- Wakeword detection on LAN
- Integration with Home Assistant (local API)

### Hardware
- **Audio Input:** EMEET OfficeCore M0 Plus (Device 2, 16kHz, for wakeword training and runtime voice input)
- **Audio Output:** EMEET OfficeCore M0 Plus (Device 1, 48kHz, for TTS responses)
- **Processing:** Mac mini M4 (wakeword detection, STT, TTS orchestration)
- **LLM Inference:** loki.local (RTX 4080, Ollama with qwen2.5:7b)

## Project Structure

### Voice Assistant (`saga_assistant/`)
Custom wakeword-based voice assistant for Home Assistant integration.

**Current Status:** Phase 1 - Wakeword Detection (✅ Complete)

**Default Wakeword Model:** `saga_assistant/models/hey_saga_noisy.onnx`
- Trained with "noisy" tier for robust performance with competing speech
- Use this model for all Saga assistant testing and development
- More tolerant to background noise and conversation than basic tier

**Key Files:**
- `saga_assistant/README.md` - Main documentation and roadmap
- `saga_assistant/WAKEWORD_SETUP.md` - Detailed technical setup guide
- `saga_assistant/demo_audio_devices.py` - Audio device testing tool
- `saga_assistant/demo_wakeword.py` - Live wakeword detection demo
- `saga_assistant/models/hey_saga_noisy.onnx` - Production wakeword model (default)
- `saga_assistant/training_scripts/` - Training pipeline with tier support

**Technology Stack:**
- OpenWakeWord v0.6.0 (wakeword detection)
- ONNX Runtime (macOS ARM64 inference)
- sounddevice + pyaudio (audio I/O)
- Python 3.13 (via pipenv)

**Training Tiers:**
- `basic`: Standard training with music/ambient noise (20k steps, SNR 0-15dB)
- `noisy`: Robust training with competing speech (25k steps, SNR -6-10dB) ⭐ **Default**

**Next Steps:**
1. ✅ ~~Train custom "Hey Saga" model~~ - Complete (using noisy tier)
2. Implement STT with faster-whisper
3. Integrate LLM on loki.local
4. Add TTS with Piper
5. Connect to Home Assistant API

---

**Last Updated:** November 2025
