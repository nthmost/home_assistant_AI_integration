#!/bin/bash
# Reorganize saga_assistant directory for better UX

echo "Creating new directory structure..."

# Create subdirectories
mkdir -p training_scripts
mkdir -p docs

# Move training implementation scripts to training_scripts/
echo "Moving training scripts..."
mv train_wakeword_integrated.py training_scripts/ 2>/dev/null
mv download_datasets.py training_scripts/ 2>/dev/null
mv download_base_models.sh training_scripts/ 2>/dev/null
mv monitor_training.py training_scripts/ 2>/dev/null
mv fix.py training_scripts/ 2>/dev/null
mv patch_openwakeword.py training_scripts/ 2>/dev/null

# Move old/deprecated training scripts
mv train_wakeword.py training_scripts/ 2>/dev/null
mv train_hey_saga.py training_scripts/ 2>/dev/null
mv train_interactive.py training_scripts/ 2>/dev/null
mv check_sample_rates.py training_scripts/ 2>/dev/null
mv fix_sample_rates.py training_scripts/ 2>/dev/null
mv clean_training_artifacts.py training_scripts/ 2>/dev/null
mv monitor_downloads.py training_scripts/ 2>/dev/null

# Move setup scripts to training_scripts/
mv setup_py311.sh training_scripts/ 2>/dev/null
mv setup_training_loki.sh training_scripts/ 2>/dev/null
mv setup_training_nosudo.sh training_scripts/ 2>/dev/null
mv install_piper.sh training_scripts/ 2>/dev/null
mv finish_setup.sh training_scripts/ 2>/dev/null

# Move config files to training_scripts/
mv *.yml training_scripts/ 2>/dev/null
mv *.yaml training_scripts/ 2>/dev/null

# Move docs to docs/
echo "Moving documentation..."
mv QUICKSTART.md docs/ 2>/dev/null
mv TRAINING_README.md docs/ 2>/dev/null
mv TRAINING_PLAN.md docs/ 2>/dev/null
mv TRAINING_STATUS.md docs/ 2>/dev/null
mv WAKEWORD_SETUP.md docs/ 2>/dev/null
mv automatic_model_training.ipynb docs/ 2>/dev/null

# Keep these in root:
# - demo_wakeword.py (user-facing)
# - demo_audio_devices.py (user-facing)
# - models/ (trained models)
# - README.md (main docs)

echo ""
echo "✅ Reorganization complete!"
echo ""
echo "Root directory now contains:"
echo "  demo_wakeword.py       - Test wake word detection"
echo "  demo_audio_devices.py  - Check audio setup"
echo "  models/                - Trained models"
echo "  training_scripts/      - Training implementation"
echo "  docs/                  - Documentation"
echo ""
