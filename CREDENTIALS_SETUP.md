# Setting Up Home Assistant Credentials

This project requires credentials to connect to your Home Assistant instance. Follow these steps to set up secure credential management.

## Quick Start

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials:**
   ```bash
   nano .env  # or use your preferred editor
   ```

3. **Add your Home Assistant URL and token:**
   ```
   HA_URL=http://homeassistant.local:8123
   HA_TOKEN=your-long-lived-access-token-here
   ```

## Getting a Long-Lived Access Token

1. Log into your Home Assistant instance
2. Click your profile icon (bottom left corner)
3. Scroll down to **Security** section
4. Under **Long-Lived Access Tokens**, click **Create Token**
5. Give it a name (e.g., "Python Scripts")
6. Copy the generated token and paste it in your `.env` file

## Security Notes

- ✅ `.env` is already in `.gitignore` - your credentials won't be committed
- ✅ Use `.env.example` as a template for others (no real credentials)
- ⚠️ Never commit your actual `.env` file to version control
- ⚠️ Treat access tokens like passwords - keep them secret!

## Using Credentials in Your Scripts

### Option 1: Use the Config Loader (Recommended)

```python
from light_effects.ha_config import load_credentials

url, token = load_credentials()
```

The config loader automatically finds and loads your `.env` file.

### Option 2: Use python-dotenv Directly

```python
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv('HA_URL')
token = os.getenv('HA_TOKEN')
```

### Option 3: Environment Variables (Manual)

```bash
export HA_URL="http://homeassistant.local:8123"
export HA_TOKEN="your-token"
python your_script.py
```

## Files

- `.env` - Your actual credentials (gitignored, never commit)
- `.env.example` - Template showing what credentials are needed (safe to commit)
- `.gitignore` - Ensures `.env` is never committed
- `light_effects/ha_config.py` - Utility for loading credentials

## Troubleshooting

### "Missing credentials" error

Make sure:
1. You've created a `.env` file (not just `.env.example`)
2. The file is in the project root directory
3. Both `HA_URL` and `HA_TOKEN` are set
4. No quotes around the values in `.env`

### "Connection refused" error

Check:
1. Your Home Assistant URL is correct
2. Home Assistant is running and accessible
3. The port (usually 8123) is correct
4. You can access the URL in a browser

### "401 Unauthorized" error

Your token might be:
1. Expired or revoked
2. Copied incorrectly (check for extra spaces)
3. From a different Home Assistant instance

Generate a new token and update your `.env` file.
