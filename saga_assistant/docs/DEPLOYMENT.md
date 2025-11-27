# Weather Service Deployment to nike.local

## Architecture

```
┌─────────────────────────────────────┐
│  nike.local (24/7 server)           │
│  - Weather fetcher daemon           │
│  - SQLite cache (local)             │
│  - Updates every 20 minutes         │
└─────────────────────────────────────┘
           ↓ (shared via NFS/SMB)
┌─────────────────────────────────────┐
│  Mac mini M4 (Saga host)            │
│  - Mounts nike's cache              │
│  - Reads weather instantly          │
│  - No API calls needed              │
└─────────────────────────────────────┘
```

## Deployment Options

### Option 1: Shared Database (Recommended - Simplest)

Nike runs the weather daemon, Mac mini reads from a shared database.

**Steps:**

1. **On nike.local**: Run the weather daemon
   ```bash
   ./saga_assistant/services/deploy_to_nike.sh
   ```

2. **Set up NFS share** (or SMB if you prefer):

   On nike.local:
   ```bash
   # Create shared directory
   mkdir -p /home/$USER/saga-shared

   # Configure NFS export
   sudo bash -c 'echo "/home/$USER/saga-shared *(rw,sync,no_subtree_check)" >> /etc/exports'
   sudo exportfs -ra
   ```

3. **On Mac mini**: Mount the share
   ```bash
   # Create mount point
   mkdir -p ~/.saga_assistant

   # Mount (add to /etc/fstab for auto-mount)
   sudo mount -t nfs nike.local:/home/$USER/saga-shared ~/.saga_assistant
   ```

4. **Update nike's daemon** to write to shared location:
   ```bash
   ssh nike.local
   # Edit weather_fetcher.py cache path to use /home/$USER/saga-shared/weather.db
   ```

**Pros**: Mac mini never calls weather APIs, reads are instant
**Cons**: Requires NFS setup

### Option 2: Standalone Service (Alternative)

Nike runs the service completely independently, Mac mini accesses via HTTP API.

**Setup:**

1. Deploy to nike.local:
   ```bash
   ./saga_assistant/services/deploy_to_nike.sh
   ```

2. The deployment script will:
   - Copy service files to `~/saga-weather/` on nike.local
   - Install Python dependencies
   - Create systemd service
   - Start daemon (updates every 20 minutes)

3. Update Mac mini's weather.py to point to nike's cache:
   ```python
   # In saga_assistant/services/weather_cache.py
   # Change default path to NFS mount or add remote access
   ```

## Quick Deployment

### Prerequisites

- SSH access to nike.local configured
- Python 3 installed on nike.local
- Sudo access on nike.local (for systemd)

### Deploy

```bash
cd ~/projects/git/home_assistant_AI_integration
./saga_assistant/services/deploy_to_nike.sh
```

This will:
1. ✅ Check connection to nike.local
2. ✅ Copy weather service files
3. ✅ Copy .env with API key
4. ✅ Install Python dependencies
5. ✅ Create systemd service
6. ✅ Start daemon (auto-starts on boot)

### Verify

```bash
# Check service is running
ssh nike.local 'sudo systemctl status saga-weather'

# View logs
ssh nike.local 'tail -f /tmp/saga-weather.log'

# Check cache
ssh nike.local 'sqlite3 ~/.saga_assistant/weather.db "SELECT current_temp_f, current_condition, datetime(updated_at, \"localtime\") FROM weather_cache;"'
```

## Configuration

### Change Update Interval

Default: 20 minutes

To change:
```bash
# Edit systemd service
ssh nike.local 'sudo nano /etc/systemd/system/saga-weather.service'

# Change: --interval 20
# To:     --interval 10  (for 10 minutes)

# Reload and restart
ssh nike.local 'sudo systemctl daemon-reload && sudo systemctl restart saga-weather'
```

### Change ZIP Code

Default: 94118

To change:
```bash
# Edit systemd service
ssh nike.local 'sudo nano /etc/systemd/system/saga-weather.service'

# Add: --zip 90210

# Reload and restart
ssh nike.local 'sudo systemctl daemon-reload && sudo systemctl restart saga-weather'
```

## Accessing Cache from Mac Mini

### Option A: NFS Mount (Best for LAN)

```bash
# One-time setup
mkdir -p ~/.saga_assistant

# Mount nike's cache directory
sudo mount -t nfs nike.local:/home/$USER/.saga_assistant ~/.saga_assistant

# Add to /etc/fstab for auto-mount on boot:
# nike.local:/home/$USER/.saga_assistant /Users/nthmost/.saga_assistant nfs rw,bg,hard,intr 0 0
```

### Option B: SSH Database Access

If you don't want NFS, modify `weather_cache.py` to support remote access:

```python
# Add remote database access
class WeatherCache:
    def __init__(self, remote_host: Optional[str] = None):
        if remote_host:
            # Copy database via SSH before reading
            subprocess.run(['scp', f'{remote_host}:~/.saga_assistant/weather.db',
                          '/tmp/weather.db'], check=True)
            self.db_path = Path('/tmp/weather.db')
        else:
            self.db_path = Path.home() / '.saga_assistant' / 'weather.db'
```

Usage:
```python
cache = WeatherCache(remote_host='nike.local')
```

### Option C: HTTP API (Most Flexible)

Create a simple Flask API on nike.local that serves weather data:

```python
# On nike.local
from flask import Flask, jsonify
from weather_cache import WeatherCache

app = Flask(__name__)

@app.route('/weather/<zip_code>')
def get_weather(zip_code):
    cache = WeatherCache()
    data = cache.get(zip_code)
    if data:
        return jsonify(data.to_dict())
    return jsonify({'error': 'No data'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)
```

Then on Mac mini:
```python
import requests
response = requests.get('http://nike.local:5555/weather/94118')
data = response.json()
```

## Monitoring

### Service Status
```bash
ssh nike.local 'sudo systemctl status saga-weather'
```

### Live Logs
```bash
ssh nike.local 'tail -f /tmp/saga-weather.log'
```

### Cache Contents
```bash
ssh nike.local 'sqlite3 ~/.saga_assistant/weather.db "SELECT * FROM weather_cache;"'
```

### Manual Fetch
```bash
ssh nike.local 'cd ~/saga-weather && python3 services/weather_fetcher.py'
```

## Troubleshooting

### Service won't start
```bash
# Check logs
ssh nike.local 'sudo journalctl -u saga-weather -n 50'

# Test manually
ssh nike.local 'cd ~/saga-weather && python3 services/weather_fetcher.py'
```

### API failures
```bash
# Verify API key
ssh nike.local 'grep OPENWEATHER ~/saga-weather/.env'

# Test API directly
ssh nike.local 'curl "https://api.openweathermap.org/data/2.5/forecast?zip=94118,US&appid=YOUR_KEY&units=imperial"'
```

### Cache not updating
```bash
# Check service is running
ssh nike.local 'ps aux | grep weather_fetcher'

# Check last update time
ssh nike.local 'stat ~/.saga_assistant/weather.db'

# Restart service
ssh nike.local 'sudo systemctl restart saga-weather'
```

---

**Status**: Ready to deploy
**Created**: 2025-11-23
