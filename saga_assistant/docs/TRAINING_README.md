# Wake Word Training Guide

Complete, repeatable process for training custom wake word models using OpenWakeWord and Piper TTS.

## Quick Start

```bash
# 1. One-time setup (on training machine with GPU)
./setup_py311.sh

# 2. Download datasets (8GB, ~30-60 minutes)
python3 download_datasets.py

# 3. Download base models
./download_base_models.sh

# 4. Train a wake word (2-3 hours total)
python3 train_wakeword.py --phrase "hey saga" --model-name hey_saga

# 5. Test the model
python3 test_wakeword.py --model hey_saga
```

## Prerequisites

### Hardware Requirements

**Training Machine (loki.local):**
- GPU: NVIDIA RTX 4080 or similar (CUDA support)
- RAM: 62GB recommended (minimum 16GB)
- Storage: ~20GB for datasets + models
- OS: Ubuntu 22.04 with Python 3.11

**Inference Machine (Mac mini M4):**
- macOS with Python 3.13
- Audio device: EMEET OfficeCore M0 Plus
- 16GB RAM

### Software Requirements

- Python 3.11 (training) / 3.13 (inference)
- PyTorch with CUDA 12.1
- piper-tts and piper-phonemize
- OpenWakeWord
- Standard ML libraries (numpy, scipy, etc.)

## Setup Process

### Step 1: Environment Setup

On the training machine:

```bash
cd ~/saga_training
python3.11 -m venv venv
source venv/bin/activate
./setup_py311.sh
```

This installs:
- PyTorch with CUDA support
- Piper TTS for voice synthesis
- OpenWakeWord training framework
- All ML dependencies

### Step 2: Dataset Download

Download training datasets (~8GB):

```bash
python3 download_datasets.py
```

Downloads:
- **MIT Room Impulse Responses** (100 files) - Adds acoustic realism
- **AudioSet** (background audio) - Noise augmentation
- **Free Music Archive** - Music backgrounds
- **ACAV100M features** (17GB) - Pre-computed negative samples
- **Validation features** (177MB) - False positive testing

Monitor progress:
```bash
python3 monitor_training.py
```

### Step 3: Download Base Models

```bash
./download_base_models.sh
```

Downloads OpenWakeWord base models:
- `melspectrogram.onnx` - Audio feature extraction
- `embedding_model.onnx` - Feature embeddings
- TFLite versions for mobile deployment

## Training a Wake Word

### Using the Unified Script (Recommended)

```bash
python3 train_wakeword.py \
  --phrase "hey saga" \
  --model-name hey_saga \
  --samples 5000
```

This script automatically:
1. ✅ Checks all prerequisites
2. ✅ Patches OpenWakeWord for Piper compatibility
3. ✅ Generates synthetic voice samples
4. ✅ Fixes sample rates (16kHz)
5. ✅ Augments with noise and reverb
6. ✅ Trains the neural network
7. ✅ Saves the final model

### Manual Step-by-Step (Advanced)

If you need fine control:

```bash
# 1. Generate config
python3 train_hey_saga.py  # Customize this for your phrase

# 2. Check sample rates
python3 check_sample_rates.py

# 3. Fix if needed
python3 fix_sample_rates.py

# 4. Continue training (picks up from last step)
python3 train_hey_saga.py
```

### Training Parameters

Key configuration options in the generated YAML:

```yaml
target_phrase: ["hey saga"]      # Your wake phrase
model_name: "hey_saga"           # Output model name
n_samples: 5000                  # Training samples (more = better, slower)
n_samples_val: 1000              # Validation samples
steps: 20000                     # Training iterations
target_accuracy: 0.7             # Minimum accuracy threshold
target_recall: 0.5               # Minimum recall threshold
target_fp_per_hour: 0.2          # Max false positives per hour
```

Adjust `n_samples` based on quality needs:
- **1000-2000**: Quick testing, lower quality
- **5000**: Good balance (default)
- **10000+**: Production quality, longer training

### Training Phases

**Phase 1: Sample Generation** (30-60 minutes)
- Generates synthetic voice clips using Piper TTS
- Creates positive samples (your wake phrase)
- Creates negative samples (similar-sounding phrases)
- Applies voice variations (pitch, speed, tone)

**Phase 2: Augmentation** (10-20 minutes)
- Adds background noise (music, speech, ambient)
- Applies room acoustics (reverb, echo)
- Mixes with various SNR levels
- Extracts OpenWakeWord features

