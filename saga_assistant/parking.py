#!/usr/bin/env python3
"""
Parking and Street Sweeping Management for Saga Assistant

Handles:
- Natural language parking location parsing
- Street sweeping schedule lookups
- Parking state management
- Reminder notifications
"""

import json
import logging
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from difflib import get_close_matches

logger = logging.getLogger(__name__)


def ordinal(n: int) -> str:
    """Convert number to ordinal string.

    Examples: 1 -> '1st', 2 -> '2nd', 3 -> '3rd', 11 -> '11th', 21 -> '21st'
    """
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


def expand_street_abbreviations(text: str) -> str:
    """Expand street abbreviations for TTS pronunciation.

    St → Street, Ave → Avenue, etc.
    Also expands directions and ordinals.
    """
    # Street types
    text = (text
        .replace(" St", " Street")
        .replace(" Ave", " Avenue")
        .replace(" Blvd", " Boulevard")
        .replace(" Dr", " Drive")
        .replace(" Ln", " Lane")
        .replace(" Rd", " Road")
        .replace(" Ct", " Court")
        .replace(" Pl", " Place")
        .replace(" Ter", " Terrace")
        .replace(" Pkwy", " Parkway")
        .replace(" Cir", " Circle")
        .replace(" Hwy", " Highway")
        .replace(" Fwy", " Freeway"))

    # Ordinal number abbreviations in street names (1st, 2nd, 3rd, etc.)
    # Handle both standalone and in compound (e.g., "01st" -> "1st")
    text = (text
        .replace("01st", "1st")
        .replace("02nd", "2nd")
        .replace("03rd", "3rd")
        .replace("04th", "4th")
        .replace("05th", "5th")
        .replace("06th", "6th")
        .replace("07th", "7th")
        .replace("08th", "8th")
        .replace("09th", "9th"))

    return text


# Constants
DATA_DIR = Path(__file__).parent / "data"
SWEEPING_DATA_FILE = DATA_DIR / "street_sweeping_sf.json"
PARKING_STATE_FILE = Path.home() / ".saga_assistant" / "parking_state.json"

# Week number calculation (1st, 2nd, 3rd, 4th, 5th week of month)
WEEK_FIELDS = ['week1', 'week2', 'week3', 'week4', 'week5']

# Day of week mapping
WEEKDAY_MAP = {
    'Monday': 'Mon', 'Mon': 'Mon',
    'Tuesday': 'Tue', 'Tue': 'Tue',
    'Wednesday': 'Wed', 'Wed': 'Wed',
    'Thursday': 'Thu', 'Thu': 'Thu',
    'Friday': 'Fri', 'Fri': 'Fri',
    'Saturday': 'Sat', 'Sat': 'Sat',
    'Sunday': 'Sun', 'Sun': 'Sun',
}


@dataclass
class ParkingLocation:
    """Represents where the car is parked"""
    street: str
    cross_street_1: Optional[str]
    cross_street_2: Optional[str]
    side: str  # North, South, East, West
    block_limits: Optional[str]  # e.g., "07th Ave  -  08th Ave"
    timestamp: str
    raw_input: str


@dataclass
class SweepingSchedule:
    """Represents a street sweeping schedule"""
    corridor: str
    limits: str
    blockside: str
    weekday: str
    fullname: str
    fromhour: int
    tohour: int
    week1: bool
    week2: bool
    week3: bool
    week4: bool
    week5: bool
    holidays: bool

    def applies_to_date(self, date: datetime) -> bool:
        """Check if this schedule applies to a given date"""
        # Check day of week
        day_name = date.strftime('%a')  # Mon, Tue, Wed, etc.
        if day_name != self.weekday:
            return False

        # Check week of month (1-5)
        week_of_month = (date.day - 1) // 7 + 1
        week_applies = [self.week1, self.week2, self.week3, self.week4, self.week5]

        if week_of_month > 5:
            week_of_month = 5

        return week_applies[week_of_month - 1]

    def get_datetime_range(self, date: datetime) -> Tuple[datetime, datetime]:
        """Get the datetime range for this sweeping on a given date"""
        start = date.replace(hour=self.fromhour, minute=0, second=0, microsecond=0)
        end = date.replace(hour=self.tohour, minute=0, second=0, microsecond=0)
        return start, end

    def to_human_readable(self) -> str:
        """Convert to human-readable description"""
        from_time = f"{self.fromhour % 12 or 12}{'am' if self.fromhour < 12 else 'pm'}"
        to_time = f"{self.tohour % 12 or 12}{'am' if self.tohour < 12 else 'pm'}"
        return f"{self.fullname} {from_time}-{to_time} ({self.blockside} side)"


