# Example Demo Sequences

Copy-paste these into `demo_simple.py` to try different command combinations!

## How to Use

1. Open `demo_simple.py`
2. Find the `DEMO_SEQUENCE` list near the top
3. Replace it with one of these examples
4. Optionally adjust `PAUSE_DURATION`
5. Run: `pipenv run python squawkers/demo_simple.py`

## Example Sequences

### Dance Party
```python
PAUSE_DURATION = 10  # Longer pauses for dancing

DEMO_SEQUENCE = [
    "dance",
    "dance",
    "reset",
]
```

### Test Buttons
```python
PAUSE_DURATION = 3

DEMO_SEQUENCE = [
    "button_a",
    "button_b",
    "button_c",
]
```

### Test Gags
```python
PAUSE_DURATION = 4

DEMO_SEQUENCE = [
    "gag_a",
    "gag_b",
    "gag_c",
]
```

### Test Commands
```python
PAUSE_DURATION = 5

DEMO_SEQUENCE = [
    "command_a",
    "command_b",
    "command_c",
]
```

### Morning Wake Up
```python
PAUSE_DURATION = 5

DEMO_SEQUENCE = [
    "dance",       # Wake up with a dance
    "gag_a",       # First gag
    "button_a",    # Button A
    "reset",       # Calm down
]
```

### Party Mode
```python
PAUSE_DURATION = 8

DEMO_SEQUENCE = [
    "dance",
    "gag_b",
    "dance",
    "button_c",
    "reset",
]
```

### Test All Button Types
```python
PAUSE_DURATION = 4

DEMO_SEQUENCE = [
    "button_a",    # Plain button
    "command_a",   # Command mode
    "gag_a",       # Gag mode
    "reset",       # Reset
]
```

### Quick Test
```python
PAUSE_DURATION = 3

DEMO_SEQUENCE = [
    "dance",
    "reset",
    "gag_a",
]
```

### Long Sequence
```python
PAUSE_DURATION = 5

DEMO_SEQUENCE = [
    "dance",
    "button_a",
    "button_b",
    "gag_a",
    "gag_b",
    "command_a",
    "reset",
]
```

### Investigate Buttons A-C
```python
PAUSE_DURATION = 6

DEMO_SEQUENCE = [
    "button_a",
    "reset",       # Reset between to hear difference
    "button_b",
    "reset",
    "button_c",
    "reset",
]
```

### Compare Gags vs Buttons
```python
PAUSE_DURATION = 5

DEMO_SEQUENCE = [
    "button_a",    # Plain button A
    "gag_a",       # Gag A
    "reset",       # Reset
    "button_b",    # Plain button B
    "gag_b",       # Gag B
    "reset",
]
```

### Dance Routine
```python
PAUSE_DURATION = 12  # Let it dance longer

DEMO_SEQUENCE = [
    "dance",
    "dance",
    "dance",
    "reset",
]
```

### Recording Test
```python
PAUSE_DURATION = 5

DEMO_SEQUENCE = [
    "record_command_a",   # Trigger record mode
    "record_response_a",  # Trigger response record
    "reset",
]
```

## Custom Sequence Template

```python
PAUSE_DURATION = 5  # Change as needed

DEMO_SEQUENCE = [
    "dance",      # Command 1
    "gag_a",      # Command 2
    "reset",      # Command 3
]
```

## All Available Commands

Run this to see all 32 available methods:
```bash
pipenv run python squawkers/squawkers_full.py
```

Or check `MY_COMMANDS.md` for the complete list.

## Pro Tips

### Shorter Pauses for Quick Tests
```python
PAUSE_DURATION = 2
```

### Longer Pauses for Observation
```python
PAUSE_DURATION = 10
```

### Reset Between Commands
Good for hearing distinct behaviors:
```python
DEMO_SEQUENCE = [
    "button_a",
    "reset",
    "button_b",
    "reset",
    "button_c",
    "reset",
]
```

### Dance Then Reset Pattern
```python
PAUSE_DURATION = 8

DEMO_SEQUENCE = [
    "dance",
    "reset",
    "gag_a",
    "reset",
]
```

## Discovering Behaviors

Use sequences like this to figure out what each button does:

```python
# Test Plain Buttons
PAUSE_DURATION = 6
DEMO_SEQUENCE = ["button_a", "reset", "button_b", "reset", "button_c", "reset"]

# Test Gags
PAUSE_DURATION = 6
DEMO_SEQUENCE = ["gag_a", "reset", "gag_b", "reset", "gag_c", "reset"]

# Test Commands
PAUSE_DURATION = 6
DEMO_SEQUENCE = ["command_a", "reset", "command_b", "reset", "command_c", "reset"]
```

Take notes on what each does!

## Creating Routines

Once you know what each command does, create fun routines:

```python
# Morning greeting
PAUSE_DURATION = 5
DEMO_SEQUENCE = [
    "dance",           # Wake up dance
    "button_b",        # Maybe a laugh?
    "gag_a",           # Fun sound
    "reset",           # Calm down
]

# Party routine
PAUSE_DURATION = 8
DEMO_SEQUENCE = [
    "dance",
    "gag_b",
    "dance",
    "button_c",
    "gag_a",
    "reset",
]
```

---

**Remember:** Edit `demo_simple.py` and paste one of these sequences, then run!

```bash
pipenv run python squawkers/demo_simple.py
```
