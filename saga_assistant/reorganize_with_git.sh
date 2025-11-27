#!/bin/bash
# Reorganize saga_assistant directory using git mv to preserve history
#
# Run this from saga_assistant/ directory:
#   cd /Users/nthmost/projects/git/home_assistant_AI_integration/saga_assistant
#   chmod +x reorganize_with_git.sh
#   ./reorganize_with_git.sh

set -e  # Exit on any error

echo "=== Saga Assistant Directory Reorganization ==="
echo ""

# Create directories
echo "Creating directories..."
mkdir -p examples
mkdir -p docs

# Move demo scripts to examples/
echo ""
echo "Moving demo scripts to examples/..."
git mv demo_audio_devices.py examples/
git mv demo_ha_control.py examples/
git mv demo_llm.py examples/
git mv demo_memory.py examples/
git mv demo_stt.py examples/
git mv demo_timer_sounds.py examples/
git mv demo_tts.py examples/
git mv demo_wakeword.py examples/
git mv demo_weather_locations.py examples/
git mv demo_weather_v2.py examples/

# Move markdown docs to docs/
echo ""
echo "Moving markdown documentation to docs/..."
git mv EMEET_CAPABILITIES.md docs/
git mv EMEET_OPTIMIZATION_PLAN.md docs/
git mv MINNIE_FEATURE.md docs/
git mv PARKING_FEATURE.md docs/
git mv PARKING_VOICE_COMMANDS.md docs/
git mv PHASE1_RESULTS.md docs/
git mv PHASE3_SUMMARY.md docs/
git mv PRD.md docs/
git mv SESSION_NOTES_2025-11-18.md docs/
git mv TIMER_SOUNDS.md docs/

# Move service docs
echo ""
echo "Moving service documentation to docs/..."
git mv services/DEPLOYMENT.md docs/
git mv services/NFS_SETUP.md docs/

# Remove obsolete V1 weather files
echo ""
echo "Removing obsolete V1 weather files..."
git rm weather.py
git rm services/weather_cache.py
git rm services/weather_apis.py
git rm services/weather_fetcher.py
git rm services/README.md

echo ""
echo "=== Reorganization Complete! ==="
echo ""
echo "Files moved:"
echo "  - 10 demo scripts → examples/"
echo "  - 12 markdown docs → docs/"
echo "  - 5 obsolete files removed"
echo ""
echo "Next steps:"
echo "  1. Review changes: git status"
echo "  2. Commit changes: git commit -m 'Organize saga_assistant directory structure'"
echo "  3. Create examples/README.md (documentation for demos)"
echo ""
