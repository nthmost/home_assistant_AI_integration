#!/bin/bash
# Install weather service as local macOS launchd service
# Runs on Mac mini - simpler than nike.local + mounting!

set -e

PROJECT_DIR="$HOME/projects/git/home_assistant_AI_integration"
PLIST_FILE="$HOME/Library/LaunchAgents/com.saga.weather.plist"
VENV_PYTHON="$HOME/.local/share/virtualenvs/home_assistant_AI_integration-15Ep8vIz/bin/python"

echo "======================================"
echo "Install Saga Weather Service (Local)"
echo "======================================"
echo ""

# Check virtualenv exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtualenv not found: $VENV_PYTHON"
    echo "   Run 'pipenv install' first"
    exit 1
fi
echo "✅ Virtualenv found"
echo ""

# Create launchd plist
echo "📝 Creating launchd service..."
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.saga.weather</string>
    <key>ProgramArguments</key>
    <array>
        <string>$VENV_PYTHON</string>
        <string>$PROJECT_DIR/saga_assistant/services/weather_fetcher.py</string>
        <string>--daemon</string>
        <string>--interval</string>
        <string>20</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key>
        <string>$PROJECT_DIR</string>
    </dict>
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
EOF

echo "✅ Created: $PLIST_FILE"
echo ""

# Load service
echo "🚀 Loading service..."
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"
echo "✅ Service loaded and started"
echo ""

# Wait for first fetch
echo "⏳ Waiting for first weather fetch (5 seconds)..."
sleep 5
echo ""

# Check status
echo "📊 Service status:"
launchctl list | grep saga.weather && echo "✅ Running" || echo "⚠️  Not found"
echo ""

# Check cache
echo "🌤️  Checking weather cache..."
if [ -f "$HOME/.saga_assistant/weather.db" ]; then
    sqlite3 "$HOME/.saga_assistant/weather.db" \
        "SELECT current_temp_f, current_condition, datetime(updated_at, 'localtime') FROM weather_cache;" \
        2>/dev/null && echo "✅ Cache populated!" || echo "⏳ Still fetching..."
else
    echo "⏳ Cache not yet created (check logs)"
fi
echo ""

echo "======================================"
echo "✅ Installation Complete!"
echo "======================================"
echo ""
echo "Service Info:"
echo "  • Runs on: Mac mini (this machine)"
echo "  • Updates: Every 20 minutes"
echo "  • Cache: ~/.saga_assistant/weather.db"
echo "  • Logs: /tmp/saga-weather.log"
echo "  • Auto-start: On login"
echo ""
echo "Useful Commands:"
echo "  # View logs"
echo "  tail -f /tmp/saga-weather.log"
echo ""
echo "  # Check status"
echo "  launchctl list | grep saga"
echo ""
echo "  # Stop service"
echo "  launchctl unload $PLIST_FILE"
echo ""
echo "  # Restart service"
echo "  launchctl unload $PLIST_FILE && launchctl load $PLIST_FILE"
echo ""
echo "  # Test weather"
echo "  pipenv run python -c 'from saga_assistant.weather import get_weather; print(get_weather())'"
echo ""
