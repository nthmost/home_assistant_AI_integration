#!/usr/bin/env python3
"""
Weather Fetcher V2 - Multi-Location, 5-Day Forecasts

Fetches weather for multiple locations (bike ride planning).
Updates cache every 20 minutes with 5-day forecasts.
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from saga_assistant.services.weather_cache_v2 import WeatherCacheV2
from saga_assistant.services.weather_apis_v2 import WeatherFetcherV2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

DEFAULT_LOCATIONS_FILE = Path(__file__).parent / "bike_locations.json"


def load_locations(filepath: Path) -> list:
    """Load locations from JSON file."""
    try:
        with open(filepath) as f:
            data = json.load(f)
            return data['locations']
    except Exception as e:
        logger.error(f"Failed to load locations from {filepath}: {e}")
        return []


def fetch_and_cache_all(locations: list) -> int:
    """
    Fetch weather for all locations and update cache.

    Args:
        locations: List of location dicts with 'name' and 'zip' keys

    Returns:
        Number of successful updates
    """
    cache = WeatherCacheV2()
    fetcher = WeatherFetcherV2()
    success_count = 0

    for loc in locations:
        name = loc['name']
        zip_code = loc['zip']

        logger.info(f"🌤️  Fetching weather for {name} ({zip_code})...")

        data = fetcher.fetch(zip_code)

        if data:
            success = cache.set(name, data['current'], data['forecasts'])
            if success:
                success_count += 1
                logger.info(f"   ✅ {name}: {data['current']['temp_f']}°F, {len(data['forecasts'])} days cached")
            else:
                logger.error(f"   ❌ {name}: Cache update failed")
        else:
            logger.error(f"   ❌ {name}: API fetch failed")

        # Small delay between requests (API rate limiting)
        time.sleep(0.5)

    return success_count


def run_daemon(locations: list, interval_minutes: int):
    """
    Run weather fetcher as daemon.

    Args:
        locations: List of location dicts
        interval_minutes: Minutes between fetches
    """
    logger.info("="*60)
    logger.info("🌤️  Multi-Location Weather Fetcher Daemon")
    logger.info(f"   Locations: {', '.join(loc['name'] for loc in locations)}")
    logger.info(f"   Interval: {interval_minutes} minutes")
    logger.info(f"   Press Ctrl+C to stop")
    logger.info("="*60)
    logger.info("")

    try:
        while True:
            # Fetch all locations
            success = fetch_and_cache_all(locations)
            total = len(locations)

            if success == total:
                logger.info(f"✅ Updated all {total} locations successfully")
            else:
                logger.warning(f"⚠️  Updated {success}/{total} locations")

            # Sleep until next fetch
            logger.info(f"😴 Sleeping for {interval_minutes} minutes...")
            logger.info("")
            time.sleep(interval_minutes * 60)

    except KeyboardInterrupt:
        logger.info("")
        logger.info("⏹️  Weather Fetcher Daemon stopped")


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Location Weather Fetcher - 5-Day Forecasts"
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run as daemon (fetch every N minutes)'
    )
    parser.add_argument(
        '--locations',
        default=DEFAULT_LOCATIONS_FILE,
        help=f'Locations JSON file (default: {DEFAULT_LOCATIONS_FILE})'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=20,
        help='Fetch interval in minutes (default: 20)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load locations
    locations = load_locations(Path(args.locations))
    if not locations:
        logger.error("No locations to fetch!")
        return 1

    if args.daemon:
        run_daemon(locations, args.interval)
    else:
        # One-time fetch
        success = fetch_and_cache_all(locations)
        total = len(locations)

        if success == total:
            logger.info(f"✅ All {total} locations updated successfully")
            return 0
        else:
            logger.warning(f"⚠️  Only {success}/{total} locations updated")
            return 1


if __name__ == "__main__":
    sys.exit(main())
