#!/bin/bash
# Finish OpenWakeWord training setup on loki.local
# Run after piper-phonemize is built

set -e

cd ~/saga_training
source venv/bin/activate

# Install piper-phonemize Python package (using the built version)
echo "🎤 Installing piper-phonemize Python package..."
pip install -e ./piper-phonemize

# Install remaining dependencies
echo "📚 Installing remaining dependencies..."
pip install webrtcvad

# Install all training dependencies
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

# Download pre-trained models if not already downloaded
echo "📥 Checking OpenWakeWord base models..."
mkdir -p ./openwakeword/openwakeword/resources/models

if [ ! -f "./openwakeword/openwakeword/resources/models/embedding_model.onnx" ]; then
    wget https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/embedding_model.onnx \
      -O ./openwakeword/openwakeword/resources/models/embedding_model.onnx
fi

if [ ! -f "./openwakeword/openwakeword/resources/models/embedding_model.tflite" ]; then
    wget https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/embedding_model.tflite \
      -O ./openwakeword/openwakeword/resources/models/embedding_model.tflite
fi

if [ ! -f "./openwakeword/openwakeword/resources/models/melspectrogram.onnx" ]; then
    wget https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/melspectrogram.onnx \
      -O ./openwakeword/openwakeword/resources/models/melspectrogram.onnx
fi

if [ ! -f "./openwakeword/openwakeword/resources/models/melspectrogram.tflite" ]; then
    wget https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/melspectrogram.tflite \
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
echo "Workspace: ~/saga_training/"
echo ""
echo "Next steps:"
echo "1. Transfer training config (hey_saga_config.yaml)"
echo "2. Download training datasets"
echo "3. Train 'Hey Saga' model"
