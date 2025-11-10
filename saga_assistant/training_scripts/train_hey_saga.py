#!/usr/bin/env python3
"""
Train "Hey Saga" wake word model using OpenWakeWord
Based on automatic_model_training.ipynb
"""

import os
import sys
import yaml
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("🎯 Hey Saga Model Training")
    logger.info("="*60)

    # Load the example config and modify it for "Hey Saga"
    config_path = Path("openwakeword/examples/custom_model.yml")

    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        logger.info("Make sure you're in the ~/saga_training directory")
        return 1

    logger.info(f"📋 Loading config from {config_path}")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Modify for "Hey Saga"
    logger.info("🔧 Configuring for 'Hey Saga'...")
    config["target_phrase"] = ["hey saga"]
    config["model_name"] = "hey_saga"
    config["n_samples"] = 5000  # Number of positive samples
    config["n_samples_val"] = 1000  # Validation samples
    config["steps"] = 20000  # Training steps
    config["target_accuracy"] = 0.7
    config["target_recall"] = 0.5
    config["target_fp_per_hour"] = 0.2

    # Set paths
    config["background_paths"] = ['./audioset_16k', './fma']
    config["rir_path"] = "./mit_rirs"
    config["false_positive_validation_data_path"] = "validation_set_features.npy"
    config["feature_data_files"] = {
        "ACAV100M_sample": "openwakeword_features_ACAV100M_2000_hrs_16bit.npy"
    }

    # Set Piper TTS model
    config["piper_model_path"] = "./piper-sample-generator/models/en_US-libritts_r-medium.pt"

    # Save modified config
    output_config = "hey_saga_training.yml"
    logger.info(f"💾 Saving config to {output_config}")
    with open(output_config, 'w') as f:
        yaml.dump(config, f)

    logger.info("")
    logger.info("✅ Configuration ready!")
    logger.info("")
    logger.info("Configuration:")
    logger.info(f"  Target phrase: {config['target_phrase']}")
    logger.info(f"  Model name: {config['model_name']}")
    logger.info(f"  Positive samples: {config['n_samples']}")
    logger.info(f"  Validation samples: {config['n_samples_val']}")
    logger.info(f"  Training steps: {config['steps']}")
    logger.info("")

    logger.info("🚀 Starting training pipeline...")
    logger.info("="*60)

    # Now run the training script with our config
    train_script = Path("openwakeword/openwakeword/train.py")

    if not train_script.exists():
        logger.error(f"Training script not found: {train_script}")
        return 1

    # Step 1: Generate clips
    logger.info("")
    logger.info("📝 Step 1: Generating synthetic clips...")
    logger.info("   This will take ~30-60 minutes")
    logger.info("")

    import subprocess
    result = subprocess.run(
        [sys.executable, str(train_script), "--training_config", output_config, "--generate_clips"],
        cwd=os.getcwd()
    )

    if result.returncode != 0:
        logger.error("❌ Failed to generate clips")
        return 1

    logger.info("✅ Clip generation complete!")

    # Step 2: Augment clips
    logger.info("")
    logger.info("🔊 Step 2: Augmenting clips with noise and reverb...")
    logger.info("   This will take ~10-20 minutes")
    logger.info("")

    result = subprocess.run(
        [sys.executable, str(train_script), "--training_config", output_config, "--augment_clips"],
        cwd=os.getcwd()
    )

    if result.returncode != 0:
        logger.error("❌ Failed to augment clips")
        return 1

    logger.info("✅ Clip augmentation complete!")

    # Step 3: Train model
    logger.info("")
    logger.info("🧠 Step 3: Training model on RTX 4080...")
    logger.info("   This will take ~1-2 hours")
    logger.info("")

    result = subprocess.run(
        [sys.executable, str(train_script), "--training_config", output_config, "--train_model"],
        cwd=os.getcwd()
    )

    if result.returncode != 0:
        logger.error("❌ Training failed")
        return 1

    logger.info("")
    logger.info("="*60)
    logger.info("🎉 Training complete!")
    logger.info("="*60)
    logger.info("")
    logger.info(f"Model saved to: my_custom_model/{config['model_name']}.onnx")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Transfer model to Mac mini:")
    logger.info(f"   scp ~/saga_training/my_custom_model/{config['model_name']}.onnx mac-mini:~/projects/git/home_assistant_AI_integration/saga_assistant/models/")
    logger.info("2. Test with demo_wakeword.py")
    logger.info("")

    return 0

if __name__ == "__main__":
    sys.exit(main())
