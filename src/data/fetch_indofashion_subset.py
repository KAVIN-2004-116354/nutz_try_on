import os
import shutil
from pathlib import Path

print("=== IndoFashion / Kaggle Curated Subset Extractor ===")
raw_persons = Path("datasets/indian_raw/persons")
raw_persons.mkdir(parents=True, exist_ok=True)

# If you downloaded a zip/folder from Kaggle or Hugging Face into datasets/indian_raw/archive:
archive_dir = Path("datasets/indian_raw/archive")
if archive_dir.exists():
    all_imgs = list(archive_dir.glob("**/*.jpg")) + list(archive_dir.glob("**/*.png"))
    print(f"Found {len(all_imgs)} images in archive. Sampling 500 high-res ethnic wear photos...")
    for idx, img_path in enumerate(all_imgs[:500]):
        shutil.copy2(img_path, raw_persons / f"indofashion_{idx:04d}.jpg")
    print("Copied 500 images into datasets/indian_raw/persons/! Now re-run build_indian_curated.py")
else:
    print("Tip: To bulk-import 500 Kaggle IndoFashion images, place your archive in 'datasets/indian_raw/archive'")
    print("Or run: kaggle datasets download -d validmodel/indo-fashion-dataset -p datasets/indian_raw/")
