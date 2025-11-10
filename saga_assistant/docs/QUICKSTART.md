# Wake Word Training - Quick Start

Simple, user-friendly commands for training custom wake words.

## 🚀 New Users

```bash
# 1. Train a wake word (one command!)
python3 train_wakeword_integrated.py "hey saga"

# 2. Monitor progress (in another terminal)
python3 monitor_training.py
```

That's it! Training takes 2-3 hours total.

**Note:** Model name is auto-generated from the phrase ("hey saga" → "hey_saga").

## 🔧 If Something Goes Wrong

```bash
# Just run the fix tool
python3 fix.py
```

The fix tool will:
- ✅ Auto-detect your model (no need to remember the name!)
- ✅ Diagnose what's wrong
- ✅ Offer to fix it automatically
- ✅ Tell you exactly what to do next

### Common scenarios:

**Training failed partway through?**
```bash
python3 fix.py --auto
```

**Want to start over completely?**
```bash
python3 fix.py --full-reset
```

**Just clean up incomplete features?**
```bash
python3 fix.py --clean-features
```

## 📊 Monitor Training

The monitor shows real-time progress:

```bash
python3 monitor_training.py
```

Shows:
- Current phase (🎤 Generate, 🔊 Augment, 🧠 Train)
- Progress bars with percentages
- Sample counts
- Recent activity

## 🎯 Complete Workflow

### First Time Setup

```bash
# On loki.local (one time only)
./setup_py311.sh
python3 download_datasets.py
./download_base_models.sh
```

### Train Your First Wake Word

```bash
# Terminal 1: Start training
python3 train_wakeword_integrated.py "hey saga"

# Terminal 2: Monitor progress
python3 monitor_training.py
```

### Train Additional Wake Words

```bash
# Same datasets, new wake words - super simple!
python3 train_wakeword_integrated.py "hey eris"
python3 train_wakeword_integrated.py "hey cera"

# Or with custom model name (optional)
python3 train_wakeword_integrated.py "hey there" --model-name hey_custom
```

### If Training Fails

```bash
python3 fix.py
# Answer the prompts or use --auto for automatic fixes
```

## 🎨 User-Friendly Features

### Auto-Detection

No need to remember model names:
- **One model?** Fix tool uses it automatically
- **Multiple models?** Pick from a nice table

### Smart Diagnostics

Fix tool checks for:
- ✅ Incomplete feature files
- ✅ Wrong sample rates
- ✅ Missing clips
- ✅ Empty directories

### Clear Guidance

Every error tells you:
- What went wrong
- How to fix it
- The exact command to run

## 📁 Output

Trained model saved to:
```
my_custom_model/hey_saga.onnx
```

Transfer to Mac mini:
```bash
scp ~/saga_training/my_custom_model/hey_saga.onnx \
    mac-mini:~/projects/git/home_assistant_AI_integration/saga_assistant/models/
```

## ⚡ Quick Reference

| Command | What it does |
|---------|--------------|
| `python3 train_wakeword_integrated.py "hey X"` | Train wake word |
| `python3 monitor_training.py` | Watch progress |
| `python3 fix.py` | Fix any issues (interactive) |
| `python3 fix.py --auto` | Auto-fix issues |
| `python3 fix.py --full-reset` | Start completely over |
| `python3 download_datasets.py` | Get training data (one-time) |
| `./download_base_models.sh` | Get base models (one-time) |

## 💡 Tips

1. **Always use the integrated trainer** - `train_wakeword_integrated.py` instead of the old scripts
2. **Monitor in a separate terminal** - See progress in real-time
3. **Use tmux/screen for long training** - So you can disconnect and reconnect
4. **Fix tool is your friend** - When in doubt, just run `python3 fix.py`

## 🐛 Troubleshooting

### "No models found"
You haven't started training yet. Run the training command first.

### "Features already exist, skipping augmentation"
This means incomplete features are blocking progress. Run:
```bash
python3 fix.py --clean-features
```

### "Wrong sample rate"
Run:
```bash
python3 fix.py --fix-sample-rates
```

### "I broke everything"
Run:
```bash
python3 fix.py --full-reset
```
Then start training again.

## 🎓 Next Steps

After training completes:

1. **Test on loki.local**
   ```bash
   python3 test_wakeword.py --model hey_saga
   ```

2. **Transfer to Mac mini**
   ```bash
   scp my_custom_model/hey_saga.onnx mac-mini:~/...
   ```

3. **Test with EMEET device**
   ```bash
   python3 demo_wakeword.py --model models/hey_saga.onnx
   ```

4. **Integrate with Home Assistant**
   (Instructions coming soon!)
