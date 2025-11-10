# Wake Word Training Tiers

## Overview

Training tiers allow you to train models optimized for different acoustic environments. All tiers are speaker-independent and work for anyone.

## Available Tiers

### `basic` (Default)
**Best for:** Quiet environments, testing, initial training

**Characteristics:**
- Standard background noise (music, ambient sounds)
- Signal-to-noise ratio: 0-15 dB
- Training steps: 20,000
- Faster training time

**Use when:**
- You primarily use voice assistant in quiet rooms
- Testing wake word detection
- Want faster training iterations

**Command:**
```bash
./train "hey saga"
# or explicitly:
./train "hey saga" --tier basic
```

### `noisy`
**Best for:** Real-world use, competing speech, noisy environments

**Characteristics:**
- Includes competing speech as background noise
- Lower signal-to-noise ratio: -6 to 10 dB (more challenging)
- Training steps: 25,000 (20% more for harder conditions)
- Longer training time but more robust results

**Use when:**
- Voice assistant used in family/shared spaces
- TV, radio, or conversations happening nearby
- Want maximum reliability in real-world conditions

**Command:**
```bash
./train "hey saga" --tier noisy
```

## Model Naming

Models are automatically named with tier suffix:
- `basic` tier → `hey_saga_basic.onnx`
- `noisy` tier → `hey_saga_noisy.onnx`

This lets you test different tiers and compare performance.

## Prerequisites for 'noisy' Tier

The `noisy` tier requires speech noise samples. Download them with:

```bash
cd ~/saga_training
source venv/bin/activate
python3 scripts/download_speech_noise.py
```

This downloads public domain audiobook samples and processes them into 16kHz chunks for training.

**Note:** If speech samples aren't available, training will continue with music/ambient noise only and log a warning.

## Comparing Tiers

Test both models to see which works better in your environment:

```bash
# Test basic model
python3 demo_wakeword.py --model models/hey_saga_basic.onnx --duration 60

# Test noisy model
python3 demo_wakeword.py --model models/hey_saga_noisy.onnx --duration 60
```

Generally:
- `basic`: Lower false positive rate in quiet environments
- `noisy`: Better detection with competing speech, slightly higher false positive rate

## Adding New Tiers

Tiers are defined in `train_wakeword_integrated.py` in the `TRAINING_TIERS` dictionary. Easy to add new tiers:

```python
TRAINING_TIERS = {
    'basic': {...},
    'noisy': {...},
    'your_new_tier': {
        'description': 'Your tier description',
        'include_speech_noise': True/False,
        'snr_range': (min_db, max_db),
        'steps': 20000,
    }
}
```

Then use with `--tier your_new_tier`.

## Technical Details

### Signal-to-Noise Ratio (SNR)
- **Higher SNR** (15 dB): Wake word is much louder than background
- **Lower SNR** (-6 dB): Wake word barely louder than background
- Training with low SNR creates models robust to noisy conditions

### Training Steps
More steps = more training iterations = better learning but longer time:
- `basic`: 20,000 steps (~45-60 min on RTX 4080)
- `noisy`: 25,000 steps (~60-75 min on RTX 4080)

### Background Noise Sources
- `basic`: FMA (music), AudioSet (ambient)
- `noisy`: All of above + speech_noise (audiobooks/podcasts)
