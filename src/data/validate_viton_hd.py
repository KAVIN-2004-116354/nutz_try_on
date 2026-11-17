import os
from pathlib import Path

print("=== VITON-HD Dataset Validation Suite ===")
base_dir = Path("datasets/viton_hd")
subdirs = ["train", "test"]

for split in subdirs:
    split_path = base_dir / split
    print(f"\nChecking [{split.upper()}] split at: {split_path}")
    if not split_path.exists():
        print(f"  [WARNING] {split_path} does not exist yet.")
        continue
    
    expected_folders = ["image", "cloth", "cloth-mask", "agnostic-mask", "image-parse-v3"]
    for folder in expected_folders:
        f_path = split_path / folder
        exists = f_path.exists() and any(f_path.iterdir()) if f_path.exists() else False
        status = "[FOUND]" if exists else "[EMPTY/MISSING]"
        print(f"  - {folder}: {status}")

print("\nValidation script template ready.")
