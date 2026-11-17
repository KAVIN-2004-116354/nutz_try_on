import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image
from src.preprocessing.segmentation_pipeline import generate_intelligent_replacement_mask

person_path = PROJECT_ROOT / "frontend/assets/sample_person_female.jpg"
person = Image.open(person_path)

grok_res = {
    "mode": "pure_flux",
    "garment_analysis": {"category": "full_body", "garment_type": "evening_gown", "confidence": 1.0},
    "replacement_plan": {
        "target_regions": ["torso", "waist", "full_skirt", "left_arm", "right_arm"],
        "protected_regions": ["face", "hair", "exposed_skin", "hands"]
    }
}

res = generate_intelligent_replacement_mask(person, grok_res["garment_analysis"], grok_res["replacement_plan"])
print("Pure FLUX Mask Size:", res["mask_image"].size)
print("Mask Metrics:", res["metrics"])
print("Pure FLUX mask generation SUCCESS!")
