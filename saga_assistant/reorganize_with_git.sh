#!/bin/bash
# Reorganize saga_assistant directory using git mv to preserve history

set -e

echo "=== Saga Assistant Directory Reorganization ==="
echo ""

# Create directories
echo "Creating directories..."
mkdir -p examples
mkdir -p docs

# Move any remaining demo scripts to examples/
echo ""
echo "Moving demo scripts to examples/..."
for file in demo_*.py; do
    if [ -f "$file" ]; then
        git mv "$file" examples/
        echo "  Moved $file"
    fi
done

# Move markdown docs to docs/
echo ""
echo "Moving markdown documentation to docs/..."
for file in *.md; do
    if [ -f "$file" ] && [ "$file" != "README.md" ]; then
        git mv "$file" docs/
        echo "  Moved $file"
    fi
done

# Move service docs
echo ""
echo "Moving service documentation to docs/..."
if [ -f "services/DEPLOYMENT.md" ]; then
    git mv services/DEPLOYMENT.md docs/
    echo "  Moved services/DEPLOYMENT.md"
fi
if [ -f "services/NFS_SETUP.md" ]; then
    git mv services/NFS_SETUP.md docs/
    echo "  Moved services/NFS_SETUP.md"
fi

# Remove obsolete V1 weather files (only if they exist)
echo ""
echo "Removing obsolete V1 weather files..."
[ -f "weather.py" ] && git rm weather.py && echo "  Removed weather.py"
[ -f "services/weather_cache.py" ] && git rm services/weather_cache.py && echo "  Removed services/weather_cache.py"
[ -f "services/weather_apis.py" ] && git rm services/weather_apis.py && echo "  Removed services/weather_apis.py"
[ -f "services/weather_fetcher.py" ] && git rm services/weather_fetcher.py && echo "  Removed services/weather_fetcher.py"
[ -f "services/README.md" ] && git rm services/README.md && echo "  Removed services/README.md"

echo ""
echo "=== Reorganization Complete! ==="
echo ""
git status --short
echo ""
