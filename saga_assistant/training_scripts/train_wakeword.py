#!/usr/bin/env python3
"""
Complete, repeatable wake word training pipeline
Handles all setup, validation, and training steps automatically
"""

import os
import sys
import yaml
import wave
import logging
import subprocess
import numpy as np
from pathlib import Path
from scipy import signal
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class WakeWordTrainer:
    """Complete wake word training pipeline"""

    def __init__(self, config_path="openwakeword/examples/custom_model.yml"):
        self.config_path = Path(config_path)
        self.config = None
        self.output_config_path = None
        self.train_script = Path("openwakeword/openwakeword/train.py")

    def load_and_customize_config(self, wake_phrase, model_name, n_samples=5000):
        """Load example config and customize for target wake phrase"""
        logger.info(f"📋 Loading config from {self.config_path}")

        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            return False

        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Customize config
        logger.info(f"🔧 Configuring for '{wake_phrase}'...")
        self.config["target_phrase"] = [wake_phrase]
        self.config["model_name"] = model_name
        self.config["n_samples"] = n_samples
        self.config["n_samples_val"] = max(1000, n_samples // 5)
        self.config["steps"] = 20000
        self.config["target_accuracy"] = 0.7
        self.config["target_recall"] = 0.5
        self.config["target_fp_per_hour"] = 0.2

        # Set paths - check which background audio is available
        background_paths = []
        if Path('./audioset_16k').exists() and len(list(Path('./audioset_16k').glob('*'))) > 0:
            background_paths.append('./audioset_16k')
        if Path('./fma').exists() and len(list(Path('./fma').glob('*'))) > 0:
            background_paths.append('./fma')

        self.config["background_paths"] = background_paths if background_paths else ['./fma']
        self.config["rir_path"] = "./mit_rirs"
        self.config["false_positive_validation_data_path"] = "validation_set_features.npy"
        self.config["feature_data_files"] = {
            "ACAV100M_sample": "openwakeword_features_ACAV100M_2000_hrs_16bit.npy"
        }
        self.config["piper_model_path"] = "./piper-sample-generator/models/en_US-libritts_r-medium.pt"

        # Save config
        self.output_config_path = f"{model_name}_training.yml"
        logger.info(f"💾 Saving config to {self.output_config_path}")
        with open(self.output_config_path, 'w') as f:
            yaml.dump(self.config, f)

        return True

    def check_prerequisites(self):
        """Verify all required files and directories exist"""
        logger.info("🔍 Checking prerequisites...")

        checks = []

        # Check datasets
        required_datasets = {
            "MIT RIRs": (Path("./mit_rirs"), True),  # (path, required)
            "AudioSet 16k": (Path("./audioset_16k"), False),  # Optional
            "FMA": (Path("./fma"), True),
            "Negative features": (Path("openwakeword_features_ACAV100M_2000_hrs_16bit.npy"), True),
            "Validation features": (Path("validation_set_features.npy"), True),
        }

        for name, (path, required) in required_datasets.items():
            exists = path.exists()
            if path.is_dir():
                has_content = len(list(path.glob("*"))) > 0 if exists else False
                passed = exists and has_content
            else:
                passed = exists

            checks.append((name, passed, required, f"{'Directory' if path.is_dir() else 'File'}: {path}"))

        # Check OpenWakeWord base models
        base_models = [
            "openwakeword/openwakeword/resources/models/melspectrogram.onnx",
            "openwakeword/openwakeword/resources/models/embedding_model.onnx",
        ]

        for model_path in base_models:
            path = Path(model_path)
            checks.append((path.name, path.exists(), True, f"Model: {path}"))

        # Check Piper model
        piper_model = Path(self.config["piper_model_path"])
        checks.append(("Piper TTS model", piper_model.exists(), True, f"Model: {piper_model}"))

        # Check training script
        checks.append(("Training script", self.train_script.exists(), True, f"Script: {self.train_script}"))

        # Display results
        all_passed = True
        warnings = []
        for name, passed, required, details in checks:
            if required:
                status = "✅" if passed else "❌"
                logger.info(f"  {status} {name}")
                if not passed:
                    logger.error(f"      Missing: {details}")
                    all_passed = False
            else:
                # Optional items
                status = "✅" if passed else "⚠️ "
                logger.info(f"  {status} {name}" + ("" if passed else " (optional)"))
                if not passed:
                    warnings.append(f"{name}: {details}")

        if not all_passed:
            logger.error("\n❌ Prerequisites check failed!")
            logger.info("\nTo fix:")
            logger.info("  1. Run: ./download_base_models.sh")
            logger.info("  2. Ensure datasets are downloaded")
            return False

        logger.info("✅ All prerequisites satisfied!")
        return True

    def patch_openwakeword_train(self):
        """Patch OpenWakeWord train.py to add model parameter"""
        logger.info("🔧 Patching OpenWakeWord train.py...")

        if not self.train_script.exists():
            logger.error(f"Training script not found: {self.train_script}")
            return False

        with open(self.train_script, 'r') as f:
            content = f.read()

        # Check if already patched
        if 'model=config.get("piper_model_path"' in content:
            logger.info("  ✅ Already patched!")
            return True

        # Apply patches
        patterns = [
            ('generate_samples(\n                text=config["target_phrase"],',
             'generate_samples(\n                text=config["target_phrase"],\n                model=config.get("piper_model_path", "./piper-sample-generator/models/en_US-libritts_r-medium.pt"),'),

            ('generate_samples(text=config["target_phrase"],',
             'generate_samples(text=config["target_phrase"],\n                             model=config.get("piper_model_path", "./piper-sample-generator/models/en_US-libritts_r-medium.pt"),'),

            ('generate_samples(text=adversarial_texts,',
             'generate_samples(text=adversarial_texts,\n                             model=config.get("piper_model_path", "./piper-sample-generator/models/en_US-libritts_r-medium.pt"),'),
        ]

        for pattern, replacement in patterns:
            content = content.replace(pattern, replacement)

        with open(self.train_script, 'w') as f:
            f.write(content)

        logger.info("  ✅ Patched successfully!")
        return True

    def resample_wav_file(self, input_path, target_rate=16000):
        """Resample a WAV file to target sample rate in-place"""
        with wave.open(str(input_path), 'rb') as wav:
            orig_rate = wav.getframerate()
            n_channels = wav.getnchannels()
            sampwidth = wav.getsampwidth()
            frames = wav.readframes(wav.getnframes())

        # If already at target rate, skip
        if orig_rate == target_rate:
            return False

        # Convert to numpy array
        if sampwidth == 2:  # 16-bit
            audio = np.frombuffer(frames, dtype=np.int16)
        else:
            raise ValueError(f"Unsupported sample width: {sampwidth}")

        # Handle stereo -> mono
        if n_channels == 2:
            audio = audio.reshape(-1, 2)
            audio = audio.mean(axis=1).astype(np.int16)

        # Resample
        num_samples = int(len(audio) * target_rate / orig_rate)
        resampled = signal.resample(audio, num_samples).astype(np.int16)

        # Write back
        with wave.open(str(input_path), 'wb') as wav:
            wav.setnchannels(1)  # Mono
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(target_rate)
            wav.writeframes(resampled.tobytes())

        return True

    def clean_incomplete_features(self, clips_dir):
        """Remove incomplete feature files to force regeneration"""
        clips_path = Path(clips_dir)
        if not clips_path.exists():
            return True

        # Check if feature files are incomplete
        required_features = [
            "positive_features_train.npy",
            "positive_features_test.npy",
            "negative_features_train.npy",
            "negative_features_test.npy",
        ]

        missing = []
        for feature_file in required_features:
            if not (clips_path / feature_file).exists():
                missing.append(feature_file)

        # If some but not all features exist, clean them (incomplete set)
        if missing and len(missing) < len(required_features):
            logger.warning("⚠️  Incomplete feature set detected - will regenerate")
            for feature_file in required_features:
                file_path = clips_path / feature_file
                if file_path.exists():
                    logger.info(f"  🗑️  Removing: {feature_file}")
                    file_path.unlink()
            return True

        return True

    def fix_sample_rates(self, clips_dir):
        """Ensure all clips are at 16kHz"""
        logger.info("🔧 Checking and fixing sample rates...")

        clips_path = Path(clips_dir)
        if not clips_path.exists():
            logger.info(f"  ⏭️  Clips directory doesn't exist yet: {clips_path}")
            return True

        total_fixed = 0

        for subdir in ["positive_train", "positive_test", "negative_train", "negative_test"]:
            subdir_path = clips_path / subdir
            if not subdir_path.exists():
                continue

            wav_files = list(subdir_path.glob("*.wav"))
            if not wav_files:
                continue

            fixed = 0
            for wav_file in tqdm(wav_files, desc=f"  {subdir}", leave=False):
                try:
                    if self.resample_wav_file(wav_file):
                        fixed += 1
                except Exception as e:
                    logger.error(f"    Error processing {wav_file.name}: {e}")

            if fixed > 0:
                logger.info(f"  ✅ {subdir}: Resampled {fixed}/{len(wav_files)} files")
                total_fixed += fixed

        if total_fixed > 0:
            logger.info(f"✅ Fixed {total_fixed} files total")
            # If we fixed sample rates, remove any existing features (they're invalid)
            self.clean_incomplete_features(clips_path)
        else:
            logger.info("✅ All clips already at 16kHz")

        return True

    def run_training_step(self, step_name, args, description, estimated_time):
        """Run a training step with proper logging"""
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"{step_name}")
        logger.info(f"  {description}")
        logger.info(f"  Estimated time: {estimated_time}")
        logger.info("=" * 70)
        logger.info("")

        result = subprocess.run(
            [sys.executable, str(self.train_script)] + args,
            cwd=os.getcwd()
        )

        if result.returncode != 0:
            logger.error(f"❌ {step_name} failed")
            return False

        logger.info(f"✅ {step_name} complete!")
        return True

    def train(self):
        """Execute full training pipeline"""
        logger.info("🚀 Starting training pipeline...")
        logger.info("=" * 70)

        clips_dir = Path(self.config["output_dir"]) / self.config["model_name"]

        # Step 1: Generate clips
        if not self.run_training_step(
            "📝 Step 1: Generate Synthetic Clips",
            ["--training_config", self.output_config_path, "--generate_clips"],
            "Using Piper TTS to generate positive and negative samples",
            "30-60 minutes"
        ):
            return False

        # Fix sample rates after generation
        if not self.fix_sample_rates(clips_dir):
            return False

        # Step 2: Augment clips
        if not self.run_training_step(
            "🔊 Step 2: Augment Clips",
            ["--training_config", self.output_config_path, "--augment_clips"],
            "Adding background noise, reverb, and audio augmentations",
            "10-20 minutes"
        ):
            return False

        # Step 3: Train model
        if not self.run_training_step(
            "🧠 Step 3: Train Model",
            ["--training_config", self.output_config_path, "--train_model"],
            f"Training neural network with {self.config['steps']} steps",
            "60-90 minutes"
        ):
            return False

        logger.info("")
        logger.info("=" * 70)
        logger.info("🎉 Training Complete!")
        logger.info("=" * 70)
        logger.info("")
        logger.info(f"Model saved to: {clips_dir.parent}/{self.config['model_name']}.onnx")
        logger.info("")

        return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Train a custom wake word model")
    parser.add_argument("--phrase", required=True, help="Wake phrase (e.g., 'hey saga')")
    parser.add_argument("--model-name", required=True, help="Model name (e.g., 'hey_saga')")
    parser.add_argument("--samples", type=int, default=5000, help="Number of training samples (default: 5000)")
    parser.add_argument("--skip-checks", action="store_true", help="Skip prerequisite checks")

    args = parser.parse_args()

    logger.info("🎯 Wake Word Model Training")
    logger.info("=" * 70)
    logger.info(f"Wake phrase: {args.phrase}")
    logger.info(f"Model name: {args.model_name}")
    logger.info(f"Training samples: {args.samples}")
    logger.info("")

    # Create trainer
    trainer = WakeWordTrainer()

    # Load and customize config
    if not trainer.load_and_customize_config(args.phrase, args.model_name, args.samples):
        return 1

    # Check prerequisites
    if not args.skip_checks:
        if not trainer.check_prerequisites():
            return 1
    else:
        logger.warning("⚠️  Skipping prerequisite checks")

    # Patch OpenWakeWord
    if not trainer.patch_openwakeword_train():
        return 1

    # Run training
    if not trainer.train():
        return 1

    logger.info("Next steps:")
    logger.info(f"1. Test the model: python3 test_wakeword.py --model {args.model_name}")
    logger.info("2. Transfer to deployment device")
    logger.info("")

    return 0


if __name__ == "__main__":
    sys.exit(main())
