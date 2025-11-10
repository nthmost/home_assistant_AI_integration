#!/bin/bash
# Setup script for OpenWakeWord training on loki.local
# Run this on loki.local to install all dependencies

set -e  # Exit on error

echo "🚀 Setting up OpenWakeWord training environment on loki.local"
echo "============================================================"

# Create working directory
cd ~/saga_training
echo "📁 Working directory: $(pwd)"

# Install system dependencies
echo ""
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y git wget python3-pip python3-venv

# Create Python virtual environment
echo ""
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install PyTorch with CUDA support for RTX 4080
echo ""
echo "🔥 Installing PyTorch with CUDA 12.1 support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Clone piper-sample-generator for TTS
echo ""
echo "🎤 Installing Piper TTS for sample generation..."
git clone https://github.com/rhasspy/piper-sample-generator
wget -O piper-sample-generator/models/en_US-libritts_r-medium.pt \
  'https://github.com/rhasspy/piper-sample-generator/releases/download/v2.0.0/en_US-libritts_r-medium.pt'
pip install piper-phonemize
pip install webrtcvad

# Clone and install OpenWakeWord
echo ""
echo "🎵 Installing OpenWakeWord..."
git clone https://github.com/dscripka/openwakeword
pip install -e ./openwakeword

# Install training dependencies
echo ""
echo "📚 Installing training dependencies..."
pip install mutagen==1.47.0
pip install torchinfo==1.8.0
pip install torchmetrics==1.2.0
pip install speechbrain==0.5.14
pip install audiomentations==0.33.0
pip install torch-audiomentations==0.11.0
pip install acoustics==0.2.6
pip install tensorflow-cpu==2.8.1
pip install tensorflow_probability==0.16.0
pip install onnx_tf==1.10.0
pip install pronouncing==0.2.0
pip install datasets==2.14.6
pip install deep-phonemizer==0.0.19

# Download pre-trained models
echo ""
echo "📥 Downloading OpenWakeWord base models..."
mkdir -p ./openwakeword/openwakeword/resources/models
wget https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/embedding_model.onnx \
  -O ./openwakeword/openwakeword/resources/models/embedding_model.onnx
wget https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/embedding_model.tflite \
  -O ./openwakeword/openwakeword/resources/models/embedding_model.tflite
wget https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/melspectrogram.onnx \
  -O ./openwakeword/openwakeword/resources/models/melspectrogram.onnx
wget https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/melspectrogram.tflite \
  -O ./openwakeword/openwakeword/resources/models/melspectrogram.tflite

# Test PyTorch CUDA
echo ""
echo "🧪 Testing PyTorch CUDA support..."
python3 -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Download training datasets (run download_datasets.sh)"
echo "2. Create training config for 'Hey Saga'"
echo "3. Run training script"
echo ""
echo "To activate the environment: source ~/saga_training/venv/bin/activate"
