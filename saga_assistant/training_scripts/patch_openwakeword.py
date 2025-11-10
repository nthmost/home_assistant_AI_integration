#!/usr/bin/env python3
"""
Patch OpenWakeWord's train.py to work with newer piper-sample-generator
that requires a 'model' parameter in generate_samples()
"""

import sys
from pathlib import Path

def patch_train_py():
    """Add model parameter to all generate_samples() calls"""

    train_py = Path("openwakeword/openwakeword/train.py")

    if not train_py.exists():
        print(f"❌ Error: {train_py} not found")
        return False

    print(f"📝 Patching {train_py}...")

    with open(train_py, 'r') as f:
        content = f.read()

    # Check if already patched
    if 'model=config.get("piper_model_path"' in content:
        print("✅ Already patched!")
        return True

    # Pattern 1: generate_samples(\n                text=config["target_phrase"],
    pattern1 = 'generate_samples(\n                text=config["target_phrase"],'
    replacement1 = 'generate_samples(\n                text=config["target_phrase"],\n                model=config.get("piper_model_path", "./piper-sample-generator/models/en_US-libritts_r-medium.pt"),'

    # Pattern 2: generate_samples(text=config["target_phrase"],
    pattern2 = 'generate_samples(text=config["target_phrase"],'
    replacement2 = 'generate_samples(text=config["target_phrase"],\n                             model=config.get("piper_model_path", "./piper-sample-generator/models/en_US-libritts_r-medium.pt"),'

    # Pattern 3: generate_samples(text=adversarial_texts,
    pattern3 = 'generate_samples(text=adversarial_texts,'
    replacement3 = 'generate_samples(text=adversarial_texts,\n                             model=config.get("piper_model_path", "./piper-sample-generator/models/en_US-libritts_r-medium.pt"),'

    # Apply patches
    content = content.replace(pattern1, replacement1)
    content = content.replace(pattern2, replacement2)
    content = content.replace(pattern3, replacement3)

    # Write back
    with open(train_py, 'w') as f:
        f.write(content)

    print("✅ Patched successfully!")
    print("   Added model parameter to all generate_samples() calls")
    return True

if __name__ == "__main__":
    if patch_train_py():
        sys.exit(0)
    else:
        sys.exit(1)
