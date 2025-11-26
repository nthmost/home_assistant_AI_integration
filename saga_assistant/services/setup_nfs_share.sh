#!/bin/bash
# Setup NFS share on nike.local for weather cache
#
# This script:
# 1. Installs NFS server on nike.local
# 2. Creates shared directory for weather cache
# 3. Configures NFS export
# 4. Mounts the share on Mac mini
# 5. Deploys weather service to use shared location

set -e

REMOTE_HOST="nike.local"
REMOTE_USER=$(whoami)
SHARED_DIR="/home/$REMOTE_USER/saga-shared"
LOCAL_MOUNT="$HOME/.saga_assistant"

echo "======================================"
echo "Saga Weather NFS Setup"
echo "======================================"
echo ""

# Step 1: Check connection
echo "📡 Checking connection to $REMOTE_HOST..."
if ! ssh -o ConnectTimeout=5 $REMOTE_HOST "echo 'Connected'" > /dev/null 2>&1; then
    echo "❌ Cannot connect to $REMOTE_HOST"
    exit 1
fi
echo "✅ Connected"
echo ""

# Step 2: Install NFS server on nike.local
echo "📦 Installing NFS server on $REMOTE_HOST..."
ssh $REMOTE_HOST "sudo apt update && sudo apt install -y nfs-kernel-server" || {
    echo "⚠️  Installation failed - may already be installed"
}
echo "✅ NFS server ready"
echo ""

# Step 3: Create shared directory
echo "📁 Creating shared directory on $REMOTE_HOST..."
ssh $REMOTE_HOST "mkdir -p $SHARED_DIR"
echo "✅ Directory created: $SHARED_DIR"
echo ""

# Step 4: Configure NFS export
echo "🔧 Configuring NFS export..."
MAC_IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1 || echo "192.168.1.0/24")
echo "   Allowing access from: $MAC_IP"

ssh $REMOTE_HOST "sudo bash -c 'echo \"$SHARED_DIR $MAC_IP/24(rw,sync,no_subtree_check,no_root_squash)\" >> /etc/exports'"
ssh $REMOTE_HOST "sudo exportfs -ra"
ssh $REMOTE_HOST "sudo systemctl restart nfs-kernel-server"
echo "✅ NFS export configured"
echo ""

# Step 5: Test NFS from Mac
echo "🧪 Testing NFS availability..."
showmount -e $REMOTE_HOST || {
    echo "⚠️  showmount failed - NFS may need firewall rules"
    echo "   On nike.local, run:"
    echo "   sudo ufw allow from $MAC_IP to any port nfs"
}
echo ""

# Step 6: Mount on Mac mini
echo "🔗 Mounting NFS share on Mac mini..."

# Create mount point if needed
if [ ! -d "$LOCAL_MOUNT" ]; then
    mkdir -p "$LOCAL_MOUNT"
    echo "   Created mount point: $LOCAL_MOUNT"
fi

# Check if already mounted
if mount | grep -q "$LOCAL_MOUNT"; then
    echo "   Already mounted, unmounting first..."
    sudo umount "$LOCAL_MOUNT" || true
fi

# Mount the share
sudo mount -t nfs -o resvport $REMOTE_HOST:$SHARED_DIR "$LOCAL_MOUNT"
echo "✅ NFS share mounted at $LOCAL_MOUNT"
echo ""

# Step 7: Test mount
echo "🧪 Testing mount..."
ls -la "$LOCAL_MOUNT"
echo "✅ Mount working"
echo ""

# Step 8: Add to fstab for auto-mount
echo "📋 Adding to /etc/fstab for auto-mount on boot..."
FSTAB_ENTRY="$REMOTE_HOST:$SHARED_DIR $LOCAL_MOUNT nfs rw,bg,hard,intr,tcp,resvport 0 0"

if grep -q "$REMOTE_HOST:$SHARED_DIR" /etc/fstab 2>/dev/null; then
    echo "   ℹ️  Already in /etc/fstab"
else
    echo "   Adding entry (requires sudo)..."
    echo "$FSTAB_ENTRY" | sudo tee -a /etc/fstab
    echo "✅ Added to /etc/fstab"
fi
echo ""

echo "======================================"
echo "✅ NFS Share Setup Complete!"
echo "======================================"
echo ""
echo "NFS Info:"
echo "  • Remote: $REMOTE_HOST:$SHARED_DIR"
echo "  • Local:  $LOCAL_MOUNT"
echo "  • Status: Mounted and auto-mount enabled"
echo ""
echo "Next Steps:"
echo "  1. Deploy weather service to nike.local"
echo "  2. Weather cache will be created in shared directory"
echo "  3. Saga will read from shared cache automatically"
echo ""
echo "Run: ./saga_assistant/services/deploy_to_nike_nfs.sh"
echo ""
