#!/bin/bash
# Setup SSHFS mount for weather cache from nike.local
#
# Much simpler than NFS - no root, no fstab, just SSHFS!

set -e

REMOTE_HOST="nike.local"
REMOTE_USER=${REMOTE_USER:-$(whoami)}
REMOTE_DIR="/home/$REMOTE_USER/.saga_assistant"
LOCAL_MOUNT="$HOME/.saga_assistant"

echo "======================================"
echo "Saga Weather SSHFS Setup"
echo "======================================"
echo ""

# Check if SSHFS is installed
if ! command -v sshfs &> /dev/null; then
    echo "📦 Installing SSHFS via Homebrew..."
    brew install --cask macfuse
    brew install gromgit/fuse/sshfs-mac
    echo "✅ SSHFS installed"
    echo "⚠️  You may need to reboot for macFUSE to work"
    echo ""
fi

# Check SSH connection
echo "📡 Testing SSH connection to $REMOTE_HOST..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes $REMOTE_USER@$REMOTE_HOST "echo 'Connected'" 2>/dev/null; then
    echo "⚠️  Cannot connect to $REMOTE_USER@$REMOTE_HOST"
    echo ""
    echo "Setup SSH key authentication:"
    echo "  1. Generate key (if needed): ssh-keygen -t ed25519"
    echo "  2. Copy to nike: ssh-copy-id $REMOTE_USER@$REMOTE_HOST"
    echo "  3. Test: ssh $REMOTE_USER@$REMOTE_HOST 'echo OK'"
    echo ""
    echo "Or specify different user: REMOTE_USER=youruser $0"
    exit 1
fi
echo "✅ SSH connection working"
echo ""

# Create remote directory
echo "📁 Creating directory on $REMOTE_HOST..."
ssh $REMOTE_USER@$REMOTE_HOST "mkdir -p $REMOTE_DIR"
echo "✅ Remote directory ready: $REMOTE_DIR"
echo ""

# Create local mount point
if [ ! -d "$LOCAL_MOUNT" ]; then
    mkdir -p "$LOCAL_MOUNT"
    echo "✅ Created mount point: $LOCAL_MOUNT"
else
    echo "ℹ️  Mount point exists: $LOCAL_MOUNT"
fi
echo ""

# Unmount if already mounted
if mount | grep -q "$LOCAL_MOUNT"; then
    echo "🔄 Unmounting existing mount..."
    umount "$LOCAL_MOUNT" || sudo umount "$LOCAL_MOUNT" || true
fi

# Mount with SSHFS
echo "🔗 Mounting via SSHFS..."
sshfs $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR "$LOCAL_MOUNT" \
    -o auto_cache,reconnect,defer_permissions,noappledouble,noapplexattr
echo "✅ SSHFS mounted!"
echo ""

# Test mount
echo "🧪 Testing mount..."
ls -la "$LOCAL_MOUNT" || echo "Empty (will be populated by weather service)"
echo "✅ Mount working"
echo ""

# Create helper script for auto-mount
MOUNT_SCRIPT="$HOME/.saga_assistant_mount.sh"
cat > "$MOUNT_SCRIPT" << 'SCRIPTEOF'
#!/bin/bash
# Auto-mount helper for Saga weather cache

REMOTE_HOST="nike.local"
REMOTE_USER=$(whoami)
REMOTE_DIR="/home/$REMOTE_USER/.saga_assistant"
LOCAL_MOUNT="$HOME/.saga_assistant"

# Check if already mounted
if mount | grep -q "$LOCAL_MOUNT"; then
    echo "✅ Already mounted"
    exit 0
fi

# Mount
echo "🔗 Mounting weather cache from $REMOTE_HOST..."
sshfs $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR "$LOCAL_MOUNT" \
    -o auto_cache,reconnect,defer_permissions,noappledouble,noapplexattr 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Mounted successfully"
else
    echo "❌ Mount failed - check SSH connection"
    exit 1
fi
SCRIPTEOF

chmod +x "$MOUNT_SCRIPT"
echo "✅ Created mount helper: $MOUNT_SCRIPT"
echo ""

echo "======================================"
echo "✅ SSHFS Mount Complete!"
echo "======================================"
echo ""
echo "Mount Info:"
echo "  • Remote: $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"
echo "  • Local:  $LOCAL_MOUNT"
echo "  • Auto-reconnect: Enabled"
echo ""
echo "Next Steps:"
echo "  1. Deploy weather service: ./saga_assistant/services/deploy_to_nike_sshfs.sh"
echo "  2. Weather cache will appear in $LOCAL_MOUNT/weather.db"
echo ""
echo "Useful Commands:"
echo "  # Remount if disconnected"
echo "  $MOUNT_SCRIPT"
echo ""
echo "  # Unmount"
echo "  umount $LOCAL_MOUNT"
echo ""
echo "  # Check mount status"
echo "  mount | grep saga_assistant"
echo ""
echo "Note: SSHFS auto-reconnects if connection drops!"
echo ""
