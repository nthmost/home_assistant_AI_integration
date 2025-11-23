# Squawkers Examples

Example code showing how to use the Squawkers module, including fun interactions between Saga and Squawkers!

## Fun Demos: Saga vs Squawkers 🎭

### The Argument (Print Version)
**File:** `saga_squawkers_argument.py`

A silly 10-act dramatic performance where Saga tries to have a serious discussion about Squawkers' behavior. Squawkers... does not cooperate. Saga's lines are printed (no voice).

```bash
pipenv run python squawkers/examples/saga_squawkers_argument.py
```

### The Argument (VOICE Version) 🔊
**File:** `saga_squawkers_argument_voice.py`

Same 10-act performance, but with Saga's REAL VOICE using Piper TTS!

**First time setup:** Download Saga's voice model:
```bash
cd saga_assistant && pipenv run python run_assistant.py
# Wait for initialization, then Ctrl+C
```

**Then run:**
```bash
pipenv run python squawkers/examples/saga_squawkers_argument_voice.py
```

### Simple Voice Demo 🔊
**File:** `saga_squawkers_simple_voice.py`

Quick 3-exchange demo with Saga's real voice. Perfect for testing!

```bash
pipenv run python squawkers/examples/saga_squawkers_simple_voice.py
```

## Running Examples

```bash
# From project root
pipenv run python squawkers/examples/simple_demo.py
pipenv run python squawkers/examples/usage_examples.py
```

## Available Examples

### `simple_demo.py`

Easy 3-command demo with configurable sequence.

**Modify the sequence at top of file:**
```python
PAUSE_DURATION = 5
DEMO_SEQUENCE = [
    "dance",
    "gag_a",
    "button_b",
]
```

Then run it!

### `usage_examples.py`

Various usage patterns showing:
- Basic usage
- Custom settings
- Test sequences
- Error handling
- Custom commands

## Quick Examples

### Basic Control

```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = Squawkers(client)

squawkers.dance()
squawkers.reset()
```

### All Commands

```python
from squawkers.squawkers_full import SquawkersFull

squawkers = SquawkersFull(client)

squawkers.dance()
squawkers.button_a()
squawkers.gag_b()
squawkers.command_c()
```

### Custom Sequence

```python
import time

squawkers.dance()
time.sleep(5)
squawkers.gag_a()
time.sleep(3)
squawkers.reset()
```

### Error Handling

```python
from squawkers import CommandError

try:
    squawkers.dance()
except CommandError as e:
    print(f"Failed: {e}")
```

## More Examples

See `docs/DEMO_SEQUENCES.md` for 15+ ready-to-use sequences.

## Create Your Own

Copy `simple_demo.py` and modify the sequence!

---

## About "The Argument"

**Cast:**
- 🤖 **Saga** - Your AI Assistant (British voice via Piper TTS, very patient)
- 🦜 **Squawkers McCaw** - Animatronic Parrot (chaotic, unpredictable)

**Plot:** Saga tries to have a serious discussion about Squawkers' behavior. Things escalate. Saga gets frustrated. Squawkers dances. Saga threatens to call Alexa. More chaos ensues. Eventually Saga surrenders and just wants quiet... but Squawkers keeps making noise!

**Acts:**
1. The Confrontation
2. The Escalation
3. The Upper Hand
4. The Protest
5. The Ultimatum
6. The Breakdown
7. The Threat
8. The Standoff
9. The Surrender
10. The Unwanted Noise
**FINALE** - One last surprise

**Technical notes:**
- Saga's voice: `en_GB-semaine-medium` (British female)
- Squawkers' responses: IR commands via Home Assistant Broadlink
- Audio output: EMEET OfficeCore M0 Plus (or default speaker)
- Timing is choreographed to let each response complete
- Squawkers' behavior has some randomness from the parrot hardware
