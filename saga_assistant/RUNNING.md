# Running Saga Assistant

## Recommended: With Watchdog (Auto-Recovery)

The watchdog automatically restarts the assistant if it becomes unresponsive due to audio device issues:

```bash
cd saga_assistant
pipenv run python watchdog_assistant.py
```

**Benefits:**
- Auto-restarts on hang (30s timeout)
- Handles audio device failures gracefully
- Prevents indefinite hangs
- Logs all restart attempts

## Direct (No Auto-Recovery)

```bash
cd saga_assistant
pipenv run python run_assistant.py
```

**Note:** If the audio device hangs, you'll need to manually kill the process:
```bash
# From another terminal
pkill -9 -f run_assistant
```

## Troubleshooting

If the assistant becomes unresponsive:
1. **With watchdog:** It will auto-restart after 30 seconds
2. **Without watchdog:** Use `pkill -9 -f run_assistant` from another terminal

See `TROUBLESHOOTING.md` for detailed help with common issues.

## What to Expect

```
============================================================
🎙️  Saga Voice Assistant is ready!
   Say 'Hey Saga' to activate
   Press Ctrl+C to exit
============================================================

👂 Listening for 'Hey Saga'...
✅ Wakeword detected! (score: 0.925)
🎤 Recording command (VAD auto-stop)...
   🔴 Speech detected, recording...
   ⏹️  Recording complete (2.8s)
🗣️  Transcribing...
   📝 You said: "How far is the drive to Big Sur?"
🔍 Checking for intent command...
   🚗 Road trip query detected (confidence: 0.90)
   💬🗺️ (1.21s): "The drive to Big Sur is 145 miles via CA-1..."
🔊 Speaking...
   ✅ Speech complete
👂 Listening for 'Hey Saga'...
```

## Voice Commands

### Weather
- "What's the weather?"
- "What's the weather tomorrow?"
- "Quick question, what's the weather?" (brief response)

### Road Trip Planning
- "How far is the drive to Sacramento?"
- "How long to Lake Tahoe?"
- "When should I leave for Big Sur?"
- "Quick question, how far to LA?" (brief response)

### Parking (SF only)
- "I parked on Valencia"
- "Where did I park?"
- "When do I need to move my car?"

### Home Assistant
- "Turn on the TV light"
- "Turn off the aqua lights"

### Timers
- "Set a timer for 5 minutes"
- "Set a tea timer for 3 minutes"

## Quick Question Mode

Prefix any question with "quick question" for brief responses:

| Normal | Quick |
|--------|-------|
| "In San Francisco, it's 72 degrees and sunny" | "Sunny, 72°F" |
| "The drive to LA is 382 miles via I-5. Takes about 6 hours." | "382 miles, 6 hours" |

## Stopping the Assistant

**With Ctrl+C:**
- Usually works fine
- May require 2-3 presses if processing

**If unresponsive:**
```bash
pkill -9 -f run_assistant
```

**With watchdog:**
- Ctrl+C stops both watchdog and assistant
- If hung, watchdog will auto-restart
