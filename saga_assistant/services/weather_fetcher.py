#!/usr/bin/env python3
"""
Weather Fetcher Daemon

Background service that fetches weather every 20 minutes and caches it.
Provides fast, reliable weather data to Saga assistant.

Usage:
    # One-time fetch
    python weather_fetcher.py

    # Daemon mode (runs every 20 minutes)
    python weather_fetcher.py --daemon

    # Custom zip code
    python weather_fetcher.py --zip 90210

    # Custom interval
    python weather_fetcher.py --daemon --interval 10
"""

import argparse
import logging
import sys
import time
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from saga_assistant.services.weather_cache import WeatherCache
from saga_assistant.services.weather_apis import WeatherFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

DEFAULT_ZIP = "94118"
DEFAULT_INTERVAL_MINUTES = 20


def fetch_and_cache(zip_code: str) -> bool:
    """
    Fetch weather and update cache.

    Args:
        zip_code: ZIP code to fetch

    Returns:
        True if successful
    """
    logger.info(f"🌤️  Fetching weather for {zip_code}...")

    # Fetch with fallback chain
    fetcher = WeatherFetcher()
    data = fetcher.fetch(zip_code)

    if not data:
        logger.error("❌ Failed to fetch weather from all APIs")
        return False

    # Update cache
    cache = WeatherCache()
    success = cache.set(zip_code, data)

    if success:
        logger.info(f"✅ Weather cache updated successfully")
        logger.info(f"   Current: {data['current_temp_f']}°F, {data['current_condition']}")
        logger.info(f"   Today: High {data['today_high_f']}°F, Low {data['today_low_f']}°F")
        if data['tomorrow_high_f']:
            logger.info(f"   Tomorrow: High {data['tomorrow_high_f']}°F, Low {data['tomorrow_low_f']}°F")
    else:
        logger.error("❌ Failed to update cache")

    return success


def run_daemon(zip_code: str, interval_minutes: int):
    """
    Run weather fetcher as daemon.

    Args:
        zip_code: ZIP code to fetch
        interval_minutes: Minutes between fetches
    """
    logger.info("="*60)
    logger.info("🌤️  Weather Fetcher Daemon Starting")
    logger.info(f"   ZIP Code: {zip_code}")
    logger.info(f"   Interval: {interval_minutes} minutes")
    logger.info(f"   Press Ctrl+C to stop")
    logger.info("="*60)
    logger.info("")

    try:
        while True:
            # Fetch and cache
            fetch_and_cache(zip_code)

            # Sleep until next fetch
            logger.info(f"😴 Sleeping for {interval_minutes} minutes...")
            logger.info("")
            time.sleep(interval_minutes * 60)

    except KeyboardInterrupt:
        logger.info("")
        logger.info("⏹️  Weather Fetcher Daemon stopped")


def main():
    parser = argparse.ArgumentParser(
        description="Weather Fetcher - Fetch and cache weather data"
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run as daemon (fetch every N minutes)'
    )
    parser.add_argument(
        '--zip',
        default=DEFAULT_ZIP,
        help=f'ZIP code (default: {DEFAULT_ZIP})'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=DEFAULT_INTERVAL_MINUTES,
        help=f'Fetch interval in minutes (default: {DEFAULT_INTERVAL_MINUTES})'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.daemon:
        run_daemon(args.zip, args.interval)
    else:
        # One-time fetch
        success = fetch_and_cache(args.zip)
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
