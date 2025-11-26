# Saga Weather Service

Fast, reliable weather data with caching and API fallback.

## Quick Start

### 1. Test Current Setup (Already Working!)

```bash
# One-time fetch to populate cache
pipenv run python saga_assistant/services/weather_fetcher.py

# Test Saga's weather queries
pipenv run python -c "from saga_assistant.weather import get_weather; print(get_weather(when='tomorrow'))"
```

### 2. Run as Background Service (Recommended)

The weather fetcher should run continuously to keep the cache fresh:

```bash
# Run daemon (updates every 20 minutes)
pipenv run python saga_assistant/services/weather_fetcher.py --daemon
```

**Keep this running in the background** while Saga is active. Options:

**Option A: Terminal Tab**
```bash
# Run in dedicated terminal tab
cd ~/projects/git/home_assistant_AI_integration
pipenv run python saga_assistant/services/weather_fetcher.py --daemon
```

**Option B: tmux/screen**
```bash
# Create detached session
tmux new -d -s weather 'cd ~/projects/git/home_assistant_AI_integration && pipenv run python saga_assistant/services/weather_fetcher.py --daemon'

# Check it's running
tmux ls

# Attach to see output
tmux attach -t weather
```

**Option C: macOS launchd Service** (Runs on startup)

Create `~/Library/LaunchAgents/com.saga.weather.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.saga.weather</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/nthmost/.local/share/virtualenvs/home_assistant_AI_integration-15Ep8vIz/bin/python</string>
        <string>/Users/nthmost/projects/git/home_assistant_AI_integration/saga_assistant/services/weather_fetcher.py</string>
        <string>--daemon</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/nthmost/projects/git/home_assistant_AI_integration</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/saga-weather.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/saga-weather-error.log</string>
</dict>
</plist>
```

Then:
```bash
# Load service
launchctl load ~/Library/LaunchAgents/com.saga.weather.plist

# Check status
launchctl list | grep saga

# View logs
tail -f /tmp/saga-weather.log

# Unload if needed
launchctl unload ~/Library/LaunchAgents/com.saga.weather.plist
```

## Architecture

```
┌─────────────────────────────────┐
│  Weather Fetcher (Daemon)       │
│  Runs every 20 minutes          │
│  - Tries OpenWeatherMap         │
│  - Falls back to WeatherAPI.com │
│  - Falls back to wttr.in        │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│  SQLite Cache                   │
│  ~/.saga_assistant/weather.db   │
│  - Current conditions           │
│  - Today/tomorrow forecast      │
│  - Stale after 30 minutes       │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│  Saga Assistant                 │
│  - Reads cache (<10ms!)         │
│  - Falls back to API if stale   │
│  - Uses stale cache if API down │
└─────────────────────────────────┘
```

## Configuration

API keys in `.env`:

```bash
# Required (at least one)
OPENWEATHER_API_KEY=your_key_here    # Free: 1,000 calls/day
WEATHERAPI_KEY=your_key_here         # Free: 1M calls/month
```

## Benefits

✅ **Fast**: <10ms response (vs 3000ms with direct API)
✅ **Reliable**: 3 API fallbacks + stale cache fallback
✅ **Offline**: Works with last cached data if network down
✅ **Free**: Uses free tier APIs efficiently

## Monitoring

```bash
# Check cache status
sqlite3 ~/.saga_assistant/weather.db "SELECT zip_code, current_temp_f, current_condition, datetime(updated_at, 'localtime') FROM weather_cache;"

# Test weather queries
pipenv run python -c "from saga_assistant.weather import get_weather; print(get_weather())"
pipenv run python -c "from saga_assistant.weather import will_it_rain; print(will_it_rain('tomorrow'))"
pipenv run python -c "from saga_assistant.weather import get_wind_info; print(get_wind_info())"
```

## Troubleshooting

**Cache not updating?**
- Check daemon is running: `ps aux | grep weather_fetcher`
- Check logs if using launchd: `tail -f /tmp/saga-weather.log`
- Run manual fetch: `pipenv run python saga_assistant/services/weather_fetcher.py`

**API failures?**
- Verify API key in `.env`: `grep OPENWEATHER .env`
- Check API quota: https://home.openweathermap.org/api_keys
- Try backup API: Add `WEATHERAPI_KEY` to `.env`

**Stale data?**
- Check last update: See "Monitoring" section above
- Daemon may have stopped - restart it
- APIs may be down - check logs

---

**Status**: ✅ Working (OpenWeatherMap configured)
**Last Updated**: 2025-11-23
