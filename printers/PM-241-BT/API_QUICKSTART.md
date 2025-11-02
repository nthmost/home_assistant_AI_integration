# Label Printer Service API - Quick Start

## Service Overview
REST API for printing labels on Phomemo PM-241-BT thermal printer with configurable dimensions.

**Service URL**: `http://nike.local:8001`
**API Docs**: `http://nike.local:8001/docs` (interactive Swagger UI)

---

## Quick Examples

### Check Service Health
```bash
curl http://nike.local:8001/health
```

### Get Printer Capabilities
```bash
curl http://nike.local:8001/api/v1/capabilities | jq
```

### Print a Label
```bash
curl -X POST http://nike.local:8001/api/v1/print \
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

---

## API Endpoints

### `GET /health`
Health check - returns service status

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-29T03:00:00.000000",
  "service": "label-printer-service"
}
```

### `GET /api/v1/capabilities`
Get printer capabilities and supported label sizes

**Response**:
```json
{
  "printer_name": "PM-241-BT",
  "available": true,
  "supported_dpi": [203, 300],
  "default_label_sizes": {
    "rectangular": {"width_mm": 29.6, "height_mm": 32.2},
    "square_small": {"width_mm": 50.0, "height_mm": 50.0},
    "square_large": {"width_mm": 60.0, "height_mm": 60.0}
  },
  "max_label_size_mm": {"width_mm": 100.0, "height_mm": 150.0},
  "min_label_size_mm": {"width_mm": 20.0, "height_mm": 20.0}
}
```

### `POST /api/v1/print`
Print a label with custom text and dimensions

**Request Body**:
```json
{
  "text": "Kitchen - Tea",
  "label_size": {
    "width_mm": 50,
    "height_mm": 50
  },
  "options": {
    "border": true,
    "font_size": null,
    "dpi": 300
  }
}
```

**Fields**:
- `text` (required): Text to print (1-100 characters)
- `label_size` (required):
  - `width_mm`: Label width in millimeters
  - `height_mm`: Label height in millimeters
- `options` (optional):
  - `border`: Draw border around label (default: false)
  - `font_size`: Font size in points (default: auto-sized)
  - `dpi`: Image DPI (default: 300)

**Success Response** (200):
```json
{
  "success": true,
  "message": "Label printed successfully",
  "job_id": "20251029_030000",
  "image_path": "/tmp/label_images/label_20251029_030000.png"
}
```

**Error Response** (503):
```json
{
  "detail": "Printer PM-241-BT is not available"
}
```

---

## Python Client Example

```python
import requests

def print_label(text, width_mm=50, height_mm=50, border=False):
    """Print a label via API"""
    response = requests.post(
        "http://nike.local:8001/api/v1/print",
        json={
            "text": text,
            "label_size": {
                "width_mm": width_mm,
                "height_mm": height_mm
            },
            "options": {
                "border": border,
                "dpi": 300
            }
        }
    )
    return response.json()

# Usage
result = print_label("JUNTAWA", width_mm=50, height_mm=50, border=True)
print(result)
```

---

## Common Label Sizes

| Description | Width (mm) | Height (mm) | Use Case |
|-------------|------------|-------------|----------|
| Small square | 50 | 50 | Short labels |
| Large square | 60 | 60 | More text |
| Default rectangular | 29.6 | 32.2 | Current loaded labels |
| Wide label | 60 | 40 | Long text |

**Important**: Always match the API label size to the physical labels loaded in the printer!

---

## Testing the API

### Run the test script
```bash
cd ~/label_printer
python3 test_api.py
```

### Interactive API docs
Visit `http://nike.local:8001/docs` for Swagger UI where you can test endpoints interactively.

---

## Service Management

```bash
# Check service status
sudo systemctl status label-printer

# Restart service
sudo systemctl restart label-printer

# View logs
journalctl -u label-printer -f

# Stop service
sudo systemctl stop label-printer
```

---

## Voice Integration Path

Now that the API is running as a daemon, you can:

1. **Call from Home Assistant**
   - Create automation triggered by voice command
   - Use REST integration to call the API
   - Example: "Hey Jarvis, print a label that says JUNTAWA"

2. **Call from any machine**
   - Python script, Node.js, curl, etc.
   - Service is network-accessible at `nike.local:8001`

3. **Add to service discovery**
   - mDNS/Avahi for automatic discovery
   - Register with Home Assistant as a REST service

---

## Troubleshooting

### Service not responding
```bash
journalctl -u label-printer -n 50
sudo systemctl restart label-printer
```

### Printer not available (503 error)
```bash
# Check printer status
lpstat -p PM-241-BT

# Ensure printer is on and connected
# Check user has print permissions
groups nthmost  # Should include lpadmin or lp
```

### Port conflict
If port 8001 is in use, edit `/etc/systemd/system/label-printer.service` and change `--port 8001` to another port.

---

## Next Steps

1. ✅ Service is deployed and running
2. ✅ API endpoints are accessible
3. 🔜 Integrate with voice assistant (Home Assistant, custom agent, etc.)
4. 🔜 Add authentication if exposing outside local network
5. 🔜 Add service discovery (mDNS) for automatic detection

---

**Last Updated**: October 28, 2025