**Phase 3: Neural Network Training** (60-90 minutes)
- Trains binary classifier on RTX 4080
- 20,000 training steps with early stopping
- Validates against 11 hours of false positive data
- Saves final ONNX model

### Monitoring Training

In a separate terminal:

```bash
python3 monitor_training.py
```

Shows real-time progress:
- Current phase (generate/augment/train)
- Progress bar and ETA
- Sample counts
- Training metrics (loss, accuracy)
- Recent activity log

## Output

Trained model saved to:
```
my_custom_model/hey_saga.onnx
```

## Testing

### On Training Machine

```bash
python3 test_wakeword.py --model hey_saga
```

### Transfer to Inference Machine

```bash
scp ~/saga_training/my_custom_model/hey_saga.onnx \
    mac-mini:~/projects/git/home_assistant_AI_integration/saga_assistant/models/
```

### Test on Mac mini

```bash
cd ~/projects/git/home_assistant_AI_integration/saga_assistant
python3 demo_wakeword.py --model models/hey_saga.onnx
```

## Training Multiple Wake Words

Train additional wake words with the same datasets:

```bash
# Train "Hey Eris"
python3 train_wakeword.py --phrase "hey eris" --model-name hey_eris

# Train "Hey Cera"
python3 train_wakeword.py --phrase "hey cera" --model-name hey_cera
```

All wake words share the same datasets, so only the sample generation and training phases run.

## Troubleshooting

### Sample Rate Errors

**Error:** `ValueError: Error! Clip does not have the correct sample rate!`

**Fix:**
```bash
python3 check_sample_rates.py
python3 fix_sample_rates.py
```

### Missing Base Models

**Error:** `NO_SUCHFILE: melspectrogram.onnx failed`

**Fix:**
```bash
./download_base_models.sh
```

### CUDA Not Available

**Error:** `Specified provider 'CUDAExecutionProvider' is not in available`

**Fix:**
- Check: `nvidia-smi`
- Reinstall PyTorch with CUDA: See setup_py311.sh

### Out of Memory

**Error:** `CUDA out of memory`

**Fix:**
- Reduce batch size in config:
  ```yaml
  tts_batch_size: 25  # Default: 50
  augmentation_batch_size: 8  # Default: 16
  ```

### Piper Model Missing

**Error:** `generate_samples() missing 1 required positional argument: 'model'`

**Fix:**
```bash
# Download Piper voice model
cd piper-sample-generator/models
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts/medium/en_US-libritts-medium.onnx
```

## File Structure

```
~/saga_training/
├── download_datasets.py          # Dataset downloader
├── download_base_models.sh       # OpenWakeWord base models
├── train_wakeword.py             # Main training script (use this!)
├── train_hey_saga.py             # Legacy manual script
├── monitor_training.py           # Training progress monitor
├── check_sample_rates.py         # Diagnostic tool
├── fix_sample_rates.py           # Sample rate fixer
├── patch_openwakeword.py         # Piper compatibility patch
├── setup_py311.sh                # Environment setup
│
├── openwakeword/                 # OpenWakeWord framework
├── piper-sample-generator/       # Piper TTS integration
├── my_custom_model/              # Output models
│   └── hey_saga.onnx
│
├── mit_rirs/                     # Room impulse responses
├── audioset_16k/                 # Background audio
├── fma/                          # Music backgrounds
├── openwakeword_features_*.npy   # Negative features
└── validation_set_features.npy   # Validation data
```

## Performance Tips

1. **Use GPU acceleration** - RTX 4080 provides ~10x speedup vs CPU
2. **Keep models loaded** - Set `OLLAMA_KEEP_ALIVE=-1` if running other services
3. **Monitor with dedicated terminal** - Use `monitor_training.py` in tmux/screen
4. **Run overnight** - Full training takes 2-3 hours
5. **Parallel training** - Can train multiple wake words sequentially

## Next Steps

After training:

1. **Test thoroughly** - Try various voices, accents, distances
2. **Measure metrics** - False positive rate, detection latency
3. **Integrate with Home Assistant** - Use in voice assistant pipeline
4. **Iterate** - Retrain with more samples if quality insufficient

## References

- [OpenWakeWord Documentation](https://github.com/dscripka/openwakeword)
- [Piper TTS](https://github.com/rhasspy/piper)
- [Training Notebook](https://github.com/dscripka/openWakeWord/blob/main/notebooks/automatic_model_training.ipynb)
