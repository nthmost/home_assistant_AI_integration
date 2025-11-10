#!/usr/bin/env python3
"""
Interactive "Hey Saga" Model Training
Run this script on loki.local to train the wake word model with live progress
"""

import os
import sys
import yaml
import time
import subprocess
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich import print as rprint

console = Console()

def check_environment():
    """Verify the environment is ready"""
    console.print("\n[bold cyan]🔍 Checking environment...[/bold cyan]")

    checks = []

    # Check CUDA
    import torch
    cuda_available = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if cuda_available else "None"
    checks.append(("CUDA Available", "✓" if cuda_available else "✗", "green" if cuda_available else "red"))
    checks.append(("GPU", gpu_name, "green" if cuda_available else "red"))

    # Check piper-phonemize
    try:
        import piper_phonemize
        checks.append(("piper-phonemize", "✓", "green"))
    except ImportError:
        checks.append(("piper-phonemize", "✗", "red"))

    # Check openwakeword
    try:
        import openwakeword
        checks.append(("openwakeword", "✓", "green"))
    except ImportError:
        checks.append(("openwakeword", "✗", "red"))

    # Check required directories
    required_dirs = ["openwakeword", "piper-sample-generator"]
    for d in required_dirs:
        exists = Path(d).exists()
        checks.append((f"Dir: {d}", "✓" if exists else "✗", "green" if exists else "red"))

    # Display results
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Check", style="cyan")
    table.add_column("Status", justify="center")

    for name, status, color in checks:
        table.add_row(name, f"[{color}]{status}[/{color}]")

    console.print(table)

    # Return success if all critical checks passed
    return all(status == "✓" for name, status, color in checks if color == "red")


def create_config():
    """Create training configuration"""
    console.print("\n[bold cyan]📋 Creating training configuration...[/bold cyan]")

    config_path = Path("openwakeword/examples/custom_model.yml")
    if not config_path.exists():
        console.print("[red]Error: Config template not found![/red]")
        return None

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Customize for "Hey Saga"
    config["target_phrase"] = ["hey saga"]
    config["model_name"] = "hey_saga"
    config["n_samples"] = 5000
    config["n_samples_val"] = 1000
    config["steps"] = 20000
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

    output_config = "hey_saga_training.yml"
    with open(output_config, 'w') as f:
        yaml.dump(config, f)

    # Display config
    table = Table(title="Training Configuration", show_header=True)
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Target Phrase", str(config["target_phrase"]))
    table.add_row("Model Name", config["model_name"])
    table.add_row("Positive Samples", str(config["n_samples"]))
    table.add_row("Validation Samples", str(config["n_samples_val"]))
    table.add_row("Training Steps", str(config["steps"]))
    table.add_row("Target Accuracy", str(config["target_accuracy"]))

    console.print(table)
    console.print(f"\n[green]✓[/green] Config saved to: {output_config}")

    return output_config


def run_training_step(step_name, command, description, estimated_time):
    """Run a training step with live output"""
    console.print(f"\n[bold yellow]{'='*70}[/bold yellow]")
    console.print(f"[bold cyan]{step_name}[/bold cyan]")
    console.print(f"[dim]{description}[/dim]")
    console.print(f"[dim]Estimated time: {estimated_time}[/dim]")
    console.print(f"[bold yellow]{'='*70}[/bold yellow]\n")

    # Run command and stream output
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    start_time = time.time()

    for line in process.stdout:
        # Color-code output
        if "error" in line.lower() or "failed" in line.lower():
            console.print(f"[red]{line.rstrip()}[/red]")
        elif "warning" in line.lower():
            console.print(f"[yellow]{line.rstrip()}[/yellow]")
        elif "✓" in line or "success" in line.lower() or "complete" in line.lower():
            console.print(f"[green]{line.rstrip()}[/green]")
        elif "%" in line or "progress" in line.lower():
            console.print(f"[cyan]{line.rstrip()}[/cyan]")
        else:
            console.print(f"[dim]{line.rstrip()}[/dim]")

    process.wait()
    elapsed = time.time() - start_time

    if process.returncode == 0:
        console.print(f"\n[green]✓ {step_name} completed in {elapsed/60:.1f} minutes[/green]")
        return True
    else:
        console.print(f"\n[red]✗ {step_name} failed with exit code {process.returncode}[/red]")
        return False


def main():
    console.clear()

    # Header
    panel = Panel.fit(
        "[bold cyan]🎯 Hey Saga Wake Word Training[/bold cyan]\n"
        "[dim]Interactive training with live progress[/dim]",
        border_style="cyan"
    )
    console.print(panel)

    # Check environment
    if not check_environment():
        console.print("\n[red]Environment checks failed! Please fix the issues above.[/red]")
        return 1

    # Create config
    config_file = create_config()
    if not config_file:
        return 1

    # Confirm start
    console.print("\n[bold yellow]Ready to start training?[/bold yellow]")
    console.print("This will take approximately 2-3 hours total.")
    response = console.input("\n[cyan]Continue? (y/n):[/cyan] ")
    if response.lower() != 'y':
        console.print("[yellow]Training cancelled.[/yellow]")
        return 0

    train_script = str(Path("openwakeword/openwakeword/train.py"))

    # Step 1: Generate clips
    success = run_training_step(
        "Step 1: Generate Synthetic Clips",
        [sys.executable, train_script, "--training_config", config_file, "--generate_clips"],
        "Using Piper TTS to generate 5,000 'Hey Saga' samples with variations",
        "30-60 minutes"
    )
    if not success:
        return 1

    # Step 2: Augment clips
    success = run_training_step(
        "Step 2: Augment Clips",
        [sys.executable, train_script, "--training_config", config_file, "--augment_clips"],
        "Adding background noise, reverb, and audio augmentations",
        "10-20 minutes"
    )
    if not success:
        return 1

    # Step 3: Train model
    success = run_training_step(
        "Step 3: Train Model",
        [sys.executable, train_script, "--training_config", config_file, "--train_model"],
        "Training neural network on RTX 4080 with 20,000 steps",
        "60-90 minutes"
    )
    if not success:
        return 1

    # Success!
    console.print("\n" + "="*70)
    panel = Panel.fit(
        "[bold green]🎉 Training Complete![/bold green]\n\n"
        f"[cyan]Model saved to:[/cyan] my_custom_model/hey_saga.onnx\n\n"
        "[yellow]Next steps:[/yellow]\n"
        "1. Transfer model to Mac mini\n"
        "2. Test with demo_wakeword.py\n"
        "3. Try saying 'Hey Saga'!",
        border_style="green",
        title="Success"
    )
    console.print(panel)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Training interrupted by user[/yellow]")
        sys.exit(1)
