#!/usr/bin/env python3
"""
Download/cache SF street sweeping data from DataSF.
Run this once before starting the app, then periodically to refresh.
Adapted from saga_assistant/sync_street_sweeping.py
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
import urllib.request

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

METADATA_URL = "https://data.sfgov.org/api/views/yhqp-riqs.json"
DATA_URL = "https://data.sfgov.org/resource/yhqp-riqs.json?$limit=50000"
DATA_DIR = Path(__file__).parent / "data"


def sync(force: bool = False) -> Dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sweeping_file = DATA_DIR / "street_sweeping_sf.json"
    metadata_file = DATA_DIR / "sync_metadata.json"

    # Load local metadata
    local_meta = None
    if metadata_file.exists():
        with open(metadata_file) as f:
            local_meta = json.load(f)

    # Fetch remote metadata
    logger.info("Checking remote metadata...")
    with urllib.request.urlopen(METADATA_URL, timeout=10) as resp:
        remote = json.loads(resp.read())
    remote_meta = {
        'rows_updated_at': remote['rowsUpdatedAt'],
        'row_count': remote.get('rowCount', 0)
    }

    needs_update = force or (local_meta is None) or (
        remote_meta['rows_updated_at'] > local_meta.get('rows_updated_at', 0)
    )

    if not needs_update:
        logger.info(f"Data is current ({local_meta.get('record_count', '?')} records)")
        return {'updated': False, 'record_count': local_meta.get('record_count', 0)}

    logger.info("Downloading street sweeping data (~15MB)...")
    with urllib.request.urlopen(DATA_URL, timeout=60) as resp:
        data = json.loads(resp.read())

    with open(sweeping_file, 'w') as f:
        json.dump(data, f, indent=2)

    record_count = len(data)
    with open(metadata_file, 'w') as f:
        json.dump({
            'last_sync': datetime.now(timezone.utc).isoformat(),
            'rows_updated_at': remote_meta['rows_updated_at'],
            'record_count': record_count
        }, f, indent=2)

    logger.info(f"Downloaded {record_count} records")
    return {'updated': True, 'record_count': record_count}


if __name__ == '__main__':
    force = '--force' in sys.argv
    result = sync(force=force)
    print(f"Done: {result}")
