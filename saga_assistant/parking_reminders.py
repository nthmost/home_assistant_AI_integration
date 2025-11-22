#!/usr/bin/env python3
"""
Parking Reminders for Saga Assistant

Checks for upcoming street sweeping and sends notifications via Home Assistant.
Can run as a background service or periodic check.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict

from parking import StreetSweepingLookup, ParkingManager

logger = logging.getLogger(__name__)

# Notification thresholds
NIGHT_BEFORE_HOUR = 19  # 7pm
MORNING_OF_HOURS_BEFORE = 2  # 2 hours before sweeping


class ParkingReminderService:
    """Service to check for upcoming street sweeping and send reminders"""

    def __init__(self, ha_client=None):
        self.lookup = StreetSweepingLookup()
        self.manager = ParkingManager(self.lookup)
        self.ha_client = ha_client
        self.last_notification_file = Path.home() / ".saga_assistant" / "last_parking_notification.json"
        self.last_notification_file.parent.mkdir(parents=True, exist_ok=True)

    def load_last_notification(self) -> Optional[Dict]:
        """Load info about last notification sent"""
        if not self.last_notification_file.exists():
            return None
        with open(self.last_notification_file, 'r') as f:
            return json.load(f)

    def save_last_notification(self, notification_type: str, sweep_date: datetime):
        """Save info about notification sent"""
        data = {
            'type': notification_type,
            'sweep_date': sweep_date.isoformat(),
            'sent_at': datetime.now().isoformat()
        }
        with open(self.last_notification_file, 'w') as f:
            json.dump(data, f, indent=2)

    def should_send_notification(self, notification_type: str, sweep_date: datetime) -> bool:
        """Check if we should send this notification (avoid duplicates)"""
        last = self.load_last_notification()
        if not last:
            return True

        # Different sweep date? Always send
        if last.get('sweep_date') != sweep_date.isoformat():
            return True

        # Same sweep, same notification type? Don't spam
        if last.get('type') == notification_type:
            return False

        return True

    def check_and_notify(self) -> Optional[str]:
        """
        Check for upcoming street sweeping and send notifications if needed

        Returns:
            Message sent, or None if no notification needed
        """
        # Get next sweeping event
        next_sweep = self.manager.get_next_sweeping(days_ahead=7)
        if not next_sweep:
            logger.info("No upcoming street sweeping in next 7 days")
            return None

        schedule = next_sweep['schedule']
        start_time = next_sweep['start_time']
        now = datetime.now()
        delta = start_time - now

        # Determine notification type
        notification_type = None
        message = None

        # Night before (if sweeping is tomorrow and it's evening)
        if delta.days == 0 and now.hour >= NIGHT_BEFORE_HOUR:
            notification_type = "night_before"
            from_time = f"{schedule.fromhour % 12 or 12}{'am' if schedule.fromhour < 12 else 'pm'}"
            to_time = f"{schedule.tohour % 12 or 12}{'am' if schedule.tohour < 12 else 'pm'}"
            message = (
                f"Reminder: Street sweeping TOMORROW morning "
                f"{from_time}-{to_time}. Don't forget to move your car!"
            )

        # Morning of (within 2 hours of sweeping)
        elif delta.total_seconds() / 3600 <= MORNING_OF_HOURS_BEFORE and delta.total_seconds() > 0:
            notification_type = "morning_of"
            from_time = f"{schedule.fromhour % 12 or 12}{'am' if schedule.fromhour < 12 else 'pm'}"
            hours_left = delta.total_seconds() / 3600
            message = (
                f"URGENT: Street sweeping in {hours_left:.1f} hours at {from_time}! "
                f"Move your car now!"
            )

        # Send notification if needed
        if notification_type and message:
            if self.should_send_notification(notification_type, start_time):
                logger.info(f"Sending {notification_type} notification: {message}")
                self._send_notification(message)
                self.save_last_notification(notification_type, start_time)
                return message
            else:
                logger.debug(f"Skipping duplicate {notification_type} notification")

        return None

    def _send_notification(self, message: str):
        """Send notification via Home Assistant"""
        if self.ha_client:
            # Use HA notify service
            self.ha_client.call_service(
                'notify',
                'notify',  # or specific notifier like 'mobile_app_iphone'
                {
                    'title': 'Street Sweeping Reminder',
                    'message': message
                }
            )
        else:
            # Just log if no HA client
            logger.info(f"Notification: {message}")

    def get_status_message(self) -> str:
        """Get human-readable status for current parking"""
        return self.manager.get_human_readable_status()


def main():
    """CLI for testing reminders"""
    import argparse

    parser = argparse.ArgumentParser(description='Check parking reminders')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    service = ParkingReminderService()

    print("\n" + "="*70)
    print("Parking Reminder Check")
    print("="*70)

    # Show current status
    print("\nCurrent parking status:")
    print(service.get_status_message())

    print("\n" + "-"*70)
    print("Checking for notifications...")
    print("-"*70)

    # Check for notifications
    message = service.check_and_notify()
    if message:
        print(f"\n✉️  Notification sent:")
        print(f"   {message}")
    else:
        print("\n✓ No notifications needed at this time")

    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
