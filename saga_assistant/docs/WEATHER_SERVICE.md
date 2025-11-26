# Weather Service Architecture

## Problem

The current weather implementation uses wttr.in, which is unreliable:
- Connection timeouts (3s timeout too aggressive)
- Connection resets (API instability)
- No caching (every query hits API)
- No fallback (single point of failure)

**Result**: Saga fails to answer weather queries ~50% of the time.

## Solution: Cached Weather Microservice

### Architecture

```
Background Service → API Fallback Chain → SQLite Cache → Saga (instant reads)
```

### Components

#### 1. Weather Cache Database (`~/.saga_assistant/weather.db`)

**Schema:**
```sql
CREATE TABLE weather_cache (
    id INTEGER PRIMARY KEY,
    zip_code TEXT NOT NULL,
    current_temp_f INTEGER,
    current_condition TEXT,
    current_feels_like_f INTEGER,
    current_humidity INTEGER,
    today_high_f INTEGER,
    today_low_f INTEGER,
    today_condition TEXT,
    today_rain_chance INTEGER,
    tomorrow_high_f INTEGER,
    tomorrow_low_f INTEGER,
    tomorrow_condition TEXT,
    tomorrow_rain_chance INTEGER,
    wind_speed_mph INTEGER,
    wind_direction TEXT,
    updated_at TIMESTAMP,
    UNIQUE(zip_code)
);
```

**Stale Threshold**: 30 minutes (data older than this triggers refresh)

#### 2. Weather Fetcher Service (`saga_assistant/services/weather_fetcher.py`)

**Runs every 20 minutes** as a background daemon or cron job.

**Fallback chain:**
1. OpenWeatherMap (requires `OPENWEATHER_API_KEY` in .env)
2. WeatherAPI.com (requires `WEATHERAPI_KEY` in .env)
3. wttr.in (no key needed, last resort)

**Error handling:**
- If API #1 fails → try API #2
- If API #2 fails → try API #3
- If all fail → log error, keep stale cache
- Retry with exponential backoff on transient errors

**Logging:**
- Success: "✅ Weather updated from OpenWeatherMap"
- Fallback: "⚠️ OpenWeatherMap failed, trying WeatherAPI.com"
- Failure: "❌ All weather APIs failed, using stale cache (45 min old)"

#### 3. Weather Client (`saga_assistant/weather.py` - refactored)

**Fast path (99% of queries):**
```python
def get_weather(when="now"):
    cache = WeatherCache()
    data = cache.get(zip_code="94118")

    if data and not data.is_stale():
        return format_weather(data, when)

    # Fallback: try direct API fetch
    return fetch_live_weather(when)
```

**Benefits:**
- Instant response (<10ms vs 3000ms)
- Works offline (uses last good data)
- Saga never waits for slow APIs

### Setup

#### 1. Get API Keys (Free Tiers)

**OpenWeatherMap:**
1. Sign up: https://openweathermap.org/api
2. Free tier: 1,000 calls/day, 60 calls/min
3. Add to `.env`: `OPENWEATHER_API_KEY=your_key_here`

**WeatherAPI.com:**
1. Sign up: https://www.weatherapi.com/signup.aspx
2. Free tier: 1,000,000 calls/month
3. Add to `.env`: `WEATHERAPI_KEY=your_key_here`

#### 2. Run Weather Service

**Option A: Background daemon (recommended)**
```bash
pipenv run python saga_assistant/services/weather_fetcher.py --daemon
```

**Option B: Cron job**
```bash
# Add to crontab (every 20 minutes)
*/20 * * * * cd ~/projects/git/home_assistant_AI_integration && pipenv run python saga_assistant/services/weather_fetcher.py
```

**Option C: systemd service (Linux)**
```ini
[Unit]
Description=Saga Weather Fetcher
After=network.target

[Service]
Type=simple
User=nthmost
WorkingDirectory=/Users/nthmost/projects/git/home_assistant_AI_integration
ExecStart=/Users/nthmost/.local/share/virtualenvs/home_assistant_AI_integration-15Ep8vIz/bin/python saga_assistant/services/weather_fetcher.py --daemon
Restart=always

[Install]
WantedBy=multi-user.target
```

### Implementation Phases

**Phase 1: Cache Infrastructure** ✅
- Create weather.db schema
- Implement WeatherCache class
- Add stale detection logic

**Phase 2: API Fallback Chain** ✅
- Implement OpenWeatherMap adapter
- Implement WeatherAPI.com adapter
- Keep wttr.in as last resort
- Add retry logic with exponential backoff

**Phase 3: Background Service** ✅
- Create weather_fetcher.py daemon
- 20-minute refresh cycle
- Logging to file + stdout

**Phase 4: Saga Integration** ✅
- Refactor weather.py to use cache
- Remove direct wttr.in calls
- Add fallback for stale cache

**Phase 5: Monitoring** 🔄
- Add metrics: cache hit rate, API failures
- Alert on stale data >1 hour
- Dashboard showing last successful update

## Benefits

✅ **Reliability**: 3 APIs with fallback
✅ **Speed**: Cache responds in <10ms
✅ **Offline**: Works with stale data if network down
✅ **Monitoring**: Clear logs show API health
✅ **Cost**: Free tiers handle our usage

## Migration

1. Deploy weather service
2. Wait 20 minutes for first cache
3. Update Saga to use cache
4. Monitor for 24 hours
5. Remove old wttr.in code

---

**Status**: Architecture designed, ready to implement
**Owner**: Claude Code
**Created**: 2025-11-23
