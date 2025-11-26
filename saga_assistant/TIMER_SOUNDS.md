# Custom Timer Sounds 🔔

Saga now supports **custom sounds** for different timer types! Each timer can play a unique, iconic sound when it expires.

## Features

✅ **10 Built-in Sounds** - Kitchen timer, tea kettle, meditation bowl, laundry chime, and more
✅ **Automatic Recognition** - Just say "laundry timer" and it plays the laundry sound
✅ **Default Mappings** - Common timer types pre-assigned to matching sounds
✅ **Extensible** - Add new timer types and assign sounds via database

## Usage

### Voice Commands

```text
"Hey Saga, set a laundry timer for 60 minutes"  → 🔔 Laundry chime
"Hey Saga, set a tea timer for 3 minutes"       → 🫖 Tea kettle whistle
"Hey Saga, set a meditation timer for 10 minutes" → 🧘 Singing bowl
"Hey Saga, set a workout timer for 30 minutes"  → 💪 Energetic ascending beeps
"Hey Saga, set a cooking timer for 15 minutes"  → 🍳 Friendly triple beep
"Hey Saga, set a kitchen timer for 5 minutes"   → ⏲️  Classic three-ding bell
"Hey Saga, set a pomodoro timer for 25 minutes" → ⏱️  Single decisive tone
"Hey Saga, set a parking timer for 2 minutes"   → 🚗 Urgent triple beep
"Hey Saga, set a bike timer for 45 minutes"     → 🚴 Bike bell - two dings
```

Generic "timer" uses the default pleasant two-tone beep.

## Available Sounds

| Sound Name | Description | Best For |
|-----------|-------------|----------|
| `laundry` | Pleasant two-tone doorbell chime | Laundry, cleaning tasks |
| `tea` | Tea kettle whistle | Tea, coffee, brewing |
| `meditation` | Singing bowl / meditation chime | Meditation, yoga, breathing exercises |
| `cooking` | Friendly triple beep | Cooking, baking |
| `kitchen` | Classic kitchen timer bell - three dings | General kitchen tasks |
| `workout` | Energetic ascending beeps | Exercise, workouts, circuits |
| `bike` | Bike bell - two short dings | Bike rides, outdoor activities |
| `pomodoro` | Work timer - single decisive tone | Work sessions, focus time |
| `parking` | Urgent alert - fast triple beep | Parking meters, urgent reminders |
| `default` | Generic pleasant two-tone beep | Generic timers |

## Architecture

### Components

1. **Sound Library** (`saga_assistant/sounds/timers/`)
   - 10 synthesized WAV files
   - Generated using numpy sine waves with harmonics
   - Each sound designed to be iconic and recognizable

2. **Database** (`~/.saga_assistant/timer_sounds.db`)
   - SQLite database storing timer_type → sound_name mappings
   - Pre-populated with sensible defaults
   - Extensible for custom mappings

3. **Timer Sound Manager** (`saga_assistant/timer_sounds.py`)
   - Manages sound assignments
   - Queries database for timer types
   - Returns sound file paths

4. **Integration** (`saga_assistant/run_assistant.py`)
   - Timer regex extracts timer types from voice commands
   - Timer expiration callback plays custom sound
   - Fallback to default sound if no mapping exists

### Timer Regex

```python
r"(?:set a |set |)(?:([a-z]+) |)timer for (\d+|one|two|...) (minute|second)s?"
```

Captures:
- Group 1: Timer type (optional) - e.g., "laundry", "tea", "meditation"
- Group 2: Duration - e.g., "60", "five", "twenty"
- Group 3: Unit - "minute" or "second"

### Database Schema

```sql
CREATE TABLE timer_sounds (
    timer_type TEXT PRIMARY KEY,
    sound_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP
);
```

## Testing

### Test All Sounds

Play all timer sounds to hear them:

```bash
pipenv run python saga_assistant/demo_timer_sounds.py
```

This will:
- Play each sound with description
- Show database mappings
- Verify all sounds exist

### Test Timer Parsing

Test that timer types are recognized:

```bash
pipenv run python -c "
from saga_assistant.run_assistant import SagaAssistant
assistant = SagaAssistant()

# Test various timer commands
test_commands = [
    'Set a laundry timer for 60 minutes',
    'Set a tea timer for 3 minutes',
    'Set a meditation timer for 10 minutes',
    'Set a workout timer for 30 minutes',
    'Set a timer for 5 minutes',  # Generic
]

for cmd in test_commands:
    print(f'{cmd}')
    result = assistant.check_power_phrases(cmd.lower())
    print(f'  → {result}')
    print()
"
```

### End-to-End Test

