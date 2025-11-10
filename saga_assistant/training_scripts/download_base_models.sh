#!/bin/bash
# Download OpenWakeWord base models
set -e

cd ~/saga_training

echo "📥 Downloading OpenWakeWord base models..."
mkdir -p ./openwakeword/openwakeword/resources/models

MODELS_DIR="./openwakeword/openwakeword/resources/models"
DOWNLOADED=0
FAILED=0

# Function to check if file is valid (not empty, not 404 page)
check_file() {
    local file=$1
    if [ ! -f "$file" ]; then
        return 1
    fi
    # Check if file is not empty
    if [ ! -s "$file" ]; then
        echo "  ⚠️  File exists but is empty: $file"
        return 1
    fi
    # Check file size is reasonable (> 100KB for these models)
    local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    if [ "$size" -lt 100000 ]; then
        echo "  ⚠️  File too small (${size} bytes), likely corrupt: $file"
        return 1
    fi
    return 0
}

# Download embedding model (ONNX)
FILE="$MODELS_DIR/embedding_model.onnx"
if check_file "$FILE"; then
    echo "✅ embedding_model.onnx already exists ($(ls -lh "$FILE" | awk '{print $5}'))"
else
    echo "📥 Downloading embedding_model.onnx..."
    if wget https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/embedding_model.onnx -O "$FILE"; then
        echo "  ✅ Downloaded successfully"
        DOWNLOADED=$((DOWNLOADED + 1))
    else
        echo "  ❌ Download failed"
        FAILED=$((FAILED + 1))
    fi
fi

# Download embedding model (TFLite)
FILE="$MODELS_DIR/embedding_model.tflite"
if check_file "$FILE"; then
    echo "✅ embedding_model.tflite already exists ($(ls -lh "$FILE" | awk '{print $5}'))"
else
    echo "📥 Downloading embedding_model.tflite..."
    if wget https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/embedding_model.tflite -O "$FILE"; then
        echo "  ✅ Downloaded successfully"
        DOWNLOADED=$((DOWNLOADED + 1))
    else
        echo "  ❌ Download failed"
        FAILED=$((FAILED + 1))
    fi
fi

# Download melspectrogram model (ONNX)
FILE="$MODELS_DIR/melspectrogram.onnx"
if check_file "$FILE"; then
    echo "✅ melspectrogram.onnx already exists ($(ls -lh "$FILE" | awk '{print $5}'))"
else
    echo "📥 Downloading melspectrogram.onnx..."
    if wget https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/melspectrogram.onnx -O "$FILE"; then
        echo "  ✅ Downloaded successfully"
        DOWNLOADED=$((DOWNLOADED + 1))
    else
        echo "  ❌ Download failed"
        FAILED=$((FAILED + 1))
    fi
fi

# Download melspectrogram model (TFLite)
FILE="$MODELS_DIR/melspectrogram.tflite"
if check_file "$FILE"; then
    echo "✅ melspectrogram.tflite already exists ($(ls -lh "$FILE" | awk '{print $5}'))"
else
    echo "📥 Downloading melspectrogram.tflite..."
    if wget https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/melspectrogram.tflite -O "$FILE"; then
        echo "  ✅ Downloaded successfully"
        DOWNLOADED=$((DOWNLOADED + 1))
    else
        echo "  ❌ Download failed"
        FAILED=$((FAILED + 1))
    fi
fi

echo ""
echo "=========================================="
if [ $FAILED -gt 0 ]; then
    echo "❌ Download failed for $FAILED file(s)"
    exit 1
elif [ $DOWNLOADED -gt 0 ]; then
    echo "✅ Downloaded $DOWNLOADED new file(s)"
else
    echo "✅ All base models already present"
fi
echo "=========================================="
echo ""
echo "Final verification:"
ls -lh "$MODELS_DIR"/*.onnx
ls -lh "$MODELS_DIR"/*.tflite
