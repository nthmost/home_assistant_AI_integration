#!/bin/bash
# Deploy Saga Weather Service to nike.local with NFS shared cache
#
# Prerequisites: Run setup_nfs_share.sh first

set -e

REMOTE_HOST="nike.local"
REMOTE_USER=$(whoami)
REMOTE_DIR="/home/$REMOTE_USER/saga-weather"
SHARED_CACHE_DIR="/home/$REMOTE_USER/saga-shared"
LOCAL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

echo "======================================"
echo "Saga Weather Service Deployment (NFS)"
echo "Target: $REMOTE_USER@$REMOTE_HOST"
echo "======================================"
echo ""

# Check NFS mount
if ! mount | grep -q "$HOME/.saga_assistant"; then
    echo "❌ NFS share not mounted!"
    echo "   Run: ./saga_assistant/services/setup_nfs_share.sh"
    exit 1
fi
echo "✅ NFS share is mounted"
echo ""

# Check connection
echo "📡 Checking connection to $REMOTE_HOST..."
if ! ssh -o ConnectTimeout=5 $REMOTE_HOST "echo 'Connected'" > /dev/null 2>&1; then
    echo "❌ Cannot connect to $REMOTE_HOST"
    exit 1
fi
echo "✅ Connected"
echo ""

# Create directories
echo "📁 Creating directories on $REMOTE_HOST..."
ssh $REMOTE_HOST "mkdir -p $REMOTE_DIR/services"
ssh $REMOTE_HOST "mkdir -p $SHARED_CACHE_DIR"
echo "✅ Directories created"
echo ""

# Copy service files
echo "📦 Copying weather service files..."
scp "$LOCAL_DIR/saga_assistant/services/weather_cache.py" \
    "$REMOTE_HOST:$REMOTE_DIR/services/"
scp "$LOCAL_DIR/saga_assistant/services/weather_apis.py" \
    "$REMOTE_HOST:$REMOTE_DIR/services/"
scp "$LOCAL_DIR/saga_assistant/services/weather_fetcher.py" \
    "$REMOTE_HOST:$REMOTE_DIR/services/"
scp "$LOCAL_DIR/saga_assistant/services/__init__.py" \
    "$REMOTE_HOST:$REMOTE_DIR/services/"
echo "✅ Files copied"
echo ""

# Copy .env file
echo "🔑 Copying .env file..."
scp "$LOCAL_DIR/.env" "$REMOTE_HOST:$REMOTE_DIR/.env"
echo "✅ API keys transferred"
echo ""

# Install dependencies
echo "📚 Installing Python dependencies..."
ssh $REMOTE_HOST "cd $REMOTE_DIR && python3 -m pip install --user requests python-dotenv"
echo "✅ Dependencies installed"
echo ""

# Create systemd service with shared cache path
echo "⚙️  Creating systemd service..."
ssh $REMOTE_HOST "cat > /tmp/saga-weather.service << 'EOF'
[Unit]
Description=Saga Weather Fetcher Service (NFS Shared)
After=network.target

[Service]
Type=simple
User=$REMOTE_USER
WorkingDirectory=$REMOTE_DIR
Environment=\"PYTHONPATH=$REMOTE_DIR\"
Environment=\"SAGA_WEATHER_DB=$SHARED_CACHE_DIR/weather.db\"
ExecStart=/usr/bin/python3 $REMOTE_DIR/services/weather_fetcher.py --daemon --interval 20
Restart=always
RestartSec=60
StandardOutput=append:/tmp/saga-weather.log
StandardError=append:/tmp/saga-weather-error.log

[Install]
WantedBy=multi-user.target
EOF"

# Update weather_cache.py to use environment variable for DB path
echo "🔧 Configuring cache to use shared directory..."
ssh $REMOTE_HOST "cat > $REMOTE_DIR/patch_cache.py << 'PYEOF'
import sys
with open('$REMOTE_DIR/services/weather_cache.py', 'r') as f:
    content = f.read()

# Add environment variable support
if 'SAGA_WEATHER_DB' not in content:
    content = content.replace(
        'if db_path is None:',
        '''if db_path is None:
            import os
            db_path_env = os.getenv('SAGA_WEATHER_DB')
            if db_path_env:
                db_path = Path(db_path_env)
                db_path.parent.mkdir(parents=True, exist_ok=True)
            else:'''
    )
    # Fix indentation
    content = content.replace(
        '            else:\n            db_path = Path.home()',
        '                db_path = Path.home()'
    )

    with open('$REMOTE_DIR/services/weather_cache.py', 'w') as f:
        f.write(content)
    print('✅ Patched weather_cache.py to use SAGA_WEATHER_DB')
else:
    print('ℹ️  Already patched')
PYEOF
python3 $REMOTE_DIR/patch_cache.py"
echo "✅ Cache configured for shared directory"
echo ""

# Install systemd service
ssh $REMOTE_HOST "sudo mv /tmp/saga-weather.service /etc/systemd/system/ && sudo systemctl daemon-reload"
echo "✅ Systemd service installed"
echo ""

# Enable and start
echo "🚀 Starting weather service..."
ssh $REMOTE_HOST "sudo systemctl enable saga-weather && sudo systemctl start saga-weather"
echo "✅ Service started and enabled"
echo ""

# Wait for first fetch
echo "⏳ Waiting for initial weather fetch (5 seconds)..."
sleep 5
echo ""

# Check status
echo "📊 Service status:"
ssh $REMOTE_HOST "sudo systemctl status saga-weather --no-pager -n 10" || true
echo ""

# Test cache
echo "🌤️  Testing weather cache..."
if [ -f "$HOME/.saga_assistant/weather.db" ]; then
    echo "✅ Cache file exists on Mac!"
    sqlite3 "$HOME/.saga_assistant/weather.db" "SELECT current_temp_f, current_condition, datetime(updated_at, 'localtime') FROM weather_cache;" 2>/dev/null && echo "✅ Cache data readable!" || echo "⏳ Cache populating..."
else
    echo "⏳ Cache file not yet created (check logs)"
fi
echo ""

echo "======================================"
echo "✅ Deployment Complete!"
echo "======================================"
echo ""
echo "Configuration:"
echo "  • Nike: $REMOTE_HOST:$SHARED_CACHE_DIR/weather.db"
echo "  • Mac:  $HOME/.saga_assistant/weather.db (NFS mount)"
echo "  • Both point to SAME file!"
echo ""
echo "Verify:"
echo "  # Check service"
echo "  ssh $REMOTE_HOST 'sudo systemctl status saga-weather'"
echo ""
echo "  # View logs"
echo "  ssh $REMOTE_HOST 'tail -f /tmp/saga-weather.log'"
echo ""
echo "  # Test from Mac"
echo "  sqlite3 ~/.saga_assistant/weather.db 'SELECT * FROM weather_cache;'"
echo ""
echo "  # Test Saga weather"
echo "  pipenv run python -c 'from saga_assistant.weather import get_weather; print(get_weather())'"
echo ""
