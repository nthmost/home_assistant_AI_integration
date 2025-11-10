#!/bin/bash
# Complete setup with Python 3.11 on loki.local
set -e

cd ~/saga_training
source venv/bin/activate

echo "🚀 Installing training environment with Python 3.11"
echo "Python version: $(python --version)"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install PyTorch with CUDA support
echo ""
echo "🔥 Installing PyTorch with CUDA 12.1..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install piper-phonemize (should work with Python 3.11)
echo ""
echo "🎤 Installing piper-phonemize..."
pip install piper-phonemize==1.1.0

# Install webrtcvad
echo ""
echo "📚 Installing webrtcvad..."
pip install webrtcvad

# Clone OpenWakeWord if not already present
echo ""
echo "🎵 Installing OpenWakeWord..."
if [ ! -d "openwakeword" ]; then
    git clone https://github.com/dscripka/openwakeword
fi
pip install -e ./openwakeword

# Install all training dependencies
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

# Download OpenWakeWord base models
echo ""
echo "📥 Downloading OpenWakeWord base models..."
mkdir -p ./openwakeword/openwakeword/resources/models

if [ ! -f "./openwakeword/openwakeword/resources/models/embedding_model.onnx" ]; then
    wget -q https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/embedding_model.onnx \
      -O ./openwakeword/openwakeword/resources/models/embedding_model.onnx
fi

if [ ! -f "./openwakeword/openwakeword/resources/models/embedding_model.tflite" ]; then
    wget -q https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/embedding_model.tflite \
      -O ./openwakeword/openwakeword/resources/models/embedding_model.tflite
fi

if [ ! -f "./openwakeword/openwakeword/resources/models/melspectrogram.onnx" ]; then
    wget -q https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/melspectrogram.onnx \
      -O ./openwakeword/openwakeword/resources/models/melspectrogram.onnx
fi

if [ ! -f "./openwakeword/openwakeword/resources/models/melspectrogram.tflite" ]; then
    wget -q https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/melspectrogram.tflite \
      -O ./openwakeword/openwakeword/resources/models/melspectrogram.tflite
fi

# Test PyTorch CUDA
echo ""
echo "🧪 Testing PyTorch CUDA support..."
python3 -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Training environment ready on loki.local!"
echo "Python: $(python --version)"
echo "Workspace: ~/saga_training/"
echo ""
echo "Next steps:"
echo "1. Transfer training config (hey_saga_config.yaml)"
echo "2. Download training datasets"
echo "3. Train 'Hey Saga' model"
