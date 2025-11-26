#!/bin/bash
# Deploy Saga Weather Service to nike.local
#
# This script:
# 1. Creates directory structure on nike.local
# 2. Copies weather service files
# 3. Installs Python dependencies
# 4. Sets up systemd service for auto-start
# 5. Starts the weather daemon

set -e  # Exit on error

REMOTE_HOST="nike.local"
REMOTE_USER=$(whoami)
REMOTE_DIR="/home/$REMOTE_USER/saga-weather"
LOCAL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

echo "======================================"
echo "Saga Weather Service Deployment"
echo "Target: $REMOTE_USER@$REMOTE_HOST"
echo "======================================"
echo ""

# Check if nike.local is reachable
echo "📡 Checking connection to $REMOTE_HOST..."
if ! ssh -o ConnectTimeout=5 $REMOTE_HOST "echo 'Connected'" > /dev/null 2>&1; then
    echo "❌ Cannot connect to $REMOTE_HOST"
    echo "   Make sure SSH is configured and the host is up"
    exit 1
fi
echo "✅ Connected to $REMOTE_HOST"
echo ""

# Check Python version
echo "🐍 Checking Python on $REMOTE_HOST..."
PYTHON_VERSION=$(ssh $REMOTE_HOST "python3 --version 2>&1" || echo "Not found")
echo "   $PYTHON_VERSION"
if [[ "$PYTHON_VERSION" == "Not found" ]]; then
    echo "❌ Python 3 not found on $REMOTE_HOST"
    echo "   Install with: sudo apt install python3 python3-pip"
    exit 1
fi
echo ""

# Create directory structure
echo "📁 Creating directory structure..."
ssh $REMOTE_HOST "mkdir -p $REMOTE_DIR/{services,.env_files}"
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

# Copy .env file (with API key)
echo "🔑 Copying .env file..."
scp "$LOCAL_DIR/.env" "$REMOTE_HOST:$REMOTE_DIR/.env"
echo "✅ API keys transferred"
echo ""

# Install Python dependencies
echo "📚 Installing Python dependencies..."
ssh $REMOTE_HOST "cd $REMOTE_DIR && python3 -m pip install --user requests python-dotenv"
echo "✅ Dependencies installed"
echo ""

# Create systemd service file
echo "⚙️  Creating systemd service..."
ssh $REMOTE_HOST "cat > /tmp/saga-weather.service << 'EOF'
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

# Install systemd service
ssh $REMOTE_HOST "sudo mv /tmp/saga-weather.service /etc/systemd/system/ && sudo systemctl daemon-reload"
echo "✅ Systemd service created"
echo ""

# Enable and start service
echo "🚀 Starting weather service..."
ssh $REMOTE_HOST "sudo systemctl enable saga-weather && sudo systemctl start saga-weather"
echo "✅ Service started and enabled (auto-start on boot)"
echo ""

# Check status
echo "📊 Service status:"
ssh $REMOTE_HOST "sudo systemctl status saga-weather --no-pager" || true
echo ""

# Test weather fetch
echo "🌤️  Testing weather fetch..."
sleep 5  # Give it time to fetch
ssh $REMOTE_HOST "sqlite3 ~/.saga_assistant/weather.db 'SELECT current_temp_f, current_condition FROM weather_cache;' 2>/dev/null" || echo "   (Cache not yet populated - check logs)"
echo ""

echo "======================================"
echo "✅ Deployment Complete!"
echo "======================================"
echo ""
echo "Service Info:"
echo "  • Host: $REMOTE_HOST"
echo "  • Location: $REMOTE_DIR"
echo "  • Cache: ~/.saga_assistant/weather.db"
echo "  • Logs: /tmp/saga-weather.log"
echo ""
echo "Useful Commands:"
echo "  # Check service status"
echo "  ssh $REMOTE_HOST 'sudo systemctl status saga-weather'"
echo ""
echo "  # View logs"
echo "  ssh $REMOTE_HOST 'tail -f /tmp/saga-weather.log'"
echo ""
echo "  # Check cache"
echo "  ssh $REMOTE_HOST 'sqlite3 ~/.saga_assistant/weather.db \"SELECT * FROM weather_cache;\"'"
echo ""
echo "  # Restart service"
echo "  ssh $REMOTE_HOST 'sudo systemctl restart saga-weather'"
echo ""
echo "  # Stop service"
echo "  ssh $REMOTE_HOST 'sudo systemctl stop saga-weather'"
echo ""
