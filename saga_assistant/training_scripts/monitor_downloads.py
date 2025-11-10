#!/usr/bin/env python3
"""
Monitor dataset download progress with a nice visual interface
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
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn

console = Console()

def parse_wget_line(line):
    """Parse wget progress line to extract info"""
    # Example: "7970700K .......... .......... .......... .......... .......... 47% 9.06M 13m11s"
    # Try with multiple dots sections
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

def format_size(kb):
    """Format KB to human readable"""
    if kb < 1024:
        return f"{kb}K"
    elif kb < 1024 * 1024:
        return f"{kb/1024:.1f}M"
    else:
        return f"{kb/(1024*1024):.2f}G"

def get_download_status(log_file):
    """Get current download status from log file"""
    if not Path(log_file).exists():
        return None

    # Read last 100 lines
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()[-100:]
    except:
        return None

    status = {
        'current_file': 'Unknown',
        'phase': 'Unknown',
        'progress': None,
        'recent_activity': []
    }

    # Parse backwards to find current state
    for line in reversed(lines):
        line = line.strip()

        # Check for FILE: markers
        if '📦 FILE:' in line:
            # Extract filename from "📦 FILE: filename (size)"
            parts = line.split('FILE:')
            if len(parts) > 1:
                filename_part = parts[1].strip()
                # Remove size info in parentheses
                if '(' in filename_part:
                    filename_part = filename_part.split('(')[0].strip()
                status['current_file'] = filename_part

        # Fallback: Check for file being downloaded in older format
        elif 'Downloading' in line and not status['current_file']:
            parts = line.split()
            for i, part in enumerate(parts):
                if part.endswith('.tar') or part.endswith('.npy') or part.endswith('.flac'):
                    status['current_file'] = part
                    break

        # Check for phase
        if 'Downloading MIT Room' in line:
            status['phase'] = 'MIT Room Impulse Responses'
        elif 'Downloading AudioSet' in line:
            status['phase'] = 'AudioSet (Background Audio)'
        elif 'Downloading Free Music' in line:
            status['phase'] = 'Free Music Archive'
        elif 'Downloading pre-computed' in line:
            status['phase'] = 'Pre-computed Features'
        elif 'Converting to 16kHz' in line:
            status['phase'] = 'Converting AudioSet to 16kHz'
        elif 'Extracting' in line:
            status['phase'] = 'Extracting Archive'

        # Parse wget progress
        progress = parse_wget_line(line)
        if progress and not status['progress']:
            status['progress'] = progress

        # Collect recent activity
        if len(status['recent_activity']) < 5:
            if any(keyword in line for keyword in ['✅', '❌', 'Downloading', 'Converting', 'Saved']):
                status['recent_activity'].insert(0, line)

    return status

def create_display(status):
    """Create rich display table"""

    # Main status table
    table = Table(title="📥 Dataset Download Monitor", show_header=False, border_style="cyan")
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value", style="white")

    table.add_row("Current Phase", f"[yellow]{status['phase']}[/yellow]")
    table.add_row("Current File", f"[cyan]{status['current_file']}[/cyan]")

    if status['progress']:
        p = status['progress']
        downloaded_str = format_size(p['downloaded'])
        progress_bar = "█" * (p['percent'] // 2) + "░" * (50 - p['percent'] // 2)
        table.add_row("Progress", f"[green]{progress_bar}[/green] {p['percent']}%")
        table.add_row("Downloaded", f"[green]{downloaded_str}[/green]")
        table.add_row("Speed", f"[cyan]{p['speed']}/s[/cyan]")
        table.add_row("ETA", f"[yellow]{p['eta']}[/yellow]")
    else:
        table.add_row("Progress", "[dim]Waiting...[/dim]")

    return table

def create_activity_panel(status):
    """Create recent activity panel"""
    if not status['recent_activity']:
        return None

    activity_text = "\n".join(status['recent_activity'][:5])
    return Panel(
        activity_text,
        title="Recent Activity",
        border_style="dim",
        height=8
    )

def main():
    log_file = Path("dataset_download.log")

    if not log_file.exists():
        console.print("[red]Error: dataset_download.log not found[/red]")
        console.print("Make sure you're in ~/saga_training/ directory")
        return 1

    console.print("[cyan]Starting download monitor... Press Ctrl+C to exit[/cyan]\n")

    try:
        with Live(console=console, refresh_per_second=2) as live:
            while True:
                status = get_download_status(log_file)

                if status:
                    # Create display
                    display = create_display(status)
                    activity = create_activity_panel(status)

                    # Combine displays
                    if activity:
                        from rich.columns import Columns
                        layout = Columns([display, activity])
                        live.update(layout)
                    else:
                        live.update(display)
                else:
                    live.update("[yellow]Waiting for download to start...[/yellow]")

                time.sleep(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped[/yellow]")
        return 0

if __name__ == "__main__":
    sys.exit(main())
