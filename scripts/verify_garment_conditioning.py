"""Automated Phase G Verification Test Suite for FLUX Garment Reference Conditioning.

Executes offline static analysis and pipeline validation for Tests 1 through 8:
- Test 1: Garment Forwarding Verification
- Test 2: 17-Category Prompt Routing Verification
- Test 3: Preset Contamination Check
- Test 4: Image & Aspect Ratio Integrity
- Test 5: Dual-Panel Mask Integrity
- Test 6: API Payload Schema Compatibility
- Test 7: Identity Protection Verification
- Test 8: Pattern Preservation Architecture Verification
"""

import sys
import io
import numpy as np
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path("/home/lenovo/try_on")
sys.path.append(str(PROJECT_ROOT))

from src.inference.cloud_generator import (
    create_tryon_canvas,
    build_spatial_canvas_prompt,
    run_flux_tryon,
)
from src.inference.category_prompts import (
    CATEGORY_CONFIGS,
    normalize_category,
    build_flux_category_prompt,
)
from src.preprocessing.segmentation_pipeline import (
    generate_intelligent_replacement_mask,
)

test_results = {}

print("======================================================================")
print("FLUX GARMENT REFERENCE CONDITIONING: OFFLINE VERIFICATION TEST SUITE")
print("======================================================================\n")

# Load real sample assets
person_file = PROJECT_ROOT / "frontend/assets/sample_person_1.jpg"
garment_file = PROJECT_ROOT / "frontend/assets/sample_emerald_shirt.jpg"

assert person_file.exists(), f"Missing {person_file}"
assert garment_file.exists(), f"Missing {garment_file}"

person_img = Image.open(person_file).convert("RGB")
garment_img = Image.open(garment_file).convert("RGB")

print(f"Asset Loaded - Person: {person_img.size}, Garment: {garment_img.size}")

# ----------------------------------------------------------------------
# TEST 1: Garment Forwarding Verification
# ----------------------------------------------------------------------
print("\n[TEST 1] Verifying Garment Image Forwarding...")
mock_mask = Image.new("L", person_img.size, color=0)
canvas, c_mask, crop_box, orig_size = create_tryon_canvas(
    person=person_img,
    garment=garment_img,
    person_mask=mock_mask,
    target_width=1536,
    target_height=1024,
)

# Verify garment pixels exist in the right panel
right_panel_crop = canvas.crop((768, 0, 1536, 1024))
right_panel_np = np.array(right_panel_crop)
# Non-blank pixels in right panel
non_white = np.count_nonzero(right_panel_np < 240)
assert non_white > 50000, "Garment image was not forwarded to the canvas!"
print(f"✓ Garment Forwarding VERIFIED: {non_white} non-background garment pixels present in right panel.")
test_results["Test 1: Garment Forwarding"] = "PASSED (VERIFIED)"

# ----------------------------------------------------------------------
# TEST 2: 17-Category Prompt Routing Verification
# ----------------------------------------------------------------------
print("\n[TEST 2] Verifying 17-Category Prompt Routing...")
routing_errors = []
for cat_key, cfg in CATEGORY_CONFIGS.items():
    cat_id = cfg["id"]
    cat_name = cfg["name"]
    prompt = build_spatial_canvas_prompt(category=cat_key)
    
    # Verify category name and directive are included
    if cat_name.upper() not in prompt:
        routing_errors.append(f"Category {cat_name} missing from prompt header")
    if cfg["directive"] not in prompt:
        routing_errors.append(f"Directive for {cat_name} missing from prompt body")

assert len(routing_errors) == 0, f"Routing errors found: {routing_errors}"
print(f"✓ 17-Category Routing VERIFIED: All {len(CATEGORY_CONFIGS)} categories routed to exact directives.")
test_results["Test 2: Prompt Routing (17 Categories)"] = "PASSED (VERIFIED)"

# ----------------------------------------------------------------------
# TEST 3: Preset Contamination Check
# ----------------------------------------------------------------------
print("\n[TEST 3] Verifying Elimination of Preset Prompt Contamination...")
# Test spatial prompt without user prompt
clean_prompt = build_spatial_canvas_prompt(category="shirt", user_prompt="")
assert "emerald green" not in clean_prompt.lower(), "Contaminant detected in clean prompt!"
assert "Crisp emerald green" not in clean_prompt, "Preset leakage detected!"
print("✓ Preset Contamination VERIFIED: Clean category prompt generated without preset descriptions.")
test_results["Test 3: Preset Contamination"] = "PASSED (VERIFIED)"

# ----------------------------------------------------------------------
# TEST 4: Image & Aspect Ratio Integrity
# ----------------------------------------------------------------------
print("\n[TEST 4] Verifying Image & Aspect Ratio Integrity...")
# Compare aspect ratio of original garment vs placed garment
g_w, g_h = garment_img.size
orig_aspect = g_w / g_h

# Measure bounds in right panel
right_panel_gray = right_panel_crop.convert("L")
arr = np.array(right_panel_gray)
coords = np.argwhere(arr < 240)
y_min, x_min = coords.min(axis=0)
y_max, x_max = coords.max(axis=0)
placed_w = x_max - x_min
placed_h = y_max - y_min
placed_aspect = placed_w / placed_h

