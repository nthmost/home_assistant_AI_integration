#!/usr/bin/env python3
"""
Monitor dataset downloads and training progress with a nice visual interface
Watches multiple log files and adapts display based on current phase
"""

import os
import sys
import time
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.console import Group

console = Console()

def parse_wget_line(line):
    """Parse wget progress line to extract info"""
    match = re.search(r'(\d+)K\s+\.+.*?(\d+)%\s+([\d.]+[KMG])\s+([\dms]+)', line)
    if match:
        downloaded_kb = int(match.group(1))
        percent = int(match.group(2))
        speed = match.group(3)
        eta = match.group(4)
        return {
            'downloaded': downloaded_kb,
            'percent': percent,
            'speed': speed,
            'eta': eta
        }
    return None

def parse_training_progress(line):
    """Parse training progress from tqdm or other progress indicators"""
    # Look for patterns like: "Step 1500/20000 (7.5%) | Loss: 0.234 | Acc: 0.89"
    step_match = re.search(r'Step (\d+)/(\d+)', line)
    if step_match:
        current = int(step_match.group(1))
        total = int(step_match.group(2))
        percent = int((current / total) * 100)

        # Try to extract loss and accuracy
        loss = None
        acc = None
        loss_match = re.search(r'Loss[:\s]+([\d.]+)', line, re.IGNORECASE)
        acc_match = re.search(r'Acc(?:uracy)?[:\s]+([\d.]+)', line, re.IGNORECASE)

        if loss_match:
            loss = float(loss_match.group(1))
        if acc_match:
            acc = float(acc_match.group(1))

        return {
            'step': current,
            'total_steps': total,
            'percent': percent,
            'loss': loss,
            'accuracy': acc
        }

    # Look for tqdm-style progress: "75%|████████▌  | 15000/20000 [12:34<3:21, 24.7it/s]"
    tqdm_match = re.search(r'(\d+)%\|[^|]+\|\s*(\d+)/(\d+)\s*\[([^\]]+)\]', line)
    if tqdm_match:
        percent = int(tqdm_match.group(1))
        current = int(tqdm_match.group(2))
        total = int(tqdm_match.group(3))
        return {
            'step': current,
            'total_steps': total,
            'percent': percent,
            'loss': None,
            'accuracy': None
        }

    # Look for simple percentage: "45% complete" or "Progress: 67%"
    percent_match = re.search(r'(\d+)%', line)
    if percent_match:
        percent = int(percent_match.group(1))
        return {
            'step': None,
            'total_steps': None,
            'percent': percent,
            'loss': None,
            'accuracy': None
        }

    # Look for "X/Y" style progress
    fraction_match = re.search(r'(\d+)/(\d+)', line)
    if fraction_match:
        current = int(fraction_match.group(1))
        total = int(fraction_match.group(2))
        if total > 0:
            percent = int((current / total) * 100)
            return {
                'step': current,
                'total_steps': total,
                'percent': percent,
                'loss': None,
                'accuracy': None
            }

    return None

def format_size(kb):
    """Format KB to human readable"""
    if kb < 1024:
        return f"{kb}K"
    elif kb < 1024 * 1024:
        return f"{kb/1024:.1f}M"
    else:
        return f"{kb/(1024*1024):.2f}G"

