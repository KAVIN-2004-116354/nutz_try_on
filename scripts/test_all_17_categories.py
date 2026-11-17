import sys
from pathlib import Path

PROJECT_ROOT = Path("/home/lenovo/try_on")
sys.path.insert(0, str(PROJECT_ROOT))

from src.inference.category_prompts import (
    CATEGORY_CONFIGS,
    normalize_category,
    get_category_config,
    build_flux_category_prompt,
)
from src.preprocessing.segmentation_pipeline import generate_intelligent_replacement_mask
from PIL import Image

person_path = PROJECT_ROOT / "frontend/assets/sample_person_female.jpg"
person_img = Image.open(person_path)

print(f"Total Canonical Categories: {len(CATEGORY_CONFIGS)}")
assert len(CATEGORY_CONFIGS) == 17, "Must have exactly 17 categories"

all_passed = True
for key, cfg in CATEGORY_CONFIGS.items():
    cat_id = cfg["id"]
    name = cfg["name"]
    macro = cfg["macro_category"]

    # 1. Test prompt generation
    prompt = build_flux_category_prompt(key, garment_attributes={"primary_color": "royal blue", "fabric": "silk"})
    assert "IDENTITY & BODY PRESERVATION" in prompt, f"Missing identity rules in {name}"
    assert "GARMENT DESIGN FIDELITY" in prompt, f"Missing reference rules in {name}"
    assert f"CATEGORY {cat_id}:" in prompt, f"Missing category header in {name}"
    assert "PRIORITY ORDER:" in prompt, f"Missing global instructions in {name}"

    # 2. Test segmentation mask generation
    seg_res = generate_intelligent_replacement_mask(
        person_img=person_img,
        garment_analysis={"category": macro, "garment_type": key},
        replacement_plan={"target_regions": [macro]}
    )
    assert seg_res["is_valid"], f"Mask invalid for {name}"
    cov = seg_res["metrics"]["coverage_percentage"]
    print(f"[{cat_id:02d}/17] {name:<26} -> Macro: {macro:<14} | Coverage: {cov:>4.1f}% | Mask: OK")

print("\nSUCCESS: All 17 categories validated against Universal Rules and MediaPipe Anatomy Guard!")
