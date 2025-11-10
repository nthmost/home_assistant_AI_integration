#!/bin/bash
# Install Piper TTS for sample generation
set -e

cd ~/saga_training
source venv/bin/activate

echo "🎤 Installing Piper TTS..."

# Clone piper-sample-generator if not present
if [ ! -d "piper-sample-generator" ]; then
    echo "Cloning piper-sample-generator..."
    git clone https://github.com/rhasspy/piper-sample-generator.git
fi

# Install piper-tts package
echo "Installing piper-tts via pip..."
pip install piper-tts

# Test if it works
echo ""
echo "Testing Piper import..."
python3 -c "from piper import PiperVoice; print('✅ Piper imported successfully')"

echo ""
echo "✅ Piper TTS installation complete!"