def get_log_status(log_files):
    """Get current status from all available log files"""
    status = {
        'mode': 'unknown',  # download, generate, augment, train, complete
        'phase': 'Unknown',
        'wake_word': None,  # Extract wake word being trained
        'current_file': 'Unknown',
        'download_progress': None,
        'training_progress': None,
        'recent_activity': []
    }

    # Check each log file
    for log_name, log_path in log_files.items():
        if not Path(log_path).exists():
            continue

        try:
            with open(log_path, 'r') as f:
                lines = f.readlines()[-100:]
        except:
            continue

        # First pass: detect current phase and wake word (check most recent lines first)
        for line in reversed(lines):
            line = line.strip()

            # Extract wake word from "Phrase: hey saga"
            if not status['wake_word'] and 'Phrase:' in line:
                parts = line.split('Phrase:')
                if len(parts) > 1:
                    wake_word = parts[1].strip()
                    # Clean up any emoji or extra formatting
                    wake_word = wake_word.split('|')[0].strip()
                    if wake_word and len(wake_word) < 50:  # Sanity check
                        status['wake_word'] = wake_word

            # Detect training phases from emoji markers
            if '🧠 TRAIN' in line and status['mode'] == 'unknown':
                status['mode'] = 'train'
                status['phase'] = 'Training: Neural Network'
                break
            elif '🔊 AUGMENT' in line and status['mode'] == 'unknown':
                status['mode'] = 'augment'
                status['phase'] = 'Augmenting: Adding Noise & Reverb'
                break
            elif '🔧 PATCH' in line and status['mode'] == 'unknown':
                status['mode'] = 'patch'
                status['phase'] = 'Fixing: Sample Rates'
                break
            elif '🎤 GENERATE' in line and status['mode'] == 'unknown':
                status['mode'] = 'generate'
                status['phase'] = 'Generating: Synthetic Voice Clips'
                break
            elif '🎉 COMPLETE' in line and status['mode'] == 'unknown':
                status['mode'] = 'complete'
                status['phase'] = 'Complete: Model Ready'
                break

        # Second pass: collect progress and activity
        for line in reversed(lines):
            line = line.strip()

            # Detect phase from log content
            if 'dataset_download' in log_name:
                if 'All datasets downloaded' in line:
                    status['mode'] = 'download_complete'
                elif '📦 FILE:' in line:
                    status['mode'] = 'download'
                    # Extract filename
                    parts = line.split('FILE:')
                    if len(parts) > 1:
                        filename_part = parts[1].strip()
                        if '(' in filename_part:
                            filename_part = filename_part.split('(')[0].strip()
                        status['current_file'] = filename_part

                # Parse download progress
                if status['mode'] == 'download' and not status['download_progress']:
                    progress = parse_wget_line(line)
                    if progress:
                        status['download_progress'] = progress

                # Detect download phases
                if 'Downloading MIT Room' in line:
                    status['phase'] = 'Downloading: MIT Room Impulse Responses'
                elif 'Downloading AudioSet' in line:
                    status['phase'] = 'Downloading: AudioSet (Background Audio)'
                elif 'Downloading Free Music' in line:
                    status['phase'] = 'Downloading: Free Music Archive'
                elif 'Downloading pre-computed' in line:
                    status['phase'] = 'Downloading: Pre-computed Features'
                elif 'Converting to 16kHz' in line:
                    status['phase'] = 'Converting: AudioSet to 16kHz'
                elif 'Extracting' in line:
                    status['phase'] = 'Extracting: Archive'

            elif 'training' in log_name or 'train' in log_name or 'nohup' in log_name or 'stdout' in log_name:
                # Parse training progress
                if status['mode'] in ['generate', 'augment', 'train']:
                    progress = parse_training_progress(line)
                    if progress and not status['training_progress']:
                        status['training_progress'] = progress

            # Collect recent activity (from any log)
            if len(status['recent_activity']) < 8:
                if any(keyword in line for keyword in ['✅', '❌', '📦', 'Step', 'Complete', 'Loss', 'Accuracy',
                                                        'Generating', 'Augmenting', 'Training', '%', 'clips']):
                    # Strip timestamp, emoji markers, and log levels - just keep the actual message
                    display_line = line
                    if '|' in line:
                        parts = line.split('|')
                        # Format: "HH:MM:SS | 🧠 TRAIN | DEBUG | message (may contain | in progress bar)"
                        # Join all parts after the first 3 (timestamp, emoji, level)
                        if len(parts) >= 4:
                            # Skip timestamp, emoji, level - keep message (join rest with |)
                            display_line = '|'.join(parts[3:]).strip()
                        elif len(parts) >= 3:
                            # Fallback: join from part 2 onwards
                            display_line = '|'.join(parts[2:]).strip()

                    # Skip duplicate lines and filter out noise
                    if display_line and display_line not in status['recent_activity']:
                        # Skip if it's just a log level marker
                        if display_line not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
                            # Also skip if it's empty or too short
                            if len(display_line) > 3:
                                status['recent_activity'].insert(0, display_line)

    return status

