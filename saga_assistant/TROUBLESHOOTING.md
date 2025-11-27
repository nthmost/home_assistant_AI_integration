# Saga Assistant - Troubleshooting Guide

## Audio Device Hangs / Unresponsive to Ctrl+C

### Symptoms
- Assistant stops responding after recording
- Ctrl+C doesn't stop the process
- Error message: `Error starting stream: Internal PortAudio error [PaErrorCode -9986]`
- Leaked semaphore warnings on shutdown

### Root Cause
macOS Core Audio / PortAudio gets into a bad state where:
1. The USB audio device (EMEET) becomes unresponsive
2. Audio read operations block indefinitely
3. The process can't handle interrupt signals while blocked

### Immediate Fix
```bash
# From another terminal
pkill -9 -f run_assistant
```

### Prevention: Use the Watchdog

Run the assistant through the watchdog wrapper for automatic recovery:

```bash
pipenv run python saga_assistant/watchdog_assistant.py
```

**What the watchdog does:**
- Monitors the assistant process
- Detects when it becomes unresponsive (30s timeout)
- Automatically force-kills and restarts it
- Limits restart attempts to prevent boot loops
- Forwards all output/logs normally

**Configuration** (in `watchdog_assistant.py`):
```python
HEARTBEAT_TIMEOUT = 30  # Seconds without activity = hung
RESTART_DELAY = 2  # Seconds between kill and restart
MAX_RESTART_ATTEMPTS = 3  # Max restarts per minute
```

### Long-term Solutions

**Option 1: Reset Core Audio when device fails**
```python
# In run_assistant.py, when PortAudio error occurs:
import subprocess
subprocess.run(["sudo", "killall", "coreaudiod"], check=False)
```

**Option 2: Add timeout to audio reads**
This requires using a non-blocking audio stream or threading with timeouts.

**Option 3: Use a different audio backend**
- PyAudio with ALSA (Linux only)
- sounddevice with different backend
- Direct CoreAudio bindings (complex)

### Hardware-Specific Issues

**EMEET OfficeCore M0 Plus:**
- Sometimes loses USB connection briefly
- macOS doesn't always auto-reconnect properly
- **Workaround:** Unplug and replug the device

**macOS Core Audio:**
- Can get confused when multiple apps use the same device
- Buffer underruns cause device to lock up
- **Workaround:** Close other audio apps (Zoom, Discord, etc.)

### Diagnostic Commands

**Check audio device status:**
```bash
system_profiler SPAudioDataType | grep -A10 "EMEET"
```

**Check for locked Core Audio:**
```bash
ps aux | grep coreaudiod
```

**Reset Core Audio (requires sudo):**
```bash
sudo killall coreaudiod
```

**Check leaked resources:**
```bash
# Look for leftover semaphores
ls -la /dev/shm/ 2>/dev/null || echo "No /dev/shm on macOS"
```

## Other Common Issues

### Wakeword Detection Too Sensitive

**Symptom:** False wakes from background noise

**Solution:** Adjust threshold in `run_assistant.py`:
```python
if prediction[self.wakeword_model_key] >= 0.5:  # Increase from 0.5 to 0.6 or 0.7
```

### STT Transcription Errors

**Symptom:** "LA" becomes "a toilet", etc.

**Solutions:**
1. Speak more clearly and slower
2. Move closer to microphone
3. Reduce background noise
4. Upgrade to larger Whisper model (medium or large)

### Response Generation Slow

**Symptom:** Long delay between command and response

**Possible causes:**
- LLM inference on loki.local is slow
- Network latency to loki.local
- Large/complex queries

**Solutions:**
1. Use faster model: `qwen2.5:3b` instead of `qwen2.5:7b`
2. Check network latency: `ping loki.local`
3. Use intent system instead of LLM when possible

## Getting Help

1. Check logs for specific error messages
2. Search this troubleshooting guide
3. Check `CLAUDE.md` for project standards
4. Create an issue with full error logs

## Known Limitations

- **Audio hangs:** Requires watchdog or manual restart
- **STT accuracy:** Limited by Whisper model and audio quality
- **macOS-specific:** Some issues don't occur on Linux
- **USB audio:** More prone to issues than built-in audio