1. **Start Saga**:
   ```bash
   pipenv run python saga_assistant/run_assistant.py
   ```

2. **Test a short timer**:
   ```text
   "Hey Saga, set a laundry timer for 1 minute"
   ```

3. **Wait for expiration**: After 1 minute, you should hear the laundry chime (two-tone doorbell).

## Adding Custom Sounds

### Option 1: Map Existing Sound to New Timer Type

Use the database directly:

```bash
sqlite3 ~/.saga_assistant/timer_sounds.db

INSERT INTO timer_sounds (timer_type, sound_name)
VALUES ('pizza', 'kitchen');
```

Now "pizza timer" will use the kitchen bell sound.

### Option 2: Create New Sound

1. **Generate sound** (add to `saga_assistant/sounds/generate_timer_sounds.py`):

```python
def pizza_oven():
    """Pizza oven ding - Italian restaurant style."""
    sr = 44100
    # ... generate sound ...
    return sound_samples

# Add to main():
sounds = {
    # ... existing sounds ...
    "pizza": (pizza_oven(), "Pizza oven ding"),
}
```

2. **Regenerate sounds**:
   ```bash
   pipenv run python saga_assistant/sounds/generate_timer_sounds.py
   ```

3. **Add mapping**:
   ```bash
   sqlite3 ~/.saga_assistant/timer_sounds.db
   INSERT INTO timer_sounds (timer_type, sound_name)
   VALUES ('pizza', 'pizza');
   ```

## Implementation Details

### Sound Generation

Sounds are synthesized using:
- Pure sine waves for fundamentals
- Harmonics for richness (2x, 3x, 5x frequency)
- ADSR envelopes for natural attack/decay
- Sample rate: 44.1 kHz
- Format: 16-bit mono WAV

Example (kitchen timer):
```python
def kitchen_timer():
    """Classic kitchen timer bell - three dings."""
    sr = 44100
    dings = []

    for i in range(3):
        fundamental = 880  # A5
        tone = (
            generate_sine_tone(fundamental, 0.3, sr) * 0.5 +
            generate_sine_tone(fundamental * 2, 0.3, sr) * 0.3 +
            generate_sine_tone(fundamental * 3, 0.3, sr) * 0.2
        )
        tone = apply_envelope(tone, attack=0.01, release=0.4)
        dings.append(tone)
        # ... silence between dings ...

    return np.concatenate(dings)
```

### Audio Playback

WAV files are played using sounddevice:

```python
def _play_wav(self, wav_path: str):
    with wave.open(wav_path, 'rb') as wav_file:
        sample_rate = wav_file.getframerate()
        audio_data = wav_file.readframes(wav_file.getnframes())
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        audio_array = audio_array.astype(np.float32) / 32768.0

        sd.play(audio_array, samplerate=sample_rate, device=self.emeet_output)
        sd.wait()
```

## Future Enhancements

### Voice-Based Sound Selection

When a new timer type is detected, Saga could ask:

```text
User: "Hey Saga, set a pizza timer for 15 minutes"
Saga: "I don't have a sound for pizza timer yet. Would you like to pick one?"
User: "Yes"
Saga: "Say the number: 1 for kitchen bell, 2 for tea kettle, 3 for meditation bowl..."
User: "One"
Saga: "Got it! Pizza timers will use the kitchen bell sound."
```

This would require:
- `awaiting_followup` state management
- Sound enumeration and playback during selection
- Database update after user choice

### Sound Preview

Before the timer ends, Saga could play a sample:

```text
User: "Hey Saga, what sound does my laundry timer use?"
Saga: [Plays laundry chime]
```

### Per-Instance Sounds

Allow multiple timers of the same type with different sounds:

```text
User: "Hey Saga, set a work timer for 25 minutes with parking sound"
```

## Files

```
saga_assistant/
├── sounds/
│   ├── generate_timer_sounds.py    # Sound synthesis script
│   └── timers/
│       ├── bike.wav
│       ├── cooking.wav
│       ├── default.wav
│       ├── kitchen.wav
│       ├── laundry.wav
│       ├── meditation.wav
│       ├── parking.wav
│       ├── pomodoro.wav
│       ├── tea.wav
│       └── workout.wav
├── timer_sounds.py                 # Timer sound manager
├── timers.py                       # Timer management
├── run_assistant.py                # Main integration
├── demo_timer_sounds.py            # Testing script
└── TIMER_SOUNDS.md                 # This file

~/.saga_assistant/
└── timer_sounds.db                 # Timer type → sound mappings
```

## Credits

All sounds synthesized in-house using Python/NumPy - no external assets required!

---

**Status**: Production ready
**Created**: 2025-11-24
**Author**: Claude Code + nthmost
