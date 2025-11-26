# Multi-Location Weather System (V2)

5-day forecasts for multiple locations - perfect for bike ride planning!

## Features

✅ **Multi-location support** - SF, Marin City, Sausalito, Daly City
✅ **5-day forecasts** - Plan your week
✅ **Comparison mode** - Find the best riding conditions
✅ **Week summaries** - Quick weather overview
✅ **Fast queries** - All data cached locally

## Quick Start

### 1. Test the System

```bash
# Fetch weather for all locations
pipenv run python saga_assistant/services/weather_fetcher_v2.py

# Query the data
pipenv run python -c "from saga_assistant.weather_v2 import get_weather, compare_locations; print(get_weather('Marin City', 'tomorrow')); print(compare_locations(['San Francisco', 'Marin City', 'Sausalito'], 'tomorrow'))"
```

### 2. Run as Service (Linux/systemd)

```bash
# Copy service file
sudo cp saga_assistant/services/saga-weather.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable saga-weather
sudo systemctl start saga-weather

# Check status
sudo systemctl status saga-weather

# View logs
sudo journalctl -u saga-weather -f
```

### 3. Run as Service (macOS/launchd)

```bash
# Copy the plist (adjust paths for your system)
cp saga_assistant/services/com.saga.weather.plist ~/Library/LaunchAgents/

# Edit the plist to update paths:
# - Update ProgramArguments paths
# - Update WorkingDirectory

# Load service
launchctl load ~/Library/LaunchAgents/com.saga.weather.plist

# Check logs
tail -f /tmp/saga-weather.log
```

### 4. Run Manually (Any Platform)

```bash
# One-time fetch
pipenv run python saga_assistant/services/weather_fetcher_v2.py

# Run as daemon
pipenv run python saga_assistant/services/weather_fetcher_v2.py --daemon --interval 20
```

## Configuration

### Add/Change Locations

Edit `saga_assistant/services/bike_locations.json`:

```json
{
  "locations": [
    {
      "name": "Your Location",
      "zip": "94XXX",
      "description": "Description"
    }
  ]
}
```

### Change Update Interval

Default: 20 minutes

```bash
# In systemd service file
ExecStart=/usr/bin/python3 ... --interval 10

# Or for daemon mode
python weather_fetcher_v2.py --daemon --interval 10
```

## Usage Examples

### Current Weather

```python
from saga_assistant.weather_v2 import get_weather

print(get_weather('San Francisco'))
# "In San Francisco, it's 55 degrees and partly cloudy"

print(get_weather('Marin City', 'tomorrow'))
# "Tomorrow in Marin City: clear sky, high of 58, low of 48"
```

### Week Summary

```python
from saga_assistant.weather_v2 import get_week_summary

print(get_week_summary('Sausalito'))
# "This week in Sausalito: mostly clear sky, highs around 60, lows around 50"
```

### Compare Locations (Bike Planning!)

```python
from saga_assistant.weather_v2 import compare_locations

print(compare_locations(['San Francisco', 'Marin City', 'Daly City'], 'Saturday'))
# Shows comparison with best location for biking
```

### Query by Day

```python
get_weather('San Francisco', 'today')
get_weather('San Francisco', 'tomorrow')
get_weather('San Francisco', 'Monday')
get_weather('San Francisco', 'day 3')
```

## Database

V2 uses a new database: `~/.saga_assistant/weather_v2.db`

Tables:
- `current_weather` - Current conditions per location
- `daily_forecasts` - 5-day forecasts per location

The old V1 database (`weather.db`) is still there but unused.

## API Usage

OpenWeatherMap free tier:
- 1,000 calls/day
- 60 calls/minute
- 5-day forecast included

We fetch 4 locations every 20 minutes = **288 calls/day** (well within limits)

## Monitoring

```bash
# Check service status (systemd)
sudo systemctl status saga-weather

# View logs
tail -f /tmp/saga-weather.log

# Check cache
sqlite3 ~/.saga_assistant/weather_v2.db "SELECT location, date, high_f, condition FROM daily_forecasts;"

# List cached locations
sqlite3 ~/.saga_assistant/weather_v2.db "SELECT DISTINCT location FROM current_weather;"
```

## Troubleshooting

**No data for a location:**
- Check location is in `bike_locations.json`
- Check logs: `tail -f /tmp/saga-weather.log`
- Run manual fetch: `pipenv run python saga_assistant/services/weather_fetcher_v2.py`

**API failures:**
- Verify API key: `grep OPENWEATHER .env`
- Check quota: https://home.openweathermap.org/api_keys
- Try manual API call to test

**Service not starting (systemd):**
```bash
sudo journalctl -u saga-weather -n 50
sudo systemctl restart saga-weather
```

**Service not starting (macOS):**
```bash
launchctl list | grep saga
cat /tmp/saga-weather-error.log
```

---

**Status**: Production ready
**Created**: 2025-11-23
