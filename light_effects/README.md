# Light Effects Library

A Python library for creating dynamic, programmable light effects with Home Assistant.

## Installation

```python
from light_effects import HomeAssistantClient, AdvancedEffects
```

## Quick Start

```python
# Initialize client
client = HomeAssistantClient('http://homeassistant.local:8123', 'YOUR_TOKEN')
effects = AdvancedEffects(client, 'light.tube_lamp')

# Run a surge effect
effects.surge('red', duration=5.0)

# Run a cascade effect
effects.cascade(duration=20.0)
```

## Components

### HomeAssistantClient

Low-level API wrapper for Home Assistant REST API.

**Methods:**
- `get_state(entity_id)` - Get current state of an entity
- `get_all_states()` - Get all entity states
- `light_turn_on(entity_id, **kwargs)` - Turn on light with parameters
- `light_turn_off(entity_id)` - Turn off light
- `switch_turn_on/off(entity_id)` - Control switches

### LightEffects

Basic light effect functions.

**Effects:**
- `smooth_transition(from_rgb, to_rgb, duration, steps)` - Smooth color blend
- `rainbow_cycle(duration_per_cycle, cycles, brightness)` - Rainbow rotation
- `pulse(color, min_brightness, max_brightness, duration, pulses)` - Breathing effect
- `gradient_flow(colors, duration_per_color, loops)` - Flow through color palette
- `strobe(color, interval, count)` - Rapid flashing

### AdvancedEffects

Extended effects for complex patterns and emotional responses.

**Effects:**

#### `surge(surge_type, duration, speed)`
Intense energy surge - rotates rapidly between 3 shades of a color family at maximum brightness.
Creates visceral emotional response.

**Surge Types:**
- **`red`** - Anger/Alert/Emergency - Use for critical alerts, errors, danger
- **`green`** - Life Force/Growth/Vitality - Use for success, growth, new life detected
- **`blue`** - Clarity/Cold/Precision - Use for analysis mode, data processing
- **`purple`** - Psychic/Mystery/Transcendence - Use for consciousness expansion, mystical events
- **`orange`** - Excitement/Warning/Energy - Use for warnings, high energy states
- **`cyan`** - Digital/Tech/Information - Use for system events, data streams, tech interactions

**Parameters:**
- `duration` (float): How long the surge lasts (seconds)
- `speed` (float): Time between color changes - lower = more intense (default: 0.08)

**Examples:**
```python
# Critical alert
effects.surge('red', duration=5.0, speed=0.05)

# System breakthrough
effects.surge('cyan', duration=3.0)

# Consciousness expansion
effects.surge('purple', duration=10.0, speed=0.1)
```

#### `cascade(duration)`
Cascade through rainbow colors rapidly. Creates flowing appearance through rapid color cycling.

**Parameters:**
- `duration` (float): How long to run the cascade (seconds)

**Example:**
```python
effects.cascade(duration=30.0)
```

#### Themed Flow Effects

- `ocean_swim(duration)` - Blues and cyans flowing
- `fire_swim(duration)` - Reds, oranges, yellows
- `aurora(duration)` - Greens and purples (northern lights)

## Preset Colors

Accessible via `COLORS` dictionary:
```python
from light_effects import COLORS

effects.pulse(COLORS['red'], ...)
```

Available colors: `red`, `green`, `blue`, `cyan`, `magenta`, `yellow`, `orange`, `purple`, `pink`, `white`, `warm_white`, `cool_white`

## Preset Gradients

Accessible via `GRADIENTS` dictionary:
```python
from light_effects import GRADIENTS

effects.gradient_flow(GRADIENTS['sunset'], ...)
```

Available gradients: `sunset`, `ocean`, `forest`, `fire`, `candy`

## Use Cases

### Psychedelic Internet of Things (PsIoT)

The surge effects are designed for dramatic state changes in consciousness-aware systems:

```python
# Reality shift detected
effects.surge('purple', duration=5.0)

# Life force surge (plant growth, biometric spike)
effects.surge('green', duration=8.0)

# System alert (sensor threshold exceeded)
effects.surge('red', duration=3.0, speed=0.05)

# Digital communication (data incoming)
effects.surge('cyan', duration=2.0)
```

### Home Automation Events

```python
# Someone arrives home
effects.rainbow_cycle(duration_per_cycle=5.0, cycles=1)

# Sunset detected
effects.gradient_flow(GRADIENTS['sunset'], duration_per_color=3.0, loops=1)

# Motion detected at night
effects.pulse(COLORS['warm_white'], min_brightness=100, max_brightness=255, pulses=3)

# Critical error (low battery, system offline)
effects.surge('red', duration=5.0)
```

## Demo Script

Run `python demo_effects.py` to see all basic effects in action.

## Architecture

```
light_effects/
├── __init__.py           # Package exports
├── ha_client.py          # Core API client + basic effects
├── advanced_effects.py   # Extended effects (surge, cascade, etc.)
├── demo_effects.py       # Demo script
└── README.md            # This file
```

## License

MIT
