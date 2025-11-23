#!/bin/bash
#
# Fetch Broadlink codes from Home Assistant server via SSH
#
# This script SSHs to your Home Assistant server and extracts
# the learned IR commands for the 'squawkers' device.
#

set -e

HA_HOST="${HA_HOST:-homeassistant.local}"

echo "========================================================================"
echo "FETCH BROADLINK CODES FROM HOME ASSISTANT"
echo "========================================================================"
echo ""
echo "Connecting to: $HA_HOST"
echo ""
echo "Note: You may need to:"
echo "  1. Enable SSH access in Home Assistant"
echo "  2. Set up SSH keys or use password authentication"
echo ""
echo "Set custom host: export HA_HOST=your-ha-hostname"
echo ""
echo "------------------------------------------------------------------------"
echo ""

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "⚠️  Warning: 'jq' not found. Output will be raw JSON."
    echo "   Install with: brew install jq"
    echo ""
    JQ_CMD="cat"
else
    JQ_CMD="jq"
fi

echo "▶ Fetching Broadlink storage files..."
echo ""

# SSH to HA and get the codes
ssh "root@$HA_HOST" 'cat /config/.storage/broadlink_remote_*_codes' 2>/dev/null | \
    $JQ_CMD '.data' | \
    grep -A 100 '"squawkers"' || {
        echo "❌ Failed to connect or find codes"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Check SSH access: ssh root@$HA_HOST"
        echo "  2. Check file exists: ssh root@$HA_HOST 'ls /config/.storage/broadlink_*'"
        echo "  3. Verify device name is 'squawkers' in HA"
        echo ""
        exit 1
    }

echo ""
echo "========================================================================"
echo ""
echo "To use these commands:"
echo "  squawkers.command('Command Name')"
echo ""
echo "Or see MY_COMMANDS.md for convenience methods."
echo ""
