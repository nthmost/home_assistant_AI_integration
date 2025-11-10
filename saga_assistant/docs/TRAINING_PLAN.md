# "Hey Saga" Model Training Plan

## Overview

Training a custom "Hey Saga" wakeword model using OpenWakeWord on loki.local's RTX 4080 GPU.

## Architecture

```
Mac mini M4                    loki.local (Ubuntu 22.04)
├─ saga_assistant/       ─────>  ~/saga_training/
│  ├─ Training configs           ├─ Python 3.12 venv
│  └─ Trained models  <────      ├─ PyTorch + CUDA 12.1
                                 ├─ OpenWakeWord
                                 ├─ Piper TTS
                                 ├─ Training datasets
                                 └─ RTX 4080 (16GB VRAM)
```

## Training Process

### Phase 1: Environment Setup ✅ (In Progress)

**On loki.local:**
1. Create `~/saga_training/` workspace
2. Set up Python 3.12 virtual environment
3. Install PyTorch with CUDA 12.1 support
4. Install Piper TTS for synthetic sample generation
5. Clone and install OpenWakeWord
6. Install training dependencies (speechbrain, audiomentations, etc.)
7. Download base embedding models

**Estimated Time:** 10-15 minutes
**Status:** Running (`setup_training_nosudo.sh`)

### Phase 2: Dataset Download 📋

**Required Datasets:**

1. **Synthetic Positive Samples** (Auto-generated)
   - Piper TTS will generate 5,000 "Hey Saga" samples
   - Multiple speakers, variations, accents
   - ~10 minutes generation time

2. **Background Noise** (~2GB)
   - AudioSet: Environmental sounds
   - Free Music Archive: Music samples
   - Used to augment synthetic samples

3. **Room Impulse Responses** (~100MB)
   - MIT RIR dataset
   - Simulates different room acoustics

4. **Negative Training Data** (~5GB)
   - Pre-computed OpenWakeWord features
   - ACAV100M dataset (2,000 hours of speech)
   - Validation set for false-positive testing

**Estimated Time:** 30-60 minutes (download + processing)
**Disk Space:** ~8GB total

### Phase 3: Sample Generation 📋

Using Piper TTS on loki.local:
- Generate 5,000 positive "Hey Saga" samples
- Generate 5,000 adversarial samples (similar-sounding phrases)
- Generate 1,000 validation samples
- Apply augmentations (noise, reverb, speed changes)

**Estimated Time:** 30-60 minutes (GPU-accelerated)

### Phase 4: Model Training 📋

**Configuration:** (`hey_saga_config.yaml`)
- Target phrase: "hey saga"
- Model type: DNN (deep neural network)
- Layer dim: 128
- Blocks: 2
- Training steps: 20,000
- Batch size: 512
- Learning rate: 0.001

**Training on RTX 4080:**
- GPU-accelerated PyTorch training
- Early stopping based on validation metrics
- Checkpoint averaging for best model selection

**Target Metrics:**
- Accuracy: ≥ 0.7
- Recall: ≥ 0.5
- False positives: ≤ 0.2 per hour

**Estimated Time:** 1-2 hours

### Phase 5: Model Export 📋

- Convert to ONNX format (for Mac mini M4)
- Convert to TFLite format (optional)
- Transfer model back to Mac mini
- Copy to `saga_assistant/models/hey_saga.onnx`

**Estimated Time:** 5 minutes

## Total Estimated Time

**Complete Training Pipeline:** 2-4 hours
- Setup: 15 min
- Dataset download: 1 hour
- Sample generation: 1 hour
- Training: 1-2 hours
- Export: 5 min

## Commands

### On loki.local (via SSH)

```bash
# Activate environment
source ~/saga_training/venv/bin/activate

# Download datasets
python download_datasets.py

# Generate samples
python openwakeword/openwakeword/train.py --training_config hey_saga_config.yaml --generate_clips

# Augment samples
python openwakeword/openwakeword/train.py --training_config hey_saga_config.yaml --augment_clips

# Train model
python openwakeword/openwakeword/train.py --training_config hey_saga_config.yaml --train_model

# Check GPU usage
nvidia-smi
```

### From Mac mini

```bash
# Transfer config to loki
scp saga_assistant/hey_saga_config.yaml loki.local:~/saga_training/

# Monitor training progress
ssh loki.local "tail -f ~/saga_training/training.log"

# Transfer trained model back
scp loki.local:~/saga_training/hey_saga_model/hey_saga.onnx saga_assistant/models/
```

## Testing Trained Model

Once the model is trained and transferred:

```bash
# On Mac mini
cd saga_assistant

# Test with demo script
pipenv run python demo_wakeword.py --model models/hey_saga.onnx

# Or modify demo script to load custom model:
# oww_model = Model(wakeword_models=["models/hey_saga.onnx"], inference_framework="onnx")
```

## Alternative Wakewords

If "Hey Saga" doesn't perform well, train alternatives:

1. **"Hey Eris"** - Different phonemes, may be easier to detect
2. **"Hey Cera"** - Softer sounds, different characteristics

Simply update `target_phrase` in `hey_saga_config.yaml` and re-run training.

## Optimization Tips

### For Better Performance

1. **Increase samples:** `n_samples: 10000` (longer generation time)
2. **More training steps:** `steps: 50000` (longer training)
3. **Download full datasets:** Complete AudioSet + FMA for better generalization
4. **Adjust threshold:** Lower threshold = more sensitive, higher = fewer false positives

### For Faster Training

1. **Reduce samples:** `n_samples: 2000` (faster but may reduce accuracy)
2. **Fewer steps:** `steps: 10000` (faster but may not converge fully)
3. **Smaller model:** `layer_dim: 64`, `n_blocks: 1`

## Monitoring

### Training Progress

The training script outputs:
- Step number
- Training loss
- Validation accuracy
- Validation recall
- False positive rate
- Best model checkpoints

### GPU Monitoring

```bash
# On loki.local
watch -n 1 nvidia-smi
```

Expected GPU usage:
- Utilization: ~80-100%
- Memory: ~2-4GB VRAM
- Temperature: <80°C

## Files

### On Mac mini (`saga_assistant/`)
- `hey_saga_config.yaml` - Training configuration
- `setup_training_nosudo.sh` - Setup script for loki.local
- `TRAINING_PLAN.md` - This document
- `models/hey_saga.onnx` - Trained model (after training)

### On loki.local (`~/saga_training/`)
- `venv/` - Python virtual environment
- `openwakeword/` - OpenWakeWord source
- `piper-sample-generator/` - Piper TTS
- `hey_saga_config.yaml` - Training config (transferred from Mac mini)
- `audioset_16k/` - Background audio dataset
- `fma/` - Music dataset
- `mit_rirs/` - Room impulse responses
- `*.npy` - Pre-computed negative features
- `hey_saga_model/` - Output directory with trained model

## Troubleshooting

### CUDA Out of Memory
- Reduce `batch_size` in config (try 256 or 128)
- Close other GPU processes on loki.local

### Piper TTS Errors
- Verify Piper model downloaded correctly
- Check `piper-sample-generator/models/en_US-libritts_r-medium.pt` exists

### Poor Detection Performance
- Increase `n_samples` for more training data
- Lower detection `threshold` in demo script
- Record your own voice saying "Hey Saga" and test

### Training Not Converging
- Increase `steps` to allow more training time
- Adjust `learning_rate` (try 0.0005 or 0.002)
- Check validation metrics - may be overfitting

---

**Status:** Phase 1 - Environment setup in progress on loki.local
**Next:** Wait for setup to complete, then download datasets
**Timeline:** Ready to test model in ~2-4 hours
