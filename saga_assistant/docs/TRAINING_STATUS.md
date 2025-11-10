# Hey Saga Training - Current Status

**Last Updated:** 2025-11-09 20:38:32

## Current Phase: 🔊 Augmentation (Step 2/3)

### Progress
- **Phase:** Computing features for negative test samples
- **Progress:** 65% complete (40/62 batches)
- **Speed:** ~1.68 iterations/second
- **ETA:** ~13 seconds remaining for this batch

### Training Pipeline Status

✅ **Step 1: Generate Clips** - COMPLETE
- Synthetic "Hey Saga" voice samples generated with Piper TTS
- Positive and negative samples created
- All clips resampled to 16kHz

🔄 **Step 2: Augment Clips** - IN PROGRESS (65%)
- Adding noise and reverb to clips
- Extracting audio features
- Creating training-ready feature files

⏳ **Step 3: Train Model** - PENDING
- Neural network training on RTX 4080
- 20,000 training steps
- Will take 2-3 hours

## How to Monitor

```bash
# On loki.local, run in a separate terminal:
cd ~/saga_training
python3 monitor_training.py
```

The monitor will show:
- ✅ Clean display (no "DEBUG" prefix overflow)
- 📊 Progress bars and percentages
- 🎤 Current phase with emoji markers
- 📝 Recent activity feed

## Training Configuration

- **Wake Phrase:** "hey saga"
- **Model Name:** hey_saga
- **Training Samples:** 5,000
- **Validation Samples:** 1,000
- **Training Steps:** 20,000
- **Target Accuracy:** 70%
- **Target Recall:** 50%
- **Target False Positives:** 0.2 per hour

## Output Location

When training completes, the model will be saved to:
```
~/saga_training/my_custom_model/hey_saga.onnx
```

## Next Steps

### When Training Completes

1. **Transfer model to Mac mini:**
   ```bash
   scp ~/saga_training/my_custom_model/hey_saga.onnx \
       mac-mini:~/projects/git/home_assistant_AI_integration/saga_assistant/models/
   ```

2. **Test on loki.local:**
   ```bash
   python3 test_wakeword.py --model hey_saga
   ```

3. **Test with EMEET device (on Mac mini):**
   ```bash
   python3 demo_wakeword.py --model models/hey_saga.onnx
   ```

### If Training Fails

Don't panic! Just run the fix tool:
```bash
python3 fix.py
```

It will:
- Auto-detect your model (no need to remember the name!)
- Diagnose what went wrong
- Offer to fix it automatically
- Tell you exactly what to do next

## Training Additional Wake Words

Once "Hey Saga" is complete, you can train more wake words using the same process:

```bash
# Hey Eris
python3 train_wakeword_integrated.py --phrase "hey eris" --model-name hey_eris

# Hey Cera
python3 train_wakeword_integrated.py --phrase "hey cera" --model-name hey_cera
```

The datasets are already downloaded, so subsequent trainings will be faster!

## Logs

All training output is being written to:
```
~/saga_training/training.log
```

View recent activity:
```bash
tail -f training.log
```

## System Info

- **Server:** loki.local (Ubuntu 22.04)
- **GPU:** NVIDIA GeForce RTX 4080 (16GB VRAM)
- **Python:** 3.11.14 (piper-phonemize compatible)
- **Framework:** OpenWakeWord v0.6.0
- **TTS:** Piper (en_US-libritts_r-medium)

---

**Estimated Time to Completion:**
- Augmentation: ~15 minutes remaining
- Training: ~2-3 hours
- **Total:** ~3 hours from now
