# Parking & Street Sweeping Feature for Saga Assistant

## Overview

Saga can now help you track where you parked your car and remind you about SF street sweeping schedules!

## What It Does

1. **Remember where you parked** using natural language
2. **Look up street sweeping schedules** from offline SF data
3. **Tell you when you need to move your car**
4. **Send proactive reminders** (night before & morning of)
5. **Works 100% offline** (after initial data download)

## Files Created

### Core Modules

- **`parking.py`** - Main parking logic
  - `StreetSweepingLookup` - Queries local SF street sweeping database
  - `LocationParser` - Parses natural language parking locations
  - `ParkingManager` - Manages parking state and queries

- **`parking_reminders.py`** - Reminder/notification system
  - `ParkingReminderService` - Checks for upcoming sweeping and sends notifications

- **`sync_street_sweeping.py`** - Data synchronization
  - `StreetSweepingSyncer` - Downloads latest SF sweeping data when it changes

### Data

- **`data/street_sweeping_sf.json`** - Full SF street sweeping database (15MB, 37,878 records)
- **`data/sync_metadata.json`** - Tracks last sync timestamp
- **`~/.saga_assistant/parking_state.json`** - Current parking location and schedule
- **`~/.saga_assistant/last_parking_notification.json`** - Prevents duplicate notifications

### Demo Scripts

- **`demo_parking.py`** - Interactive demo of all features

## Usage Examples

### Tell Saga where you parked

```python
from parking import StreetSweepingLookup, ParkingManager

lookup = StreetSweepingLookup()
manager = ParkingManager(lookup)

# Natural language parsing
location = manager.parser.parse("north side of Anza between 7th and 8th ave")
manager.save_parking_location(location)
```

**Supported formats:**
- "north side of Anza between 7th and 8th ave"
- "Valencia between 18th and 19th"
- "on Mission near 24th street"
- "1234 Valencia Street" (address)

### Ask when you need to move your car

```python
# Get human-readable status
status = manager.get_human_readable_status()
print(status)
# Output:
# Parked on Anza St 07th Ave  -  08th Ave (North side)
#
# Next sweeping: Friday, November 28 8am-10am

# Get next sweeping event programmatically
next_sweep = manager.get_next_sweeping(days_ahead=14)
if next_sweep:
    schedule = next_sweep['schedule']
    start_time = next_sweep['start_time']
    # ... use the data
```

### Check for reminders

```python
from parking_reminders import ParkingReminderService

service = ParkingReminderService(ha_client=ha)
message = service.check_and_notify()
```

**Notification triggers:**
- **Night before (7pm)**: "Reminder: Street sweeping TOMORROW morning..."
- **Morning of (2 hours before)**: "URGENT: Street sweeping in 1.5 hours! Move your car now!"

### Sync street sweeping data

```bash
# Check and download if data changed
pipenv run python saga_assistant/sync_street_sweeping.py

# Force download
pipenv run python saga_assistant/sync_street_sweeping.py --force
```

## How It Works

### 1. Offline-First Architecture

- **Initial download**: Full SF DataSF street sweeping dataset (37,878 records)
- **Weekly sync**: Checks metadata API, only downloads if data changed
- **Local cache**: All lookups query local JSON file (no internet required)

### 2. Change Detection

```python
# Fast metadata check (50KB)
remote_metadata = fetch_remote_metadata()
# { 'rows_updated_at': 1750349257, ... }

# Only download if timestamp increased
if remote_timestamp > local_timestamp:
    download_full_dataset()  # 15MB
```

### 3. Natural Language Parsing

```python
# Input: "north side of Anza between 7th and 8th ave"
#
# Steps:
# 1. Normalize: "07th Ave", "08th Ave" (pad numbers)
# 2. Extract: street="anza", cross1="07th", cross2="08th Ave", side="north"
# 3. Fuzzy match: "anza" -> "Anza St"
# 4. Find block: "07th Ave  -  08th Ave" (exact match in database)
# 5. Filter: North side only
#
# Result: SweepingSchedule(
#     corridor="Anza St",
#     limits="07th Ave  -  08th Ave",
#     blockside="North",
#     weekday="Fri",
#     fullname="Fri 2nd & 4th",
#     fromhour=8,
#     tohour=10,
#     week1=False, week2=True, week3=False, week4=True, week5=False
# )
```

### 4. Week-of-Month Calculation

Street sweeping schedules use week-of-month (1st, 2nd, 3rd, 4th, 5th):

