#!/usr/bin/env python3
"""
Interactive troubleshooting and repair tool for wake word training

Usage:
  python3 fix.py              # Interactive mode
  python3 fix.py --auto       # Automatic detection and repair
  python3 fix.py --model hey_saga --clean-features
"""

import os
import sys
import shutil
import wave
import numpy as np
from pathlib import Path
from scipy import signal
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel

console = Console()


class TrainingDoctor:
    """Diagnose and fix training issues"""

    def __init__(self):
        self.models_dir = Path("my_custom_model")
        self.issues_found = []
        self.fixes_applied = []

    def find_models(self):
        """Find all models in training"""
        if not self.models_dir.exists():
            return []

        models = []
        for model_path in self.models_dir.iterdir():
            if model_path.is_dir() and not model_path.name.startswith('.'):
                models.append({
                    'name': model_path.name,
                    'path': model_path,
                    'clips_exist': self._check_clips(model_path),
                    'features_exist': self._check_features(model_path),
                    'model_exists': self._check_model(model_path),
                })
        return models

    def _check_clips(self, model_path):
        """Check if clips exist"""
        for subdir in ["positive_train", "positive_test", "negative_train", "negative_test"]:
            clips_path = model_path / subdir
            if clips_path.exists() and len(list(clips_path.glob("*.wav"))) > 0:
                return True
        return False

    def _check_features(self, model_path):
        """Check if all feature files exist"""
        required_features = [
            "positive_features_train.npy",
            "positive_features_test.npy",
            "negative_features_train.npy",
            "negative_features_test.npy",
        ]
        return all((model_path / f).exists() for f in required_features)

    def _check_model(self, model_path):
        """Check if final model exists"""
        model_file = model_path.parent / f"{model_path.name}.onnx"
        return model_file.exists()

    def select_model(self, models):
        """Let user select which model to work with"""
        if not models:
            console.print("[red]No models found in my_custom_model/[/red]")
            console.print("\nHave you started training yet?")
            console.print("Run: [cyan]python3 train_wakeword_integrated.py --phrase 'hey saga' --model-name hey_saga[/cyan]")
            return None

        if len(models) == 1:
            model = models[0]
            console.print(f"[cyan]Found one model:[/cyan] {model['name']}")
            return model

        # Multiple models - show table and ask
        table = Table(title="Available Models")
        table.add_column("Model", style="cyan")
        table.add_column("Clips", style="green")
        table.add_column("Features", style="yellow")
        table.add_column("Final Model", style="magenta")

        for i, model in enumerate(models, 1):
            table.add_row(
                f"{i}. {model['name']}",
                "✅" if model['clips_exist'] else "❌",
                "✅" if model['features_exist'] else "❌",
                "✅" if model['model_exists'] else "❌",
            )

        console.print(table)
        console.print()

        choice = Prompt.ask(
            "Which model?",
            choices=[str(i) for i in range(1, len(models) + 1)],
            default="1"
        )

        return models[int(choice) - 1]

    def diagnose(self, model):
        """Diagnose issues with the model"""
        console.print(f"\n[bold]🔍 Diagnosing model:[/bold] {model['name']}\n")

        issues = []

        # Check 1: Incomplete features
        if model['clips_exist'] and not model['features_exist']:
            issues.append({
                'type': 'incomplete_features',
                'title': 'Incomplete Feature Files',
                'description': 'Clips exist but feature extraction incomplete',
                'fix': 'Remove partial features and re-run augmentation',
                'severity': 'error'
            })

        # Check 2: Missing clips
        if not model['clips_exist']:
            issues.append({
                'type': 'missing_clips',
                'title': 'Missing Audio Clips',
                'description': 'No training clips found',
                'fix': 'Re-run clip generation',
                'severity': 'error'
            })

        # Check 3: Sample rate issues
        if model['clips_exist']:
            bad_rates = self._check_sample_rates(model['path'])
            if bad_rates:
                issues.append({
                    'type': 'bad_sample_rates',
                    'title': 'Incorrect Sample Rates',
                    'description': f'Found {bad_rates} clips not at 16kHz',
                    'fix': 'Resample all clips to 16kHz',
                    'severity': 'warning'
                })

        # Check 4: Empty directories
        empty_dirs = self._check_empty_dirs(model['path'])
        if empty_dirs:
            issues.append({
                'type': 'empty_dirs',
                'title': 'Empty Clip Directories',
                'description': f'Empty directories: {", ".join(empty_dirs)}',
                'fix': 'Remove empty directories',
                'severity': 'warning'
            })

        self.issues_found = issues
        return issues

    def _check_sample_rates(self, model_path):
        """Check for clips with wrong sample rate"""
        bad_count = 0
        for subdir in ["positive_train", "positive_test", "negative_train", "negative_test"]:
            clips_path = model_path / subdir
            if not clips_path.exists():
                continue

            for wav_file in list(clips_path.glob("*.wav"))[:10]:  # Sample first 10
                try:
                    with wave.open(str(wav_file), 'rb') as wav:
                        if wav.getframerate() != 16000:
                            bad_count += 1
                except:
                    pass

        return bad_count

    def _check_empty_dirs(self, model_path):
        """Find empty clip directories"""
        empty = []
        for subdir in ["positive_train", "positive_test", "negative_train", "negative_test"]:
            clips_path = model_path / subdir
            if clips_path.exists() and len(list(clips_path.glob("*.wav"))) == 0:
                empty.append(subdir)
        return empty

    def show_issues(self, issues):
        """Display found issues"""
        if not issues:
            console.print("✅ [green]No issues found![/green]")
            return

        console.print(f"\n[bold]Found {len(issues)} issue(s):[/bold]\n")

        for i, issue in enumerate(issues, 1):
            severity_color = "red" if issue['severity'] == 'error' else "yellow"
            console.print(f"[{severity_color}]{i}. {issue['title']}[/{severity_color}]")
            console.print(f"   {issue['description']}")
            console.print(f"   [dim]Fix: {issue['fix']}[/dim]")
            console.print()

    def fix_incomplete_features(self, model):
        """Remove incomplete feature files"""
        console.print("[cyan]Removing incomplete feature files...[/cyan]")

        features = [
            "positive_features_train.npy",
            "positive_features_test.npy",
            "negative_features_train.npy",
            "negative_features_test.npy",
        ]

        removed = 0
        for feature_file in features:
            file_path = model['path'] / feature_file
            if file_path.exists():
                file_path.unlink()
                console.print(f"  🗑️  Removed: {feature_file}")
                removed += 1

        if removed > 0:
            console.print(f"✅ Removed {removed} incomplete feature files")
            self.fixes_applied.append("Cleaned incomplete features")
        else:
            console.print("⏭️  No feature files to remove")

    def fix_sample_rates(self, model):
        """Resample all clips to 16kHz"""
        console.print("[cyan]Resampling clips to 16kHz...[/cyan]")

        from tqdm import tqdm

        total_fixed = 0
        for subdir in ["positive_train", "positive_test", "negative_train", "negative_test"]:
            clips_path = model['path'] / subdir
            if not clips_path.exists():
                continue

            wav_files = list(clips_path.glob("*.wav"))
            if not wav_files:
                continue

            fixed = 0
            for wav_file in tqdm(wav_files, desc=f"  {subdir}", leave=False):
                try:
                    if self._resample_file(wav_file):
                        fixed += 1
                except Exception as e:
                    console.print(f"  [red]Error: {wav_file.name} - {e}[/red]")

            if fixed > 0:
                console.print(f"  ✅ {subdir}: Resampled {fixed}/{len(wav_files)} files")
                total_fixed += fixed

        if total_fixed > 0:
            console.print(f"✅ Resampled {total_fixed} files total")
            self.fixes_applied.append(f"Resampled {total_fixed} clips")
            # Also clean features since they're now invalid
            self.fix_incomplete_features(model)
        else:
            console.print("✅ All clips already at 16kHz")

    def _resample_file(self, wav_path):
        """Resample a single WAV file to 16kHz"""
        with wave.open(str(wav_path), 'rb') as wav:
            orig_rate = wav.getframerate()
            if orig_rate == 16000:
                return False

            n_channels = wav.getnchannels()
            sampwidth = wav.getsampwidth()
            frames = wav.readframes(wav.getnframes())

        # Convert to numpy
        if sampwidth == 2:
            audio = np.frombuffer(frames, dtype=np.int16)
        else:
            raise ValueError(f"Unsupported sample width: {sampwidth}")

        # Handle stereo
        if n_channels == 2:
            audio = audio.reshape(-1, 2).mean(axis=1).astype(np.int16)

        # Resample
        num_samples = int(len(audio) * 16000 / orig_rate)
        resampled = signal.resample(audio, num_samples).astype(np.int16)

        # Write back
        with wave.open(str(wav_path), 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(resampled.tobytes())

        return True

    def fix_all(self, model, issues):
        """Fix all detected issues"""
        console.print("\n[bold cyan]Applying fixes...[/bold cyan]\n")

        for issue in issues:
            if issue['type'] == 'incomplete_features':
                self.fix_incomplete_features(model)
            elif issue['type'] == 'bad_sample_rates':
                self.fix_sample_rates(model)
            elif issue['type'] == 'empty_dirs':
                # Just informational, no fix needed
                pass
            elif issue['type'] == 'missing_clips':
                console.print("[yellow]Cannot auto-fix missing clips - need to re-run training[/yellow]")

    def full_reset(self, model):
        """Complete reset - delete everything for this model"""
        console.print(f"\n[bold red]⚠️  FULL RESET: {model['name']}[/bold red]")
        console.print("This will delete:")
        console.print("  - All generated clips")
        console.print("  - All feature files")
        console.print("  - Training progress")
        console.print("\n[yellow]The final .onnx model will be preserved[/yellow]")

        if not Confirm.ask("\nAre you sure?", default=False):
            console.print("Cancelled")
            return

        console.print(f"\n🗑️  Removing {model['path']}")
        shutil.rmtree(model['path'])
        console.print("✅ Full reset complete")
        console.print("\nRestart training with:")
        console.print(f"[cyan]python3 train_wakeword_integrated.py --phrase 'hey saga' --model-name {model['name']}[/cyan]")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fix training issues")
    parser.add_argument("--model", help="Model name (auto-detected if only one)")
    parser.add_argument("--auto", action="store_true", help="Auto-fix without prompts")
    parser.add_argument("--full-reset", action="store_true", help="Delete all training data")
    parser.add_argument("--clean-features", action="store_true", help="Remove feature files")
    parser.add_argument("--fix-sample-rates", action="store_true", help="Resample to 16kHz")

    args = parser.parse_args()

    doctor = TrainingDoctor()

    # Show header
    panel = Panel.fit(
        "[bold cyan]🔧 Training Problem Solver[/bold cyan]\n"
        "[dim]Diagnose and fix wake word training issues[/dim]",
        border_style="cyan"
    )
    console.print(panel)

    # Find models
    models = doctor.find_models()

    # Select model
    if args.model:
        model = next((m for m in models if m['name'] == args.model), None)
        if not model:
            console.print(f"[red]Model not found:[/red] {args.model}")
            return 1
    else:
        model = doctor.select_model(models)
        if not model:
            return 1

    # Handle specific actions
    if args.full_reset:
        doctor.full_reset(model)
        return 0

    if args.clean_features:
        doctor.fix_incomplete_features(model)
        return 0

    if args.fix_sample_rates:
        doctor.fix_sample_rates(model)
        return 0

    # Full diagnostic mode
    issues = doctor.diagnose(model)
    doctor.show_issues(issues)

    if not issues:
        return 0

    # Ask what to do
    if args.auto:
        should_fix = True
    else:
        should_fix = Confirm.ask("\nAttempt automatic fixes?", default=True)

    if should_fix:
        doctor.fix_all(model, issues)

        console.print("\n[bold green]✅ Fixes applied![/bold green]")
        if doctor.fixes_applied:
            console.print("\nWhat was fixed:")
            for fix in doctor.fixes_applied:
                console.print(f"  • {fix}")

        console.print("\n[cyan]Next step:[/cyan]")
        console.print(f"python3 train_wakeword_integrated.py --phrase 'hey saga' --model-name {model['name']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
