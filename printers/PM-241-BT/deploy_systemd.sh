#!/bin/bash
# Deploy label printer service as systemd daemon
# Run this script on nike.local

set -e

echo "🚀 Deploying Label Printer Service"
echo "=================================="

# Check we're in the right directory
if [ ! -f "label_service.py" ]; then
    echo "❌ Error: Run this script from ~/label_printer directory"
    exit 1
fi

# Check .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo "   ⚡ Edit .env and add ANTHROPIC_API_KEY if needed"
fi

# Create temp image directory
echo "📁 Creating temp directory..."
mkdir -p /tmp/label_images
chmod 755 /tmp/label_images

# Install systemd service
echo "🔧 Installing systemd service..."
sudo cp label-printer.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start service
echo "▶️  Enabling and starting service..."
sudo systemctl enable label-printer
sudo systemctl start label-printer

# Wait a moment for service to start
sleep 2

# Check status
echo ""
echo "📊 Service status:"
sudo systemctl status label-printer --no-pager

# Test health endpoint
echo ""
echo "🏥 Testing health endpoint..."
if curl -s http://localhost:8001/health | python3 -m json.tool; then
    echo ""
    echo "✅ Service deployed successfully!"
    echo ""
    echo "📍 Service URL: http://nike.local:8001"
    echo "📖 API docs: http://nike.local:8001/docs"
    echo ""
    echo "Useful commands:"
    echo "  sudo systemctl status label-printer   # Check status"
    echo "  sudo systemctl restart label-printer  # Restart service"
    echo "  sudo systemctl stop label-printer     # Stop service"
    echo "  journalctl -u label-printer -f        # Follow logs"
else
    echo ""
    echo "❌ Service may not be responding. Check logs:"
    echo "   journalctl -u label-printer -n 50"
fi