class StreetSweepingLookup:
    """Lookup street sweeping schedules from local cache"""

    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or SWEEPING_DATA_FILE
        self.data: List[Dict] = []
        self.street_index: Dict[str, List[Dict]] = {}
        self._load_data()

    def _load_data(self):
        """Load and index street sweeping data"""
        if not self.data_file.exists():
            raise FileNotFoundError(
                f"Street sweeping data not found at {self.data_file}. "
                f"Run sync_street_sweeping.py first."
            )

        logger.info(f"Loading street sweeping data from {self.data_file}")
        with open(self.data_file, 'r') as f:
            self.data = json.load(f)

        # Build index by street name for faster lookups
        for record in self.data:
            street = record['corridor']
            if street not in self.street_index:
                self.street_index[street] = []
            self.street_index[street].append(record)

        logger.info(f"Loaded {len(self.data)} records covering {len(self.street_index)} streets")

    def get_street_names(self) -> List[str]:
        """Get all unique street names"""
        return sorted(self.street_index.keys())

    def find_street(self, street_query: str) -> Optional[str]:
        """Find street name with fuzzy matching"""
        # Normalize query
        street_query = street_query.strip().title()

        # Exact match
        if street_query in self.street_index:
            return street_query

        # Try with common suffixes
        for suffix in [' St', ' Ave', ' Blvd', ' Dr', ' Way', ' Ln']:
            candidate = street_query + suffix
            if candidate in self.street_index:
                logger.info(f"Matched '{street_query}' to '{candidate}' with suffix")
                return candidate

        # Fuzzy match with lower cutoff for partial names
        matches = get_close_matches(street_query, self.street_index.keys(), n=1, cutoff=0.6)
        if matches:
            logger.info(f"Fuzzy matched '{street_query}' to '{matches[0]}'")
            return matches[0]

        return None

    def get_valid_sides(
        self,
        street: str,
        block_limits: Optional[str] = None
    ) -> List[str]:
        """
        Get list of valid sides (North/South/East/West) for a street/block.

        Args:
            street: Street name (e.g., "Balboa St")
            block_limits: Block boundaries (e.g., "07th Ave  -  08th Ave")

        Returns:
            List of valid sides (e.g., ["North", "South"])
        """
        # Find street
        street_name = self.find_street(street)
        if not street_name:
            return []

        # Get all records for this street
        records = self.street_index.get(street_name, [])

        # Filter by block limits if provided
        if block_limits:
            records = [r for r in records if r['limits'] == block_limits]

        # Extract unique sides
        sides = set()
        for record in records:
            side = record.get('blockside', '').strip()
            if side:  # Only add non-empty sides
                sides.add(side)

        return sorted(list(sides))

    def lookup_schedule(
        self,
        street: str,
        block_limits: Optional[str] = None,
        side: Optional[str] = None
    ) -> List[SweepingSchedule]:
        """
        Look up street sweeping schedule

        Args:
            street: Street name (e.g., "Anza St")
            block_limits: Block boundaries (e.g., "07th Ave  -  08th Ave")
            side: Side of street (North, South, East, West)

        Returns:
            List of matching sweeping schedules
        """
        # Find street
        street_name = self.find_street(street)
        if not street_name:
            logger.warning(f"Street not found: {street}")
            return []

        # Get all records for this street
        records = self.street_index.get(street_name, [])

        # Filter by block limits if provided
        if block_limits:
            records = [r for r in records if r['limits'] == block_limits]

        # Filter by side if provided (but not if Unknown)
        if side and side.lower() != 'unknown':
            records = [r for r in records if r.get('blockside', '').lower() == side.lower()]

        # Convert to SweepingSchedule objects
        schedules = []
        for r in records:
            schedules.append(SweepingSchedule(
                corridor=r['corridor'],
                limits=r['limits'],
                blockside=r['blockside'],
                weekday=r['weekday'],
                fullname=r['fullname'],
                fromhour=int(r['fromhour']),
                tohour=int(r['tohour']),
                week1=bool(int(r['week1'])),
                week2=bool(int(r['week2'])),
                week3=bool(int(r['week3'])),
                week4=bool(int(r['week4'])),
                week5=bool(int(r['week5'])),
                holidays=bool(int(r['holidays']))
            ))

        return schedules

    def get_all_blocks_for_street(self, street: str) -> List[str]:
        """Get all block limits for a given street"""
        street_name = self.find_street(street)
        if not street_name:
            return []

        records = self.street_index.get(street_name, [])
        blocks = sorted(set(r['limits'] for r in records))
        return blocks


