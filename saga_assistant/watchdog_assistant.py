#!/usr/bin/env python3
"""
Watchdog wrapper for Saga Assistant

Monitors the assistant process and restarts it if it becomes unresponsive.
Also handles cleanup of leaked resources.
"""

import subprocess
import time
import signal
import sys
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

ASSISTANT_SCRIPT = Path(__file__).parent / "run_assistant.py"
HEARTBEAT_FILE = Path.home() / ".saga_assistant" / "heartbeat"
HEARTBEAT_TIMEOUT = 30  # Seconds without heartbeat = hung
RESTART_DELAY = 2  # Seconds to wait before restart
MAX_RESTART_ATTEMPTS = 3  # Max restarts in RESTART_WINDOW
RESTART_WINDOW = 60  # Seconds


class AssistantWatchdog:
    """Monitors and manages the Saga Assistant process."""

    def __init__(self):
        self.process = None
        self.restart_times = []
        self.running = True

        # Ensure heartbeat directory exists
        HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self._stop_assistant()
        sys.exit(0)

    def _start_assistant(self):
        """Start the assistant process."""
        logger.info("🚀 Starting Saga Assistant...")

        # Clear old heartbeat
        if HEARTBEAT_FILE.exists():
            HEARTBEAT_FILE.unlink()

        self.process = subprocess.Popen(
            ["python", str(ASSISTANT_SCRIPT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffered
        )

        logger.info(f"✅ Assistant started (PID: {self.process.pid})")

    def _stop_assistant(self, force=False):
        """Stop the assistant process."""
        if not self.process:
            return

        logger.info("🛑 Stopping assistant...")

        if not force:
            # Try graceful shutdown first
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                logger.info("✅ Assistant stopped gracefully")
                return
            except subprocess.TimeoutExpired:
                logger.warning("⏱️  Graceful shutdown timed out, forcing...")

        # Force kill
        self.process.kill()
        try:
            self.process.wait(timeout=2)
            logger.info("✅ Assistant force killed")
        except subprocess.TimeoutExpired:
            logger.error("❌ Failed to kill assistant!")

    def _check_heartbeat(self) -> bool:
        """Check if assistant is responding."""
        if not HEARTBEAT_FILE.exists():
            return True  # No heartbeat file yet, that's OK at startup

        try:
            mtime = HEARTBEAT_FILE.stat().st_mtime
            age = time.time() - mtime
            return age < HEARTBEAT_TIMEOUT
        except Exception as e:
            logger.warning(f"Error checking heartbeat: {e}")
            return True  # Assume OK if we can't check

    def _should_restart(self) -> bool:
        """Check if we should restart (not too many recent restarts)."""
        now = time.time()

        # Remove old restart times outside window
        self.restart_times = [t for t in self.restart_times if now - t < RESTART_WINDOW]

        if len(self.restart_times) >= MAX_RESTART_ATTEMPTS:
            logger.error(
                f"❌ Too many restarts ({len(self.restart_times)}) in "
                f"{RESTART_WINDOW}s window. Giving up."
            )
            return False

        return True

    def _restart_assistant(self):
        """Restart the assistant process."""
        if not self._should_restart():
            self.running = False
            return

        logger.warning("🔄 Restarting assistant...")
        self.restart_times.append(time.time())

        self._stop_assistant(force=True)
        time.sleep(RESTART_DELAY)
        self._start_assistant()

    def run(self):
        """Main watchdog loop."""
        logger.info("👁️  Saga Assistant Watchdog starting...")
        logger.info(f"   Heartbeat timeout: {HEARTBEAT_TIMEOUT}s")
        logger.info(f"   Max restarts: {MAX_RESTART_ATTEMPTS} per {RESTART_WINDOW}s")

        self._start_assistant()

        last_heartbeat_check = time.time()

        try:
            while self.running:
                # Check if process died
                if self.process and self.process.poll() is not None:
                    returncode = self.process.returncode
                    logger.warning(f"⚠️  Assistant process died (exit code: {returncode})")
                    self._restart_assistant()
                    last_heartbeat_check = time.time()
                    continue

                # Check heartbeat periodically
                if time.time() - last_heartbeat_check > 5:
                    if not self._check_heartbeat():
                        logger.warning("💔 Heartbeat timeout - assistant appears hung")
                        self._restart_assistant()
                    last_heartbeat_check = time.time()

                # Read and forward output
                if self.process and self.process.stdout:
                    try:
                        line = self.process.stdout.readline()
                        if line:
                            print(line, end='', flush=True)
                    except Exception as e:
                        logger.debug(f"Error reading output: {e}")

                time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Interrupted by user")

        finally:
            self._stop_assistant()
            logger.info("👋 Watchdog stopped")


def main():
    """Run the watchdog."""
    watchdog = AssistantWatchdog()
    watchdog.run()


if __name__ == '__main__':
    main()
