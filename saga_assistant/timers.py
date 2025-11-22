"""Timer management for voice assistant."""

import time
import threading
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class Timer:
    """Represents an active timer."""
    name: str
    duration_seconds: int
    start_time: float
    end_time: float
    callback: Optional[callable] = None
    message: Optional[str] = None  # For reminders


class TimerManager:
    """Manage multiple named timers."""

    def __init__(self):
        """Initialize timer manager."""
        self.timers: Dict[str, Timer] = {}
        self._lock = threading.Lock()

    def set_timer(self, duration_minutes: int = None, duration_seconds: int = None,
                  name: str = "timer", callback: callable = None, message: str = None) -> str:
        """Set a timer.

        Args:
            duration_minutes: Duration in minutes
            duration_seconds: Duration in seconds (if minutes not specified)
            name: Timer name/label
            callback: Optional function to call when timer expires

        Returns:
            Confirmation message
        """
        # Calculate total seconds
        if duration_minutes is not None:
            total_seconds = duration_minutes * 60
            duration_str = f"{duration_minutes} minute{'s' if duration_minutes != 1 else ''}"
        elif duration_seconds is not None:
            total_seconds = duration_seconds
            duration_str = f"{duration_seconds} second{'s' if duration_seconds != 1 else ''}"
        else:
            return "Please specify a duration"

        with self._lock:
            # Cancel existing timer with same name
            if name in self.timers:
                self.cancel_timer(name)

            # Create timer
            start_time = time.time()
            end_time = start_time + total_seconds

            timer = Timer(
                name=name,
                duration_seconds=total_seconds,
                start_time=start_time,
                end_time=end_time,
                callback=callback,
                message=message
            )

            self.timers[name] = timer

            # Start background thread to handle expiration
            threading.Thread(
                target=self._timer_thread,
                args=(name, total_seconds),
                daemon=True
            ).start()

            logger.info(f"Timer '{name}' set for {duration_str}" + (f" - {message}" if message else ""))

            # Different responses for timers vs reminders
            if message:
                # This is a reminder
                if duration_minutes and duration_minutes == 1:
                    return "I'll remind you in one minute"
                else:
                    return f"I'll remind you in {duration_str}"
            else:
                # This is a timer
                if duration_minutes and duration_minutes == 1:
                    return "Timer set for one minute"
                else:
                    return f"Timer set for {duration_str}"

    def _timer_thread(self, name: str, duration: int):
        """Background thread to handle timer expiration.

        Args:
            name: Timer name
            duration: Duration in seconds
        """
        time.sleep(duration)

        with self._lock:
            if name in self.timers:
                timer = self.timers[name]

                # Call callback if provided
                if timer.callback:
                    try:
                        # Pass the message to the callback if it exists
                        if timer.message:
                            timer.callback(name, timer.message)
                        else:
                            timer.callback(name)
                    except Exception as e:
                        logger.error(f"Timer callback error: {e}")

                # Remove expired timer
                del self.timers[name]
                logger.info(f"Timer '{name}' expired")

    def check_timer(self, name: str = "timer") -> str:
        """Check remaining time on a timer.

        Args:
            name: Timer name

        Returns:
            Status message
        """
        with self._lock:
            if name not in self.timers:
                if len(self.timers) == 0:
                    return "No active timers"
                elif len(self.timers) == 1:
                    # If asking about "timer" but there's a different one
                    actual_name = list(self.timers.keys())[0]
                    return self.check_timer(actual_name)
                else:
                    return f"No timer named '{name}'. Active: {', '.join(self.timers.keys())}"

            timer = self.timers[name]
            remaining = timer.end_time - time.time()

            if remaining <= 0:
                return "Timer should be done"

            # Format remaining time
            if remaining < 60:
                return f"{int(remaining)} seconds left"
            elif remaining < 3600:
                minutes = int(remaining / 60)
                seconds = int(remaining % 60)
                if seconds == 0:
                    return f"{minutes} minute{'s' if minutes != 1 else ''} left"
                else:
                    return f"{minutes} minute{'s' if minutes != 1 else ''} and {seconds} seconds left"
            else:
                hours = int(remaining / 3600)
                minutes = int((remaining % 3600) / 60)
                return f"{hours} hour{'s' if hours != 1 else ''} and {minutes} minute{'s' if minutes != 1 else ''} left"

    def cancel_timer(self, name: str = "timer") -> str:
        """Cancel a timer.

        Args:
            name: Timer name

        Returns:
            Confirmation message
        """
        with self._lock:
            if name not in self.timers:
                if len(self.timers) == 0:
                    return "No active timers"
                elif len(self.timers) == 1:
                    # If asking to cancel "timer" but there's a different one
                    actual_name = list(self.timers.keys())[0]
                    del self.timers[actual_name]
                    return "Timer cancelled"
                else:
                    return f"No timer named '{name}'"

            del self.timers[name]
            logger.info(f"Timer '{name}' cancelled")
            return "Timer cancelled"

    def list_timers(self) -> str:
        """List all active timers.

        Returns:
            List of active timers
        """
        with self._lock:
            if len(self.timers) == 0:
                return "No active timers"

            timer_list = []
            for name, timer in self.timers.items():
                remaining = timer.end_time - time.time()
                minutes = int(remaining / 60)
                seconds = int(remaining % 60)

                if name == "timer":
                    timer_list.append(f"{minutes}:{seconds:02d} remaining")
                else:
                    timer_list.append(f"{name}: {minutes}:{seconds:02d}")

            if len(timer_list) == 1:
                return timer_list[0]
            else:
                return ", ".join(timer_list)
