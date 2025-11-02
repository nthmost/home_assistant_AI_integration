# Deployment Guide - Label Printer Service

## Overview
Deploy the label printer service as a systemd daemon on nike.local, making it accessible to other machines on the network.

## Architecture
- **Service API**: FastAPI REST service
- **Binding**: 0.0.0.0:8000 (accessible from network)
- **Process Manager**: systemd
- **Logging**: journald

## Prerequisites on nike.local

1. **Python environment**
   ```bash
   cd ~
   python3 -m venv label_venv
   source label_venv/bin/activate
   ```

2. **Directory structure**
   ```bash
   mkdir -p ~/label_printer
   mkdir -p /tmp/label_images
   ```

3. **Printer access**
   - Phomemo PM-241-BT must be configured in CUPS
   - User must have permissions to print (`lpadmin` group)

## Deployment Steps

### 1. Transfer Files to nike.local
```bash
# From project root
rsync -avz printers/PM-241-BT/ nike.local:~/label_printer/
```

### 2. Install Dependencies on nike.local
```bash
ssh nike.local
cd ~/label_printer
source ~/label_venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cd ~/label_printer
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY if using NL interface
nano .env
```

### 4. Test Service Manually
```bash
# Activate venv
source ~/label_venv/bin/activate

# Run service in foreground
python3 label_service.py --host 0.0.0.0 --port 8000

# In another terminal, test endpoints
curl http://nike.local:8000/health
curl http://nike.local:8000/api/v1/capabilities
```

### 5. Install systemd Service
```bash
# Copy service file to systemd directory
sudo cp label-printer.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable label-printer

# Start service
sudo systemctl start label-printer

# Check status
sudo systemctl status label-printer
```

### 6. Verify Service
```bash
# Check service is running
systemctl status label-printer

# View logs
journalctl -u label-printer -f

# Test from another machine
curl http://nike.local:8000/health
```

## API Usage

### Health Check
```bash
curl http://nike.local:8000/health
```

### Get Capabilities
```bash
curl http://nike.local:8000/api/v1/capabilities
```

### Print a Label
```bash
curl -X POST http://nike.local:8000/api/v1/print \
  -H "Content-Type: application/json" \
  -d '{
    "text": "JUNTAWA",
    "label_size": {
      "width_mm": 50,
      "height_mm": 50
    },
    "options": {
      "border": false,
      "dpi": 300
    }
  }'
```

### Custom Label Size
```bash
curl -X POST http://nike.local:8000/api/v1/print \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Tea - Jasmine Green",
    "label_size": {
      "width_mm": 60,
      "height_mm": 40
    },
    "options": {
      "border": true,
      "font_size": 24,
      "dpi": 300
    }
  }'
```

## Service Management

### Start/Stop/Restart
```bash
sudo systemctl start label-printer
sudo systemctl stop label-printer
sudo systemctl restart label-printer
```

### Enable/Disable Auto-start
```bash
sudo systemctl enable label-printer   # Start on boot
sudo systemctl disable label-printer  # Don't start on boot
```

### View Logs
```bash
# Follow logs in real-time
journalctl -u label-printer -f

# View recent logs
journalctl -u label-printer -n 100

# View logs since boot
journalctl -u label-printer -b
```

## Troubleshooting

### Service won't start
```bash
# Check service status
systemctl status label-printer

# Check detailed logs
journalctl -u label-printer -n 50

# Verify paths in service file
cat /etc/systemd/system/label-printer.service

# Test manually
cd ~/label_printer
source ~/label_venv/bin/activate
python3 label_service.py
```

### Printer not found
```bash
# Check CUPS printer status
lpstat -p PM-241-BT

# Check user has print permissions
groups nthmost  # Should include lpadmin or lp
```

### Port already in use
```bash
# Check what's using port 8000
sudo netstat -tlnp | grep 8000
# or
sudo ss -tlnp | grep 8000

# Edit service file to use different port
sudo nano /etc/systemd/system/label-printer.service
# Change --port 8000 to --port 8001
sudo systemctl daemon-reload
sudo systemctl restart label-printer
```

### Permission errors
```bash
# Ensure temp directory exists and is writable
mkdir -p /tmp/label_images
chmod 755 /tmp/label_images

# Check service user
systemctl show label-printer | grep User
```

## Network Discovery

### mDNS/Avahi (Optional)
To make the service discoverable via mDNS:

```bash
sudo apt install avahi-daemon

# Create service definition
sudo nano /etc/avahi/services/label-printer.service
```

Contents:
```xml
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name>Label Printer Service</name>
  <service>
    <type>_label-printer._tcp</type>
    <port>8000</port>
    <txt-record>model=PM-241-BT</txt-record>
    <txt-record>api-version=1.0</txt-record>
  </service>
</service-group>
```

## Security Considerations

1. **Firewall**: Ensure port 8000 is allowed
   ```bash
   sudo ufw allow 8000/tcp
   ```

2. **API Authentication**: Currently no auth - add API key if needed
3. **Network**: Service binds to 0.0.0.0 - accessible from local network
4. **HTTPS**: Consider adding reverse proxy (nginx) for TLS

## Updates

### Update Code
```bash
# On development machine
rsync -avz printers/PM-241-BT/ nike.local:~/label_printer/

# On nike.local
sudo systemctl restart label-printer
```

### Update Dependencies
```bash
ssh nike.local
cd ~/label_printer
source ~/label_venv/bin/activate
pip install --upgrade -r requirements.txt
sudo systemctl restart label-printer
```

## Last Updated
October 28, 2025