class LocationParser:
    """Parse natural language parking locations"""

    # Common patterns for SF addresses
    PATTERNS = [
        # "north side of Anza between 7th and 8th ave"
        r'(?P<side>north|south|east|west)\s+side\s+of\s+(?P<street>[\w\s]+)\s+between\s+(?P<cross1>[\w\s]+)\s+and\s+(?P<cross2>[\w\s]+)',
        # "Anza between 7th and 8th on the north side"
        r'(?P<street>[\w\s]+)\s+between\s+(?P<cross1>[\w\s]+)\s+and\s+(?P<cross2>[\w\s]+)',
        # "on Anza near 7th avenue"
        r'on\s+(?P<street>[\w\s]+)\s+near\s+(?P<cross1>[\w\s]+)',
        # "1234 Anza Street"
        r'(?P<address>\d+)\s+(?P<street>[\w\s]+)',
        # "on Balboa Street" or "Balboa Street" (just street name - will need more info)
        r'(?:on\s+)?(?P<street>[\w\s]+?)\s+(?:street|st|avenue|ave|blvd|boulevard|drive|dr|road|rd)\b',
    ]

    def __init__(self, lookup: StreetSweepingLookup):
        self.lookup = lookup

    def normalize_avenue_number(self, text: str) -> str:
        """Normalize avenue numbers: '7th' -> '07th', '8th' -> '08th' and 'ave' -> 'Ave'"""
        # Match numbered avenues like "7th", "8th", "12th"
        def pad_number(match):
            num = match.group(1)
            suffix = match.group(2)
            return f"{int(num):02d}{suffix}"

        text = re.sub(r'\b(\d{1,2})(st|nd|rd|th)\b', pad_number, text, flags=re.IGNORECASE)

        # Normalize avenue/street suffixes
        text = re.sub(r'\b(ave|avenue)\b', 'Ave', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(st|street)\b', 'St', text, flags=re.IGNORECASE)

        return text

    def parse(self, location_text: str) -> Optional[ParkingLocation]:
        """
        Parse natural language location into structured format

        Examples:
            "north side of Anza between 7th and 8th ave"
            "Anza between 7th and 8th"
            "1234 Valencia Street"
        """
        location_text = location_text.lower().strip()
        logger.info(f"Parsing location: {location_text}")

        # Normalize avenue numbers
        location_text = self.normalize_avenue_number(location_text)

        for pattern in self.PATTERNS:
            match = re.search(pattern, location_text, re.IGNORECASE)
            if match:
                return self._process_match(match, location_text)

        logger.warning(f"Could not parse location: {location_text}")
        return None

    def _process_match(self, match, raw_input: str) -> Optional[ParkingLocation]:
        """Process regex match into ParkingLocation"""
        data = match.groupdict()

        street = data.get('street', '').strip()
        cross1 = data.get('cross1', '').strip() if 'cross1' in data else None
        cross2 = data.get('cross2', '').strip() if 'cross2' in data else None
        side = data.get('side', '').strip().title() if 'side' in data else None

        # Find matching street in database
        street_name = self.lookup.find_street(street)
        if not street_name:
            logger.warning(f"Street not found in database: {street}")
            return None

        # Try to match block limits
        block_limits = None
        if cross1 and cross2:
            # Normalize cross street formatting
            cross1_norm = self.normalize_avenue_number(cross1)
            cross2_norm = self.normalize_avenue_number(cross2)

            # Try to find matching block
            all_blocks = self.lookup.get_all_blocks_for_street(street_name)
            for block in all_blocks:
                # Block format: "07th Ave  -  08th Ave"
                if cross1_norm in block and cross2_norm in block:
                    block_limits = block
                    break

            if not block_limits:
                logger.warning(f"Could not find block {cross1_norm} - {cross2_norm} on {street_name}")
                # Use closest match
                logger.info(f"Available blocks: {all_blocks[:5]}...")

        return ParkingLocation(
            street=street_name,
            cross_street_1=cross1,
            cross_street_2=cross2,
            side=side or "Unknown",
            block_limits=block_limits,
            timestamp=datetime.now(timezone.utc).isoformat(),
            raw_input=raw_input
        )


class ParkingManager:
    """Manage parking state and notifications"""

    def __init__(self, lookup: StreetSweepingLookup, state_file: Optional[Path] = None):
        self.lookup = lookup
        self.state_file = state_file or PARKING_STATE_FILE
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.parser = LocationParser(lookup)

    def save_parking_location(self, location: ParkingLocation):
        """Save current parking location"""
        # Look up sweeping schedule
        schedules = self.lookup.lookup_schedule(
            location.street,
            location.block_limits,
            location.side
        )

        state = {
            'location': asdict(location),
            'schedules': [asdict(s) for s in schedules],
            'saved_at': datetime.now(timezone.utc).isoformat()
        }

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

        logger.info(f"Saved parking location: {location.street} {location.block_limits}")

    def load_parking_state(self) -> Optional[Dict]:
        """Load current parking state"""
        if not self.state_file.exists():
            return None

        with open(self.state_file, 'r') as f:
            return json.load(f)

    def get_next_sweeping(self, days_ahead: int = 14) -> Optional[Dict]:
        """Get next street sweeping event for parked location"""
        state = self.load_parking_state()
        if not state:
            return None

        schedules_data = state.get('schedules', [])
        if not schedules_data:
            return None

        # Convert back to SweepingSchedule objects
        schedules = [SweepingSchedule(**s) for s in schedules_data]

        # Find next sweeping event
        now = datetime.now()
        next_event = None

        for day_offset in range(days_ahead):
            check_date = now + timedelta(days=day_offset)

            for schedule in schedules:
                if schedule.applies_to_date(check_date):
                    start_time, end_time = schedule.get_datetime_range(check_date)

                    # Skip if already passed
                    if end_time < now:
                        continue

                    if next_event is None or start_time < next_event['start_time']:
                        next_event = {
                            'schedule': schedule,
                            'date': check_date,
                            'start_time': start_time,
                            'end_time': end_time
                        }

        return next_event

    def get_human_readable_status(self, expand_abbreviations: bool = False) -> str:
        """Get human-readable parking status

        Args:
            expand_abbreviations: If True, expand St/Ave for TTS pronunciation
        """
        state = self.load_parking_state()
        if not state:
            return "No parking location saved"

        location = state['location']
        next_sweep = self.get_next_sweeping()

        street = location['street']
        block_limits = location['block_limits']

        if expand_abbreviations:
            street = expand_street_abbreviations(street)
            if block_limits:
                block_limits = expand_street_abbreviations(block_limits)

        status = f"Parked on {street}"
        if block_limits:
            status += f" between {block_limits.replace('  -  ', ' and ')}"
        status += f" on the {location['side'].lower()} side"

        if next_sweep:
            schedule = next_sweep['schedule']
            start = next_sweep['start_time']
            delta = start - datetime.now()

            if delta.days == 0:
                when = "TODAY"
            elif delta.days == 1:
                when = "TOMORROW"
            else:
                # Use ordinal for day (December 2nd, not December 2)
                when = start.strftime('%A, %B ') + ordinal(start.day)

            from_time = f"{schedule.fromhour % 12 or 12}{'am' if schedule.fromhour < 12 else 'pm'}"
            to_time = f"{schedule.tohour % 12 or 12}{'am' if schedule.tohour < 12 else 'pm'}"

            status += f"\n\nNext sweeping: {when} {from_time}-{to_time}"
        else:
            status += "\n\nNo upcoming street sweeping found"

        return status


def main():
    """Test/demo functionality"""
    logging.basicConfig(level=logging.INFO)

    # Load lookup
    lookup = StreetSweepingLookup()
    manager = ParkingManager(lookup)

    # Test parsing
    test_locations = [
        "north side of Anza between 7th and 8th ave",
        "Valencia between 18th and 19th",
        "on Mission near 24th street",
    ]

    for loc_text in test_locations:
        print(f"\n{'='*60}")
        print(f"Testing: {loc_text}")
        print('='*60)

        location = manager.parser.parse(loc_text)
        if location:
            print(f"Parsed: {location}")
            manager.save_parking_location(location)
            print(f"\n{manager.get_human_readable_status()}")
        else:
            print("Failed to parse")


if __name__ == '__main__':
    main()