def create_display(status):
    """Create rich display table based on current mode"""

    # Determine title based on mode - include wake word if available
    if status['wake_word']:
        wake_word_display = f"'{status['wake_word']}'"
    else:
        wake_word_display = ""

    titles = {
        'download': f'📥 Dataset Download {wake_word_display}',
        'download_complete': f'✅ Downloads Complete {wake_word_display}',
        'generate': f'🎤 Generating Samples {wake_word_display}',
        'patch': f'🔧 Fixing Sample Rates {wake_word_display}',
        'augment': f'🔊 Augmenting Audio {wake_word_display}',
        'train': f'🧠 Training Model {wake_word_display}',
        'complete': f'🎉 Training Complete {wake_word_display}',
        'unknown': '⏳ Monitoring'
    }
    title = titles.get(status['mode'], '⏳ Monitoring')

    table = Table(title=title, show_header=False, border_style="cyan")
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value", style="white")

    table.add_row("Current Phase", f"[yellow]{status['phase']}[/yellow]")

    # Show file for downloads
    if status['mode'] in ['download', 'download_complete']:
        table.add_row("Current File", f"[cyan]{status['current_file']}[/cyan]")

    # Show download progress
    if status['download_progress']:
        p = status['download_progress']
        downloaded_str = format_size(p['downloaded'])
        progress_bar = "█" * (p['percent'] // 2) + "░" * (50 - p['percent'] // 2)
        table.add_row("Progress", f"[green]{progress_bar}[/green] {p['percent']}%")
        table.add_row("Downloaded", f"[green]{downloaded_str}[/green]")
        table.add_row("Speed", f"[cyan]{p['speed']}/s[/cyan]")
        table.add_row("ETA", f"[yellow]{p['eta']}[/yellow]")

    # Show training progress
    elif status['training_progress']:
        p = status['training_progress']
        progress_bar = "█" * (p['percent'] // 2) + "░" * (50 - p['percent'] // 2)
        table.add_row("Progress", f"[green]{progress_bar}[/green] {p['percent']}%")

        # Show step counts if available
        if p['step'] is not None and p['total_steps'] is not None:
            table.add_row("Samples", f"[cyan]{p['step']:,} / {p['total_steps']:,}[/cyan]")

        # Show loss and accuracy if available
        if p['loss'] is not None:
            table.add_row("Loss", f"[yellow]{p['loss']:.4f}[/yellow]")
        if p['accuracy'] is not None:
            table.add_row("Accuracy", f"[green]{p['accuracy']:.2%}[/green]")
    else:
        # Show status message based on current mode
        status_messages = {
            'generate': "[cyan]Generating synthetic clips with Piper TTS...[/cyan]",
            'patch': "[cyan]Converting audio files to 16kHz...[/cyan]",
            'augment': "[cyan]Adding noise, reverb, and extracting features...[/cyan]",
            'train': "[cyan]Training neural network on GPU...[/cyan]",
            'complete': "[green]✅ Model ready![/green]",
            'unknown': "[dim]Initializing...[/dim]"
        }
        status_msg = status_messages.get(status['mode'], "[dim]Starting...[/dim]")
        table.add_row("Status", status_msg)

    return table

def create_activity_panel(status):
    """Create recent activity panel"""
    if not status['recent_activity']:
        return None

    activity_text = "\n".join(status['recent_activity'][:8])
    return Panel(
        activity_text,
        title="Recent Activity",
        border_style="dim",
        height=12
    )

def find_most_recent_log():
    """Find the most recently modified log file that has training content"""
    potential_logs = [
        'training.log',
        'hey_saga_training.log',
        'train_output.log',
        'dataset_download.log',
        'nohup.out',
    ]

    candidates = []
    for log_path in potential_logs:
        path = Path(log_path)
        if path.exists() and path.stat().st_size > 0:
            # Check if file has been modified in last hour (active training)
            mtime = path.stat().st_mtime
            age_seconds = time.time() - mtime
            if age_seconds < 3600:  # Modified in last hour
                candidates.append((path, mtime))

    if not candidates:
        return None

    # Return most recently modified
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]

def main():
    console.print("[cyan]🔍 Auto-detecting active training log...[/cyan]\n")

    # Define log files to monitor (check for existence)
    potential_log_files = {
        'dataset_download': 'dataset_download.log',
        'training': 'training.log',
        'hey_saga_training': 'hey_saga_training.log',
        'hey_saga_stdout': 'hey_saga_stdout.log',
        'train_output': 'train_output.log',
        'nohup': 'nohup.out'
    }

    console.print("[cyan]Starting training monitor... Press Ctrl+C to exit[/cyan]\n")

    try:
        with Live(console=console, refresh_per_second=2) as live:
            last_active_log = None
            no_activity_count = 0

            while True:
                # Auto-detect most recent active log
                active_log = find_most_recent_log()

                if active_log and active_log != last_active_log:
                    console.log(f"[green]📄 Monitoring: {active_log}[/green]")
                    last_active_log = active_log
                    no_activity_count = 0

                # Build log files dict from active log
                if active_log:
                    log_files = {'active': str(active_log)}
                else:
                    # Fallback: check all potential logs
                    log_files = {name: path for name, path in potential_log_files.items()
                                if Path(path).exists()}

                if not log_files:
                    if no_activity_count < 5:
                        live.update("[yellow]Waiting for training to start...[/yellow]")
                    else:
                        live.update(
                            "[yellow]No active training detected[/yellow]\n\n"
                            "Start training with:\n"
                            "[cyan]python3 train_wakeword_integrated.py --phrase 'hey saga' --model-name hey_saga[/cyan]"
                        )
                    no_activity_count += 1
                    time.sleep(1)
                    continue

                status = get_log_status(log_files)

                # Create display
                display = create_display(status)
                activity = create_activity_panel(status)

                # Stack displays vertically
                if activity:
                    layout = Group(display, activity)
                    live.update(layout)
                else:
                    live.update(display)

                time.sleep(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped[/yellow]")
        return 0

if __name__ == "__main__":
    sys.exit(main())
