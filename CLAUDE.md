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

## Task Status Reporting

When working on long-running or multi-step tasks in this project, create a task status file for monitoring:

### Status File
- **Location:** `~/.claude-monitor/home_assistant.json`
- **Purpose:** Allows external monitoring of Claude Code progress
- **Monitored by:** `~/claude-monitor/monitor.py`
- **Note:** All projects deposit breadcrumbs in `~/.claude-monitor/` using project-specific filenames

### When to Create Status Files
- Multi-step tasks (3+ steps)
- Long-running operations (>30 seconds)
- Tasks that may need user intervention
- Background processes (training, downloads, builds)
- Wakeword model training (report progress during 20k+ step training)

### Status File Format

```json
{
  "task_name": "Training Hey Saga Wakeword Model",
  "status": "in_progress",
  "progress_percent": 45,
  "current_step": "Step 9000/20000 (45%)",
  "message": "Training neural network on GPU",
  "needs_attention": false,
  "updated_at": "2025-11-10T14:30:00Z"
}
```

### Status Values
- `pending` - Task queued but not started
- `in_progress` - Currently working on task
- `blocked` - Waiting for user input or external dependency
- `waiting` - Paused, will resume automatically
- `completed` - Task finished successfully
- `error` - Task failed, needs attention

### Required Fields
- `task_name` (string): Brief description of the task
- `status` (string): One of the status values above
- `updated_at` (string): ISO 8601 timestamp

### Optional Fields
- `progress_percent` (int): 0-100 completion percentage
- `current_step` (string): What's happening right now
- `message` (string): Additional context or status message
- `needs_attention` (bool): Set to `true` if user action required

### Update Frequency
- Update the file whenever status changes significantly
- For long operations (training), update every 5-10 seconds or every 500 steps
- Always update when transitioning between states
- Always update when `needs_attention` becomes `true`

### For Claude Code: Use Write Tool

**IMPORTANT:** When creating/updating status files, Claude Code should use the **Write tool** directly, NOT Bash with heredocs.

```python
# Use the Write tool with file_path and JSON content
# Example:
Write(
    file_path="/Users/username/.claude-monitor/home_assistant.json",
    content=json.dumps({
        "task_name": "Training Hey Saga Model",
        "status": "in_progress",
        "progress_percent": 45,
        "current_step": "Step 9000/20000",
        "message": "Training neural network",
        "needs_attention": False,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }, indent=2)
)
```

### Python Helper Function (For Scripts)

Add this to training scripts and long-running operations:

```python
import json
from pathlib import Path
from datetime import datetime, timezone

def update_task_status(
    task_name: str,
    status: str,
    progress_percent: int = None,
    current_step: str = None,
    message: str = None,
    needs_attention: bool = False,
    status_file: Path = Path.home() / '.claude-monitor' / 'home_assistant.json'
):
    """Update Claude task monitoring status file."""
    # Ensure directory exists
    status_file.parent.mkdir(parents=True, exist_ok=True)

    data = {
        'task_name': task_name,
        'status': status,
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    if progress_percent is not None:
        data['progress_percent'] = progress_percent
    if current_step:
        data['current_step'] = current_step
    if message:
        data['message'] = message
    if needs_attention:
        data['needs_attention'] = needs_attention

    with open(status_file, 'w') as f:
        json.dump(data, f, indent=2)
```

### Integration with Training Scripts

For training scripts that use tqdm or custom progress tracking:

```python
# Start of training
update_task_status(
    task_name="Training Hey Saga Model",
    status="in_progress",
    progress_percent=0,
    current_step="Loading training data"
)

# During training (update every 500 steps)
for step in range(total_steps):
    # ... training code ...
    if step % 500 == 0:
        progress = int((step / total_steps) * 100)
        update_task_status(
            task_name="Training Hey Saga Model",
            status="in_progress",
            progress_percent=progress,
            current_step=f"Step {step}/{total_steps}"
        )

# On completion
update_task_status(
    task_name="Training Hey Saga Model",
    status="completed",
    progress_percent=100,
    message="Model saved to models/hey_saga_noisy.onnx"
)
```

---

**Last Updated:** November 2025
