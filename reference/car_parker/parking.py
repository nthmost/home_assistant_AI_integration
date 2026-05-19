#!/usr/bin/env python3
"""
SF Parking and Street Sweeping lookup.
Adapted from saga_assistant/parking.py (home_assistant_AI_integration project).
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

DATA_DIR = Path(__file__).parent / "data"
SWEEPING_DATA_FILE = DATA_DIR / "street_sweeping_sf.json"
PARKING_STATE_FILE = DATA_DIR / "parking_state.json"

WEEK_FIELDS = ['week1', 'week2', 'week3', 'week4', 'week5']

WEEKDAY_MAP = {
    'Monday': 'Mon', 'Mon': 'Mon',
    'Tuesday': 'Tue', 'Tue': 'Tue',
    'Wednesday': 'Wed', 'Wed': 'Wed',
    'Thursday': 'Thu', 'Thu': 'Thu',
    'Friday': 'Fri', 'Fri': 'Fri',
    'Saturday': 'Sat', 'Sat': 'Sat',
    'Sunday': 'Sun', 'Sun': 'Sun',
}


def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


@dataclass
class ParkingLocation:
    street: str
    cross_street_1: Optional[str]
    cross_street_2: Optional[str]
    side: str  # North, South, East, West, Unknown
    block_limits: Optional[str]  # e.g., "07th Ave  -  08th Ave"
    timestamp: str
    raw_input: str


@dataclass
class SweepingSchedule:
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
        day_name = date.strftime('%a')
        if day_name != self.weekday:
            return False
        week_of_month = (date.day - 1) // 7 + 1
        week_applies = [self.week1, self.week2, self.week3, self.week4, self.week5]
        if week_of_month > 5:
            week_of_month = 5
        return week_applies[week_of_month - 1]

    def get_datetime_range(self, date: datetime) -> Tuple[datetime, datetime]:
        start = date.replace(hour=self.fromhour, minute=0, second=0, microsecond=0)
        end = date.replace(hour=self.tohour, minute=0, second=0, microsecond=0)
        return start, end

    def weeks_description(self) -> str:
        weeks = []
        for i, applies in enumerate([self.week1, self.week2, self.week3, self.week4, self.week5], 1):
            if applies:
                weeks.append(ordinal(i))
        return ', '.join(weeks)

    def to_dict(self) -> dict:
        return {
            'corridor': self.corridor,
            'limits': self.limits,
            'blockside': self.blockside,
            'weekday': self.weekday,
            'fullname': self.fullname,
            'fromhour': self.fromhour,
            'tohour': self.tohour,
            'weeks': self.weeks_description(),
            'holidays': self.holidays,
        }


class StreetSweepingLookup:
    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or SWEEPING_DATA_FILE
        self.data: List[Dict] = []
        self.street_index: Dict[str, List[Dict]] = {}
        self._load_data()

    def _load_data(self):
        if not self.data_file.exists():
            raise FileNotFoundError(
                f"Street sweeping data not found at {self.data_file}. "
                f"Run: python sync.py"
            )
        with open(self.data_file, 'r') as f:
            self.data = json.load(f)
        for record in self.data:
            street = record['corridor']
            if street not in self.street_index:
                self.street_index[street] = []
            self.street_index[street].append(record)
        logger.info(f"Loaded {len(self.data)} records covering {len(self.street_index)} streets")

    def get_street_names(self) -> List[str]:
        return sorted(self.street_index.keys())

    def find_street(self, street_query: str) -> Optional[str]:
        street_query = street_query.strip().title()
        if street_query in self.street_index:
            return street_query
        for suffix in [' St', ' Ave', ' Blvd', ' Dr', ' Way', ' Ln']:
            candidate = street_query + suffix
            if candidate in self.street_index:
                return candidate
        matches = get_close_matches(street_query, self.street_index.keys(), n=3, cutoff=0.6)
        if matches:
            return matches[0]
        return None

    def find_streets_prefix(self, prefix: str, limit: int = 20) -> List[str]:
        """Return streets starting with prefix (case-insensitive), for autocomplete."""
        import re
        prefix = prefix.strip().lower()
        # Also try zero-padded form: "9th" -> "09th"
        padded = re.sub(r'^(\d)(st|nd|rd|th)', lambda m: f'0{m.group(1)}{m.group(2)}', prefix)
        results = [s for s in self.get_street_names()
                   if s.lower().startswith(prefix) or (padded != prefix and s.lower().startswith(padded))]
        return results[:limit]

    def get_valid_sides(self, street: str, block_limits: Optional[str] = None) -> List[str]:
        street_name = self.find_street(street)
        if not street_name:
            return []
        records = self.street_index.get(street_name, [])
        if block_limits:
            records = [r for r in records if r['limits'] == block_limits]
        sides = set()
        for record in records:
            side = record.get('blockside', '').strip()
            if side:
                sides.add(side)
        return sorted(list(sides))

    def lookup_schedule(
        self,
        street: str,
        block_limits: Optional[str] = None,
        side: Optional[str] = None
    ) -> List[SweepingSchedule]:
        street_name = self.find_street(street)
        if not street_name:
            return []
        records = self.street_index.get(street_name, [])
        if block_limits:
            records = [r for r in records if r['limits'] == block_limits]
        if side and side.lower() != 'unknown':
            records = [r for r in records if r.get('blockside', '').lower() == side.lower()]
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
        street_name = self.find_street(street)
        if not street_name:
            return []
        records = self.street_index.get(street_name, [])
        return sorted(set(r['limits'] for r in records))


class LocationParser:
    PATTERNS = [
        r'(?P<side>north|south|east|west)\s+side\s+of\s+(?P<street>[\w\s]+)\s+between\s+(?P<cross1>[\w\s]+)\s+and\s+(?P<cross2>[\w\s]+)',
        r'(?P<street>[\w\s]+)\s+between\s+(?P<cross1>[\w\s]+)\s+and\s+(?P<cross2>[\w\s]+)',
        r'on\s+(?P<street>[\w\s]+)\s+near\s+(?P<cross1>[\w\s]+)',
        r'(?P<address>\d+)\s+(?P<street>[\w\s]+)',
        r'(?:on\s+)?(?P<street>[\w\s]+?)\s+(?:street|st|avenue|ave|blvd|boulevard|drive|dr|road|rd)\b',
    ]

    def __init__(self, lookup: StreetSweepingLookup):
        self.lookup = lookup

    def normalize_avenue_number(self, text: str) -> str:
        def pad_number(match):
            num = match.group(1)
            suffix = match.group(2)
            return f"{int(num):02d}{suffix}"
        text = re.sub(r'\b(\d{1,2})(st|nd|rd|th)\b', pad_number, text, flags=re.IGNORECASE)
        text = re.sub(r'\b(ave|avenue)\b', 'Ave', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(st|street)\b', 'St', text, flags=re.IGNORECASE)
        return text

    def parse(self, location_text: str) -> Optional[ParkingLocation]:
        location_text = location_text.lower().strip()
        location_text = self.normalize_avenue_number(location_text)
        for pattern in self.PATTERNS:
            match = re.search(pattern, location_text, re.IGNORECASE)
            if match:
                return self._process_match(match, location_text)
        return None

    def _process_match(self, match, raw_input: str) -> Optional[ParkingLocation]:
        data = match.groupdict()
        street = data.get('street', '').strip()
        cross1 = data.get('cross1', '').strip() if 'cross1' in data else None
        cross2 = data.get('cross2', '').strip() if 'cross2' in data else None
        side = data.get('side', '').strip().title() if 'side' in data else None

        street_name = self.lookup.find_street(street)
        if not street_name:
            return None

        block_limits = None
        if cross1 and cross2:
            cross1_norm = self.normalize_avenue_number(cross1)
            cross2_norm = self.normalize_avenue_number(cross2)
            all_blocks = self.lookup.get_all_blocks_for_street(street_name)
            for block in all_blocks:
                if cross1_norm in block and cross2_norm in block:
                    block_limits = block
                    break

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
    def __init__(self, lookup: StreetSweepingLookup, state_file: Optional[Path] = None):
        self.lookup = lookup
        self.state_file = state_file or PARKING_STATE_FILE
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.parser = LocationParser(lookup)

    def save_parking_location(self, location: ParkingLocation, extra: Optional[Dict] = None):
        schedules = self.lookup.lookup_schedule(
            location.street,
            location.block_limits,
            location.side
        )
        state = {
            'location': asdict(location),
            'schedules': [asdict(s) for s in schedules],
            'saved_at': datetime.now(timezone.utc).isoformat(),
            'time_limit': (extra or {}).get('time_limit'),
            'lat': (extra or {}).get('lat'),
            'lng': (extra or {}).get('lng'),
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def save_gps_location(self, lat: float, lng: float, time_limit: Optional[Dict]):
        """Save a GPS-only location when no sweeping record was found nearby."""
        state = {
            'location': {
                'street': 'Unknown',
                'cross_street_1': None,
                'cross_street_2': None,
                'side': 'Unknown',
                'block_limits': None,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'raw_input': f'GPS {lat:.5f},{lng:.5f}',
            },
            'schedules': [],
            'saved_at': datetime.now(timezone.utc).isoformat(),
            'time_limit': time_limit,
            'lat': lat,
            'lng': lng,
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def save_structured_location(self, street: str, block_limits: Optional[str], side: str):
        """Save from structured form data (street dropdown + block dropdown + side)."""
        schedules = self.lookup.lookup_schedule(street, block_limits, side)
        location = ParkingLocation(
            street=street,
            cross_street_1=None,
            cross_street_2=None,
            side=side,
            block_limits=block_limits,
            timestamp=datetime.now(timezone.utc).isoformat(),
            raw_input=f"{street} {block_limits or ''} {side} side"
        )
        state = {
            'location': asdict(location),
            'schedules': [asdict(s) for s in schedules],
            'saved_at': datetime.now(timezone.utc).isoformat()
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def clear_parking(self):
        if self.state_file.exists():
            self.state_file.unlink()

    def load_parking_state(self) -> Optional[Dict]:
        if not self.state_file.exists():
            return None
        with open(self.state_file, 'r') as f:
            return json.load(f)

    def get_next_sweeping(self, days_ahead: int = 14) -> Optional[Dict]:
        state = self.load_parking_state()
        if not state:
            return None
        schedules_data = state.get('schedules', [])
        if not schedules_data:
            return None

        schedules = [SweepingSchedule(**s) for s in schedules_data]
        now = datetime.now()
        next_event = None

        for day_offset in range(days_ahead):
            check_date = now + timedelta(days=day_offset)
            for schedule in schedules:
                if schedule.applies_to_date(check_date):
                    start_time, end_time = schedule.get_datetime_range(check_date)
                    if end_time < now:
                        continue
                    if next_event is None or start_time < next_event['start_time']:
                        next_event = {
                            'schedule': schedule,
                            'date': check_date,
                            'start_time': start_time,
                            'end_time': end_time,
                        }
            if next_event:
                break  # stop at first day that has an event

        return next_event

    def get_status(self) -> Dict:
        """Return full status dict for the API."""
        state = self.load_parking_state()
        if not state:
            return {'parked': False}

        location = state['location']
        next_sweep = self.get_next_sweeping()

        result = {
            'parked': True,
            'location': location,
            'saved_at': state.get('saved_at'),
            'schedules': state.get('schedules', []),
            'next_sweeping': None,
            'time_limit': state.get('time_limit'),
            'lat': state.get('lat'),
            'lng': state.get('lng'),
            'urgency': 'safe',  # safe | soon | urgent | now
        }

        if next_sweep:
            now = datetime.now()
            start = next_sweep['start_time']
            end = next_sweep['end_time']
            delta = start - now

            # Format time
            from_h = next_sweep['schedule'].fromhour
            to_h = next_sweep['schedule'].tohour
            from_str = f"{from_h % 12 or 12}{'am' if from_h < 12 else 'pm'}"
            to_str = f"{to_h % 12 or 12}{'am' if to_h < 12 else 'pm'}"

            total_seconds = int(delta.total_seconds())
            if total_seconds < 0:
                when_label = "NOW"
                urgency = 'now'
            elif delta.days == 0 and total_seconds < 7200:  # < 2 hours
                hours = total_seconds // 3600
                mins = (total_seconds % 3600) // 60
                when_label = f"in {hours}h {mins}m" if hours else f"in {mins} min"
                urgency = 'urgent'
            elif delta.days == 0:
                urgency = 'soon'
                when_label = f"today {from_str}–{to_str}"
            elif delta.days == 1:
                urgency = 'soon'
                when_label = f"tomorrow {from_str}–{to_str}"
            else:
                urgency = 'safe'
                day_str = start.strftime('%A, %b ') + ordinal(start.day)
                when_label = f"{day_str} {from_str}–{to_str}"

            result['next_sweeping'] = {
                'when_label': when_label,
                'start_iso': start.isoformat(),
                'end_iso': end.isoformat(),
                'weekday': next_sweep['schedule'].weekday,
                'side': next_sweep['schedule'].blockside,
            }
            result['urgency'] = urgency

        return result