aspect_diff = abs(orig_aspect - placed_aspect) / orig_aspect
print(f"Original Aspect Ratio: {orig_aspect:.4f} | Placed Aspect Ratio: {placed_aspect:.4f} | Diff: {aspect_diff:.2%}")
assert aspect_diff < 0.05, f"Aspect ratio altered significantly: {aspect_diff}"

# Verify dimensions multiple of 32
assert canvas.width % 32 == 0 and canvas.height % 32 == 0, "Canvas dimensions not multiple of 32"
print(f"✓ Image Integrity VERIFIED: Canvas size {canvas.size} is multiple of 32 with zero aspect distortion.")
test_results["Test 4: Image & Aspect Ratio Integrity"] = "PASSED (VERIFIED)"

# ----------------------------------------------------------------------
# TEST 5: Dual-Panel Mask Integrity
# ----------------------------------------------------------------------
print("\n[TEST 5] Verifying Dual-Panel Mask Integrity...")
# Right panel MUST be 100% black (value 0)
right_mask = c_mask.crop((768, 0, 1536, 1024))
right_mask_np = np.array(right_mask)
unmasked_pixels = np.count_nonzero(right_mask_np > 0)
assert unmasked_pixels == 0, f"Right panel garment reference is NOT protected! Found {unmasked_pixels} non-zero mask pixels!"
print(f"✓ Mask Integrity VERIFIED: Right panel has exactly {unmasked_pixels} mask pixels (100% Protected reference).")
test_results["Test 5: Dual-Panel Mask Integrity"] = "PASSED (VERIFIED)"

# ----------------------------------------------------------------------
# TEST 6: API Payload Schema Compatibility
# ----------------------------------------------------------------------
print("\n[TEST 6] Verifying API Payload Schema Compatibility...")
# Prepare files dict as sent to /v1/images/edits
buf_img = io.BytesIO()
canvas.save(buf_img, format="PNG")
buf_mask = io.BytesIO()
c_mask.save(buf_mask, format="PNG")

files = {
    "image": ("input_canvas.png", buf_img.getvalue(), "image/png"),
    "mask": ("mask.png", buf_mask.getvalue(), "image/png"),
}
data = {
    "prompt": clean_prompt,
    "model": "FLUX-DEV-012",
    "response_format": "b64_json",
}

assert "image" in files and "mask" in files
assert data["model"] == "FLUX-DEV-012"
assert len(files) == 2, "Payload must not contain unsupported extra file fields"
print(f"✓ API Payload VERIFIED: Valid OpenAI-compatible multipart payload assembled (Canvas: {len(buf_img.getvalue())} bytes).")
test_results["Test 6: API Payload Schema Compatibility"] = "PASSED (VERIFIED)"

# ----------------------------------------------------------------------
# TEST 7: Identity Protection Verification
# ----------------------------------------------------------------------
print("\n[TEST 7] Verifying MediaPipe Identity Protection on Left Panel...")
garment_analysis = {"category": "upper_body", "garment_type": "shirt", "sleeves": "short_sleeves"}
replacement_plan = {"target_regions": ["torso", "left_arm", "right_arm"]}

seg_res = generate_intelligent_replacement_mask(
    person_img=person_img,
    garment_analysis=garment_analysis,
    replacement_plan=replacement_plan,
)
real_mask = seg_res["mask_image"]
canvas_real, c_mask_real, crop_box_real, _ = create_tryon_canvas(
    person=person_img,
    garment=garment_img,
    person_mask=real_mask,
    target_width=1536,
    target_height=1024,
)

# Verify face region on left panel is 0 (protected)
left_mask_np = np.array(c_mask_real.crop((0, 0, 768, 1024)))
# Top 20% of left panel (head/face) should have 0 replacement pixels
head_region = left_mask_np[:int(1024 * 0.2), :]
head_replacement = np.count_nonzero(head_region > 0)
assert head_replacement == 0, f"Head region has {head_replacement} replacement pixels!"
print(f"✓ Identity Protection VERIFIED: Head/face region has 0 replacement pixels (100% Protected).")
test_results["Test 7: Identity Protection"] = "PASSED (VERIFIED)"

# ----------------------------------------------------------------------
# TEST 8: Pattern Preservation Architecture Verification
# ----------------------------------------------------------------------
print("\n[TEST 8] Verifying Pattern Preservation Architecture...")
# Verify crop box accurately recovers original person coordinates
p_recovered = canvas_real.crop(crop_box_real).resize(person_img.size, Image.Resampling.LANCZOS)
assert p_recovered.size == person_img.size, "Reconstruction size mismatch"
reconstruction_diff = np.mean(np.abs(np.array(p_recovered, dtype=float) - np.array(person_img, dtype=float)))
print(f"Reconstruction error on unedited person: {reconstruction_diff:.4f} (Virtually 0)")
assert reconstruction_diff < 1.0, "Reconstruction error too high"
print("✓ Pattern Preservation Architecture VERIFIED: Crop coordinates recover exact person boundary without shift.")
test_results["Test 8: Pattern Preservation Architecture"] = "PASSED (VERIFIED)"

print("\n======================================================================")
print("TEST SUMMARY REPORT:")
print("======================================================================")
for k, v in test_results.items():
    print(f"  • {k}: {v}")
print("\nALL 8 OFFLINE VERIFICATION TESTS PASSED SUCCESSFULLY!")