```python
def applies_to_date(schedule, date):
    # Check day of week
    if date.strftime('%a') != schedule.weekday:
        return False

    # Check week of month (1-5)
    week_of_month = (date.day - 1) // 7 + 1
    week_flags = [schedule.week1, schedule.week2, schedule.week3,
                  schedule.week4, schedule.week5]

    return week_flags[week_of_month - 1]
```

## Integration Points

### Voice Commands (Future)

Add to `intent_parser.py`:

```python
PARKING_PATTERNS = {
    "save_parking": [
        r"i parked (on )?(?P<location>.+)",
        r"my car is (on |at )?(?P<location>.+)",
    ],
    "where_parked": [
        r"where (did i park|is my car)",
    ],
    "when_to_move": [
        r"when (do i need to |should i )?move (my car|the car)",
        r"(is there )?street sweeping",
    ]
}
```

### Home Assistant Integration

**Weekly Sync Automation** (`automations.yaml`):

```yaml
- alias: "Sync Street Sweeping Data Weekly"
  trigger:
    - platform: time
      at: "03:00:00"  # 3am every Sunday
  condition:
    - condition: time
      weekday:
        - sun
  action:
    - service: shell_command.sync_street_sweeping

**Shell Command** (`configuration.yaml`):

```yaml
shell_command:
  sync_street_sweeping: >
    cd /path/to/home_assistant_AI_integration &&
    pipenv run python saga_assistant/sync_street_sweeping.py
```

**Reminder Check Automation** (periodic):

```yaml
- alias: "Check Parking Reminders"
  trigger:
    - platform: time_pattern
      hours: "*"  # Check every hour
  action:
    - service: python_script.check_parking_reminders
```

## Testing

```bash
# Run full demo
pipenv run python saga_assistant/demo_parking.py

# Test reminders
pipenv run python saga_assistant/parking_reminders.py

# Test sync
pipenv run python saga_assistant/sync_street_sweeping.py --verbose
```

## Data Source

- **Source**: San Francisco DataSF Open Data Portal
- **API**: https://data.sfgov.org/resource/yhqp-riqs.json
- **Metadata**: https://data.sfgov.org/api/views/yhqp-riqs.json
- **Update Frequency**: "As needed" when schedules change
- **Coverage**: All SF streets with sweeping schedules (1,453 unique streets)

## Next Steps

### Phase 1 (Current) ✅
- ✅ Download and cache SF street sweeping data
- ✅ Natural language location parsing
- ✅ Schedule lookup from local cache
- ✅ Parking state management
- ✅ Reminder notification system
- ✅ Weekly sync with change detection

### Phase 2 (Integrate with Saga)
- [ ] Add parking intent patterns to `intent_parser.py`
- [ ] Wire up voice commands in `run_assistant.py`
- [ ] Configure Home Assistant automation for weekly sync
- [ ] Set up periodic reminder checks
- [ ] Add notification delivery via HA

### Phase 3 (Enhanced Features)
- [ ] Home Assistant presence detection integration
  - Auto-prompt for parking location when you arrive home
  - Don't send reminders if you're not home
- [ ] Multiple vehicle support
- [ ] Historical parking log
- [ ] "Where did I park last week?" queries
- [ ] Parking zone preferences/favorites

### Phase 4 (Advanced)
- [ ] Integration with SF parking tickets API (if available)
- [ ] Parking meter expiration reminders
- [ ] Alternative parking suggestions during sweeping
- [ ] Calendar integration (add sweeping events)

## Performance

- **Dataset size**: 15MB (37,878 records)
- **Load time**: ~100ms
- **Lookup time**: <1ms (indexed by street name)
- **Sync time**: ~2 seconds (when data changes)
- **Metadata check**: ~0.5 seconds

## Error Handling

The system is designed to fail fast rather than hide errors:
- No generic exception handlers
- Missing data files raise `FileNotFoundError`
- Parse failures return `None` with logging
- Sync failures propagate network errors

This allows quick identification and fixing of issues.

## Logging

All modules use Python logging:
- `INFO`: Key operations (sync, save location, send notification)
- `WARNING`: Parse failures, missing data
- `DEBUG`: Detailed matching/lookup steps

Enable verbose logging:
```python
logging.basicConfig(level=logging.DEBUG)
```

---

**Last Updated**: November 18, 2025
**Status**: Phase 1 Complete ✅
**Next**: Integrate with Saga voice interface
