# Weather Service NFS Setup

Deploy weather daemon to nike.local with NFS-shared cache.

## Architecture

```
nike.local                          Mac mini M4
┌─────────────────────────┐        ┌──────────────────────┐
│ Weather Daemon          │        │ Saga Assistant       │
│ Updates every 20min     │        │ Reads instantly      │
│                         │        │                      │
│ /home/user/saga-shared/ │◄──NFS─►│ ~/.saga_assistant/   │
│   └── weather.db        │        │   └── weather.db     │
│                         │        │                      │
│ SAME FILE - SHARED!     │        │ Zero latency!        │
└─────────────────────────┘        └──────────────────────┘
```

## Two-Step Setup

### Step 1: Setup NFS Share

This configures nike.local to share the cache directory:

```bash
./saga_assistant/services/setup_nfs_share.sh
```

**What it does:**
- ✅ Installs NFS server on nike.local
- ✅ Creates shared directory: `/home/$USER/saga-shared/`
- ✅ Exports it via NFS
- ✅ Mounts it on Mac at: `~/.saga_assistant/`
- ✅ Adds to /etc/fstab (auto-mount on boot)

**You may need to:**
- Enter your sudo password (for mounting)
- Allow firewall access on nike.local if prompted

### Step 2: Deploy Weather Service

This deploys the weather daemon to nike.local:

```bash
./saga_assistant/services/deploy_to_nike_nfs.sh
```

**What it does:**
- ✅ Copies weather service files
- ✅ Copies API key from .env
- ✅ Installs Python dependencies
- ✅ Patches cache to use shared directory
- ✅ Creates systemd service (auto-start)
- ✅ Starts the daemon

**Result:**
Nike fetches weather every 20 minutes → writes to shared DB → Mac reads instantly!

## Verify It's Working

### Check NFS mount is active:
```bash
mount | grep saga_assistant
# Should show: nike.local:/home/user/saga-shared on /Users/nthmost/.saga_assistant
```

### Check service is running on nike:
```bash
ssh nike.local 'sudo systemctl status saga-weather'
# Should show: active (running)
```

### Watch it fetch weather:
```bash
ssh nike.local 'tail -f /tmp/saga-weather.log'
# You'll see: "✅ Weather cache updated for 94118"
```

### Test from Mac mini:
```bash
# Check cache exists
ls -la ~/.saga_assistant/weather.db

# Query weather
sqlite3 ~/.saga_assistant/weather.db "SELECT current_temp_f, current_condition FROM weather_cache;"

# Test Saga's weather
pipenv run python -c "from saga_assistant.weather import get_weather; print(get_weather())"
```

## Benefits

✅ **Nike does the work** - Mac mini just reads (no API calls)
✅ **Instant responses** - Database is always local (NFS mount)
✅ **Reliable** - Nike stays up 24/7, keeps cache fresh
✅ **Zero config in Saga** - Existing code works unchanged!
✅ **Auto-recovery** - Service auto-restarts, mount persists

## Troubleshooting

### NFS mount fails

**Check NFS server is running:**
```bash
ssh nike.local 'sudo systemctl status nfs-kernel-server'
```

**Check exports:**
```bash
showmount -e nike.local
```

**Check firewall:**
```bash
ssh nike.local 'sudo ufw status'
# May need: sudo ufw allow from 192.168.1.0/24 to any port nfs
```

**Remount manually:**
```bash
sudo umount ~/.saga_assistant
sudo mount -t nfs -o resvport nike.local:/home/$USER/saga-shared ~/.saga_assistant
```

### Weather service not running

**Check service status:**
```bash
ssh nike.local 'sudo systemctl status saga-weather'
```

**View detailed logs:**
```bash
ssh nike.local 'sudo journalctl -u saga-weather -n 50'
```

**Test manually:**
```bash
ssh nike.local 'cd ~/saga-weather && python3 services/weather_fetcher.py'
```

**Restart service:**
```bash
ssh nike.local 'sudo systemctl restart saga-weather'
```

### Cache not updating

**Check last update time:**
```bash
stat ~/.saga_assistant/weather.db
```

**View live logs:**
```bash
ssh nike.local 'tail -f /tmp/saga-weather.log'
```

**Force manual update:**
```bash
ssh nike.local 'cd ~/saga-weather && python3 services/weather_fetcher.py'
```

### API failures

**Verify API key:**
```bash
ssh nike.local 'grep OPENWEATHER ~/saga-weather/.env'
```

**Test API directly:**
```bash
ssh nike.local 'curl "https://api.openweathermap.org/data/2.5/forecast?zip=94118,US&appid=b27a3d9b8d64979f7a19fb3f6a3cd73f&units=imperial" | head -20'
```

## Maintenance

### Change update interval

Edit systemd service:
```bash
ssh nike.local 'sudo nano /etc/systemd/system/saga-weather.service'
# Change: --interval 20
# To:     --interval 10

ssh nike.local 'sudo systemctl daemon-reload && sudo systemctl restart saga-weather'
```

### Change ZIP code

```bash
ssh nike.local 'sudo nano /etc/systemd/system/saga-weather.service'
# Add: --zip 90210

ssh nike.local 'sudo systemctl daemon-reload && sudo systemctl restart saga-weather'
```

### View service configuration

```bash
ssh nike.local 'cat /etc/systemd/system/saga-weather.service'
```

### Restart after nike reboot

Service auto-starts, but NFS mount persists in /etc/fstab. Just verify:
```bash
mount | grep saga_assistant
```

If not mounted, run:
```bash
sudo mount -a  # Mounts all /etc/fstab entries
```

## Uninstall

```bash
# Unmount NFS
sudo umount ~/.saga_assistant
sudo sed -i '' '/saga-shared/d' /etc/fstab

# Stop service on nike
ssh nike.local 'sudo systemctl stop saga-weather && sudo systemctl disable saga-weather'

# Remove files
ssh nike.local 'rm -rf ~/saga-weather ~/saga-shared'
```

---

**Status**: Ready to deploy
**Created**: 2025-11-23
