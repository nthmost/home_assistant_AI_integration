#!/usr/bin/env python3
"""
Integrated wake word training with built-in progress monitoring
Uses a unified log file that the monitor can always track
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
from datetime import datetime

# Configure logging to write to both file and stdout
LOG_FILE = "training.log"

# Custom formatter that adds emojis and clear phase markers
class TrainingFormatter(logging.Formatter):
    """Custom formatter with phase indicators"""

    PHASE_MARKERS = {
        'generate': '🎤 GENERATE',
        'augment': '🔊 AUGMENT',
        'train': '🧠 TRAIN',
        'complete': '🎉 COMPLETE',
        'check': '🔍 CHECK',
        'patch': '🔧 PATCH',
        'clean': '🧹 CLEAN',
    }

    def format(self, record):
        # Add phase marker if present
        if hasattr(record, 'phase'):
            record.phase_marker = self.PHASE_MARKERS.get(record.phase, '📝')
        else:
            record.phase_marker = '📝'

        return super().format(record)


# Set up dual logging (file + console)
def setup_logging():
    """Configure logging to file and console"""

    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Create formatters
    file_formatter = TrainingFormatter(
        '%(asctime)s | %(phase_marker)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_formatter = TrainingFormatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )

    # File handler
    file_handler = logging.FileHandler(LOG_FILE, mode='w')  # Overwrite each run
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Configure root logger
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return logging.getLogger(__name__)


logger = setup_logging()


class WakeWordTrainer:
    """Integrated wake word training with progress monitoring"""

    def __init__(self, config_path="openwakeword/examples/custom_model.yml"):
        self.config_path = Path(config_path)
        self.config = None
        self.output_config_path = None
        self.train_script = Path("openwakeword/openwakeword/train.py")
        self.current_phase = None

    def log_phase(self, phase, message, level=logging.INFO):
        """Log with phase marker"""
        self.current_phase = phase
        logger.log(level, message, extra={'phase': phase})

    def load_and_customize_config(self, wake_phrase, model_name, n_samples=5000):
        """Load example config and customize for target wake phrase"""
        self.log_phase('check', f"Loading config from {self.config_path}")

        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            return False

        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Customize config
        self.log_phase('check', f"Configuring for '{wake_phrase}'...")
        self.config["target_phrase"] = [wake_phrase]
        self.config["model_name"] = model_name
        self.config["n_samples"] = n_samples
        self.config["n_samples_val"] = max(1000, n_samples // 5)
        self.config["steps"] = 20000
        self.config["target_accuracy"] = 0.7
        self.config["target_recall"] = 0.5
        self.config["target_fp_per_hour"] = 0.2

        # Auto-detect background paths (check both old and new locations)
        background_paths = []
        for base in ['.', './data']:
            audioset_path = Path(base) / 'audioset_16k'
            fma_path = Path(base) / 'fma'
            if audioset_path.exists() and len(list(audioset_path.glob('*'))) > 0:
                background_paths.append(str(audioset_path))
            if fma_path.exists() and len(list(fma_path.glob('*'))) > 0:
                background_paths.append(str(fma_path))

        # Detect RIR path
        rir_path = "./mit_rirs" if Path("./mit_rirs").exists() else "./data/mit_rirs"

        # Detect feature files
        validation_features = "validation_set_features.npy" if Path("validation_set_features.npy").exists() else "data/validation_set_features.npy"
        acav_features = "openwakeword_features_ACAV100M_2000_hrs_16bit.npy" if Path("openwakeword_features_ACAV100M_2000_hrs_16bit.npy").exists() else "data/openwakeword_features_ACAV100M_2000_hrs_16bit.npy"

        self.config["background_paths"] = background_paths if background_paths else ['./data/fma']
        self.config["rir_paths"] = [rir_path]  # Note: plural 'rir_paths' not 'rir_path'
        self.config["false_positive_validation_data_path"] = validation_features
        self.config["feature_data_files"] = {
            "ACAV100M_sample": acav_features
        }
        self.config["piper_model_path"] = "./piper-sample-generator/models/en_US-libritts_r-medium.pt"

        # Save config
        self.output_config_path = f"{model_name}_training.yml"
        logger.info(f"Saving config to {self.output_config_path}")
        with open(self.output_config_path, 'w') as f:
            yaml.dump(self.config, f)

        return True

    def fix_sample_rates(self, clips_dir):
        """Fix sample rates of generated clips to ensure they're 16kHz"""
        self.log_phase('patch', f"{'='*70}")
        self.log_phase('patch', "Step 1.5: Fix Sample Rates")
        self.log_phase('patch', f"  Converting all clips to 16kHz")
        self.log_phase('patch', f"{'='*70}")

        clips_path = Path(clips_dir)
        if not clips_path.exists():
            self.log_phase('patch', f"Clips directory not found: {clips_dir}", logging.WARNING)
            return True

        fixed_count = 0
        error_count = 0

        # Process all .wav files recursively (clips are in subdirectories)
        for wav_file in clips_path.rglob('*.wav'):
            try:
                # Read the file
                with wave.open(str(wav_file), 'rb') as wf:
                    current_rate = wf.getframerate()

                    # Skip if already 16kHz
                    if current_rate == 16000:
                        continue

                    # Read audio data
                    frames = wf.readframes(wf.getnframes())
                    audio_data = np.frombuffer(frames, dtype=np.int16)

                # Resample to 16kHz
                if current_rate != 16000:
                    num_samples = int(len(audio_data) * 16000 / current_rate)
                    resampled = signal.resample(audio_data, num_samples)
                    resampled = resampled.astype(np.int16)

                    # Write back to file
                    with wave.open(str(wav_file), 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)  # 16-bit
                        wf.setframerate(16000)
                        wf.writeframes(resampled.tobytes())

                    fixed_count += 1
                    logger.debug(f"Fixed {wav_file.relative_to(clips_path)}: {current_rate}Hz → 16000Hz", extra={'phase': 'patch'})

            except Exception as e:
                error_count += 1
                logger.error(f"Error fixing {wav_file.relative_to(clips_path)}: {e}", extra={'phase': 'patch'})

        self.log_phase('patch', f"Fixed {fixed_count} files, {error_count} errors", logging.INFO)
        return error_count == 0

    def run_training_step_integrated(self, phase, step_name, args, description, check_onnx_on_error=False):
        """Run training step with integrated logging to training.log"""
        self.log_phase(phase, f"{'='*70}")
        self.log_phase(phase, step_name)
        self.log_phase(phase, f"  {description}")
        self.log_phase(phase, f"{'='*70}")

        # Run subprocess but redirect output to our log file and console
        process = subprocess.Popen(
            [sys.executable, str(self.train_script)] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Stream output line by line to both log and console
        for line in process.stdout:
            line = line.rstrip()
            # Write to log file with phase marker
            logger.debug(line, extra={'phase': phase})

        returncode = process.wait()

        if returncode != 0:
            # For training step, check if ONNX model was created despite error
            # (TFLite conversion may fail but ONNX model is what we need)
            if check_onnx_on_error and self.config:
                model_path = Path(self.config["output_dir"]) / f"{self.config['model_name']}.onnx"
                if model_path.exists():
                    self.log_phase(phase, f"ONNX model created successfully (TFLite conversion failed, but that's optional)", logging.WARNING)
                    return True

            self.log_phase(phase, f"FAILED with exit code {returncode}", logging.ERROR)
            return False

        self.log_phase(phase, f"Complete!", logging.INFO)
        return True

    def train(self, wake_phrase, model_name, n_samples=5000):
        """Execute full training pipeline"""

        self.log_phase('check', "="*70)
        self.log_phase('check', "Wake Word Model Training")
        self.log_phase('check', f"Phrase: {wake_phrase}")
        self.log_phase('check', f"Model: {model_name}")
        self.log_phase('check', f"Samples: {n_samples}")
        self.log_phase('check', "="*70)

        # Load config
        if not self.load_and_customize_config(wake_phrase, model_name, n_samples):
            return False

        clips_dir = Path(self.config["output_dir"]) / self.config["model_name"]

        # Step 1: Generate clips
        if not self.run_training_step_integrated(
            'generate',
            "Step 1: Generate Synthetic Clips",
            ["--training_config", self.output_config_path, "--generate_clips"],
            "Generating synthetic voice samples with Piper TTS"
        ):
            return False

        # Step 1.5: Fix sample rates (automated fix for common issue)
        if not self.fix_sample_rates(clips_dir):
            self.log_phase('patch', "Sample rate conversion had errors, but continuing...", logging.WARNING)

        # Step 1.6: Check if we need to clean incomplete features
        required_features = [
            clips_dir / "positive_features_train.npy",
            clips_dir / "positive_features_test.npy",
            clips_dir / "negative_features_train.npy",
            clips_dir / "negative_features_test.npy"
        ]

        missing_features = [f.name for f in required_features if not f.exists()]
        partial_features = [f for f in required_features if f.exists()]

        if missing_features and partial_features:
            # Some features exist but not all - this indicates incomplete augmentation
            self.log_phase('clean', f"Incomplete features detected, cleaning up...", logging.WARNING)
            for feature_file in partial_features:
                if feature_file.exists():
                    feature_file.unlink()
                    logger.debug(f"Removed incomplete: {feature_file.name}", extra={'phase': 'clean'})

        # Step 2: Augment clips
        if not self.run_training_step_integrated(
            'augment',
            "Step 2: Augment Clips",
            ["--training_config", self.output_config_path, "--augment_clips"],
            "Adding noise, reverb, and extracting features"
        ):
            return False

        # Step 3: Train model
        if not self.run_training_step_integrated(
            'train',
            "Step 3: Train Neural Network",
            ["--training_config", self.output_config_path, "--train_model"],
            f"Training on GPU for {self.config['steps']} steps",
            check_onnx_on_error=True  # TFLite conversion may fail, but ONNX is what we need
        ):
            return False

        # Get the model path
        model_path = Path(self.config["output_dir"]) / f"{self.config['model_name']}.onnx"

        self.log_phase('complete', "="*70)
        self.log_phase('complete', "🎉 Training Complete!")
        self.log_phase('complete', "="*70)
        self.log_phase('complete', "")
        self.log_phase('complete', f"✅ Model saved: {model_path}")
        self.log_phase('complete', f"📊 Model size: {model_path.stat().st_size / 1024:.1f} KB")
        self.log_phase('complete', "")
        self.log_phase('complete', "Next steps:")
        self.log_phase('complete', "")
        self.log_phase('complete', "1. Test the model locally:")
        self.log_phase('complete', f"   python3 test_wakeword.py --model {self.config['model_name']}")
        self.log_phase('complete', "")
        self.log_phase('complete', "2. Transfer to Mac mini for production:")
        self.log_phase('complete', f"   scp {model_path} mac-mini:~/projects/git/home_assistant_AI_integration/saga_assistant/models/")
        self.log_phase('complete', "")
        self.log_phase('complete', "3. Test with EMEET device:")
        self.log_phase('complete', f"   python3 demo_wakeword.py --model models/{self.config['model_name']}.onnx")
        self.log_phase('complete', "")
        self.log_phase('complete', "="*70)

        return True


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Train wake word with integrated monitoring",
        usage="%(prog)s PHRASE [options]"
    )
    parser.add_argument("phrase", help="Wake phrase (e.g., 'hey saga')")
    parser.add_argument("--model-name", help="Model name (default: auto-generated from phrase)")
    parser.add_argument("--samples", type=int, default=5000, help="Training samples (default: 5000)")

    args = parser.parse_args()

    # Auto-generate model name from phrase if not provided
    if not args.model_name:
        # Convert phrase to valid model name: "hey saga" -> "hey_saga"
        model_name = args.phrase.lower().replace(" ", "_").replace("-", "_")
        logger.info(f"Auto-generated model name: {model_name}")
    else:
        model_name = args.model_name

    logger.info(f"Logging to: {LOG_FILE}")
    logger.info("Monitor with: python3 monitor_training.py")
    logger.info("")

    trainer = WakeWordTrainer()

    if trainer.train(args.phrase, model_name, args.samples):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
