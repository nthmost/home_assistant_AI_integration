#!/bin/bash
# Deploy Saga Weather Service to nike.local with SSHFS shared cache

set -e

REMOTE_HOST="nike.local"
REMOTE_USER=${REMOTE_USER:-$(whoami)}
REMOTE_DIR="/home/$REMOTE_USER/saga-weather"
LOCAL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

echo "======================================"
echo "Saga Weather Deployment (SSHFS)"
echo "Target: $REMOTE_USER@$REMOTE_HOST"
echo "======================================"
echo ""

# Check SSHFS mount
if ! mount | grep -q "$HOME/.saga_assistant"; then
    echo "⚠️  SSHFS not mounted!"
    echo "   Run: ./saga_assistant/services/setup_sshfs.sh"
    echo ""
    read -p "Try to mount now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./saga_assistant/services/setup_sshfs.sh
    else
        exit 1
    fi
fi
echo "✅ SSHFS mounted"
echo ""

# Check connection
echo "📡 Testing connection..."
if ! ssh -o ConnectTimeout=5 $REMOTE_USER@$REMOTE_HOST "echo 'OK'" > /dev/null 2>&1; then
    echo "❌ Cannot connect to $REMOTE_USER@$REMOTE_HOST"
    exit 1
fi
echo "✅ Connected"
echo ""

# Create directories
echo "📁 Creating directories..."
ssh $REMOTE_USER@$REMOTE_HOST "mkdir -p $REMOTE_DIR/services"
ssh $REMOTE_USER@$REMOTE_HOST "mkdir -p ~/.saga_assistant"
echo "✅ Directories created"
echo ""

# Copy service files
echo "📦 Copying service files..."
scp "$LOCAL_DIR/saga_assistant/services/weather_cache.py" \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/services/"
scp "$LOCAL_DIR/saga_assistant/services/weather_apis.py" \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/services/"
scp "$LOCAL_DIR/saga_assistant/services/weather_fetcher.py" \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/services/"
scp "$LOCAL_DIR/saga_assistant/services/__init__.py" \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/services/"
echo "✅ Files copied"
echo ""

# Copy .env
echo "🔑 Copying API key..."
scp "$LOCAL_DIR/.env" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/.env"
echo "✅ API key transferred"
echo ""

# Install dependencies
echo "📚 Installing Python dependencies..."
ssh $REMOTE_USER@$REMOTE_HOST "python3 -m pip install --user requests python-dotenv"
echo "✅ Dependencies installed"
echo ""

# Create systemd service
echo "⚙️  Creating systemd service..."
ssh $REMOTE_USER@$REMOTE_HOST "cat > /tmp/saga-weather.service << 'EOF'
[Unit]
Description=Saga Weather Fetcher Service
After=network.target

[Service]
Type=simple
User=$REMOTE_USER
WorkingDirectory=$REMOTE_DIR
Environment=\"PYTHONPATH=$REMOTE_DIR\"
ExecStart=/usr/bin/python3 $REMOTE_DIR/services/weather_fetcher.py --daemon --interval 20
Restart=always
RestartSec=60
StandardOutput=append:/tmp/saga-weather.log
StandardError=append:/tmp/saga-weather-error.log

[Install]
WantedBy=multi-user.target
EOF"

# Install service
ssh $REMOTE_USER@$REMOTE_HOST "sudo mv /tmp/saga-weather.service /etc/systemd/system/ && sudo systemctl daemon-reload"
echo "✅ Service installed"
echo ""

# Enable and start
echo "🚀 Starting service..."
ssh $REMOTE_USER@$REMOTE_HOST "sudo systemctl enable saga-weather && sudo systemctl start saga-weather"
echo "✅ Service started"
echo ""

# Wait for first fetch
echo "⏳ Waiting for initial weather fetch..."
sleep 8
echo ""

# Check status
echo "📊 Service status:"
ssh $REMOTE_USER@$REMOTE_HOST "sudo systemctl status saga-weather --no-pager -n 10" || true
echo ""

# Test cache via SSHFS mount
echo "🌤️  Testing weather cache..."
if [ -f "$HOME/.saga_assistant/weather.db" ]; then
    echo "✅ Cache visible via SSHFS!"
    sqlite3 "$HOME/.saga_assistant/weather.db" \
        "SELECT current_temp_f, current_condition, datetime(updated_at, 'localtime') FROM weather_cache;" \
        2>/dev/null && echo "✅ Data readable!" || echo "⏳ Populating..."
else
    echo "⏳ Cache file not yet created (check logs in 20 seconds)"
fi
echo ""

echo "======================================"
echo "✅ Deployment Complete!"
echo "======================================"
echo ""
echo "Configuration:"
echo "  • Nike: ~/.saga_assistant/weather.db"
echo "  • Mac:  ~/.saga_assistant/weather.db (SSHFS mount)"
echo "  • Updates: Every 20 minutes"
echo ""
echo "Verify:"
echo "  # Check service"
echo "  ssh $REMOTE_USER@$REMOTE_HOST 'sudo systemctl status saga-weather'"
echo ""
echo "  # View logs"
echo "  ssh $REMOTE_USER@$REMOTE_HOST 'tail -f /tmp/saga-weather.log'"
echo ""
echo "  # Test from Mac"
echo "  sqlite3 ~/.saga_assistant/weather.db 'SELECT * FROM weather_cache;'"
echo ""
echo "  # Test Saga"
echo "  pipenv run python -c 'from saga_assistant.weather import get_weather; print(get_weather())'"
echo ""
echo "  # Remount if needed"
echo "  ~/.saga_assistant_mount.sh"
echo ""
