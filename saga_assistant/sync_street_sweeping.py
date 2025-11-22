#!/usr/bin/env python3
"""
Sync SF Street Sweeping Data

Downloads the latest street sweeping schedule from SF DataSF API and caches it locally.
Only downloads if the remote data has been updated since last sync.

Can be run standalone or called as a Home Assistant service via run_assistant.py
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
import urllib.request

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
METADATA_URL = "https://data.sfgov.org/api/views/yhqp-riqs.json"
DATA_URL = "https://data.sfgov.org/resource/yhqp-riqs.json?$limit=50000"
DATA_DIR = Path(__file__).parent / "data"
SWEEPING_DATA_FILE = DATA_DIR / "street_sweeping_sf.json"
METADATA_FILE = DATA_DIR / "sync_metadata.json"


class StreetSweepingSyncer:
    """Manages syncing of SF street sweeping data"""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sweeping_file = self.data_dir / "street_sweeping_sf.json"
        self.metadata_file = self.data_dir / "sync_metadata.json"

    def load_local_metadata(self) -> Optional[Dict]:
        """Load local sync metadata"""
        if not self.metadata_file.exists():
            logger.info("No local metadata found - first sync")
            return None

        with open(self.metadata_file, 'r') as f:
            return json.load(f)

    def fetch_remote_metadata(self) -> Dict:
        """Fetch metadata from SF DataSF API"""
        logger.info(f"Fetching remote metadata from {METADATA_URL}")

        with urllib.request.urlopen(METADATA_URL, timeout=10) as response:
            data = json.loads(response.read())
            return {
                'rows_updated_at': data['rowsUpdatedAt'],
                'row_count': data.get('rowCount', 0)
            }

    def download_sweeping_data(self) -> int:
        """Download full street sweeping dataset"""
        logger.info(f"Downloading street sweeping data from {DATA_URL}")

        with urllib.request.urlopen(DATA_URL, timeout=60) as response:
            data = json.loads(response.read())

        # Write to file
        with open(self.sweeping_file, 'w') as f:
            json.dump(data, f, indent=2)

        record_count = len(data)
        logger.info(f"Downloaded {record_count} records to {self.sweeping_file}")
        return record_count

    def save_metadata(self, remote_metadata: Dict, record_count: int):
        """Save sync metadata"""
        metadata = {
            'last_sync': datetime.now(timezone.utc).isoformat(),
            'rows_updated_at': remote_metadata['rows_updated_at'],
            'record_count': record_count
        }

        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Saved sync metadata: {metadata}")

    def needs_update(self, local_metadata: Optional[Dict], remote_metadata: Dict) -> bool:
        """Check if local cache needs updating"""
        if local_metadata is None:
            logger.info("No local data - update needed")
            return True

        local_timestamp = local_metadata.get('rows_updated_at', 0)
        remote_timestamp = remote_metadata['rows_updated_at']

        if remote_timestamp > local_timestamp:
            local_dt = datetime.fromtimestamp(local_timestamp)
            remote_dt = datetime.fromtimestamp(remote_timestamp)
            logger.info(f"Remote data is newer - Local: {local_dt}, Remote: {remote_dt}")
            return True

        logger.info("Local data is up to date")
        return False

    def sync(self, force: bool = False) -> Dict:
        """
        Sync street sweeping data

        Args:
            force: Force download even if data hasn't changed

        Returns:
            Dict with sync results
        """
        logger.info("=" * 60)
        logger.info("Starting street sweeping data sync")
        logger.info("=" * 60)

        # Load local metadata
        local_metadata = self.load_local_metadata()

        # Fetch remote metadata
        remote_metadata = self.fetch_remote_metadata()

        # Check if update needed
        if force or self.needs_update(local_metadata, remote_metadata):
            logger.info("Downloading updated street sweeping data...")
            record_count = self.download_sweeping_data()
            self.save_metadata(remote_metadata, record_count)

            logger.info(f"✓ Sync completed successfully - {record_count} records")
            logger.info("=" * 60)
            return {
                'success': True,
                'updated': True,
                'message': f'Downloaded {record_count} records',
                'record_count': record_count
            }
        else:
            logger.info("✓ No update needed - data is current")
            logger.info("=" * 60)
            return {
                'success': True,
                'updated': False,
                'message': 'Data is already up to date',
                'record_count': local_metadata.get('record_count', 0)
            }


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Sync SF street sweeping data')
    parser.add_argument('--force', action='store_true',
                       help='Force download even if data is current')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    syncer = StreetSweepingSyncer()
    result = syncer.sync(force=args.force)

    if not result['success']:
        sys.exit(1)

    return result


if __name__ == '__main__':
    main()
