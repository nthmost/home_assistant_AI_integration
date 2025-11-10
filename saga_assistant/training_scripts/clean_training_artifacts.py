#!/usr/bin/env python3
"""
Clean up partial training artifacts to allow fresh restart
"""

import shutil
from pathlib import Path
import argparse

def clean_model_artifacts(model_name):
    """Remove generated features and allow augmentation to rerun"""

    model_dir = Path(f"my_custom_model/{model_name}")

    if not model_dir.exists():
        print(f"✅ No artifacts found for model: {model_name}")
        return True

    print(f"🧹 Cleaning artifacts for model: {model_name}")
    print(f"   Directory: {model_dir}")
    print()

    # Files to remove (features that may be incomplete)
    feature_files = [
        "positive_features_train.npy",
        "positive_features_test.npy",
        "negative_features_train.npy",
        "negative_features_test.npy",
    ]

    removed_count = 0

    for feature_file in feature_files:
        file_path = model_dir / feature_file
        if file_path.exists():
            print(f"   🗑️  Removing: {feature_file}")
            file_path.unlink()
            removed_count += 1
        else:
            print(f"   ⏭️  Not found: {feature_file}")

    print()

    if removed_count > 0:
        print(f"✅ Removed {removed_count} feature files")
        print("   Augmentation will regenerate these on next run")
    else:
        print("✅ No feature files to remove")

    return True


def clean_all_clips(model_name):
    """Remove ALL generated clips and features (full reset)"""

    model_dir = Path(f"my_custom_model/{model_name}")

    if not model_dir.exists():
        print(f"✅ No artifacts found for model: {model_name}")
        return True

    print(f"⚠️  FULL CLEAN: Removing all clips and features for: {model_name}")
    print(f"   This will delete the entire directory: {model_dir}")

    response = input("\n   Are you sure? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cancelled")
        return False

    print(f"\n   🗑️  Removing: {model_dir}")
    shutil.rmtree(model_dir)

    print("✅ Full clean complete")
    print("   All clips and features will be regenerated on next run")

    return True


def main():
    parser = argparse.ArgumentParser(description="Clean training artifacts")
    parser.add_argument("model_name", help="Model name (e.g., 'hey_saga')")
    parser.add_argument("--full", action="store_true",
                       help="Remove ALL clips and features (full reset)")

    args = parser.parse_args()

    if args.full:
        return 0 if clean_all_clips(args.model_name) else 1
    else:
        return 0 if clean_model_artifacts(args.model_name) else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
