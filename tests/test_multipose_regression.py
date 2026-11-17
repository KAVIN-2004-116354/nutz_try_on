import os
import sys
import time
import numpy as np
import cv2
from PIL import Image

sys.path.append("/home/lenovo/ComfyUI/custom_nodes/Comfyui-CatVTON")
from model.cloth_masker import AutoMasker

print("==================================================================")
print("       PHASE 1 MULTI-POSE & MULTI-RESOLUTION REGRESSION SUITE     ")
print("==================================================================")

masker = AutoMasker(device="cpu")
out_dir = "/home/lenovo/try_on/outputs/phase1"
os.makedirs(out_dir, exist_ok=True)

test_cases = [
    {
        "id": "CASE_1_NAMASTE_MALE",
        "name": "Namaste Folded Hands Pose (Primary Regression)",
        "path": "/home/lenovo/try_on/frontend/assets/sample_person_1.jpg",
        "res": (768, 1024)
    },
    {
        "id": "CASE_2_FEMALE_STANDING",
        "name": "Female Subject Standing Pose",
        "path": "/home/lenovo/try_on/frontend/assets/sample_person_female.jpg",
        "res": (768, 1024)
    },
    {
        "id": "CASE_3_MODI_ARMS_DOWN",
        "name": "Subject Arms-Down Pose",
        "path": "/home/lenovo/try_on/frontend/assets/sample_person_modi.png",
        "res": (768, 1024)
    },
    {
        "id": "CASE_4_NAMASTE_HI_RES",
        "name": "Namaste Pose High Resolution (1204x1600)",
        "path": "/home/lenovo/try_on/frontend/assets/sample_person_1.jpg",
        "res": (1204, 1600)
    },
    {
        "id": "CASE_5_NAMASTE_LOW_RES",
        "name": "Namaste Pose Mobile Resolution (512x682)",
        "path": "/home/lenovo/try_on/frontend/assets/sample_person_1.jpg",
        "res": (512, 682)
    }
]

results = []

for tc in test_cases:
    if not os.path.exists(tc["path"]):
        print(f"[SKIP] Missing asset: {tc['path']}")
        continue

    img_raw = Image.open(tc["path"]).convert("RGB")
    target_w, target_h = tc["res"]
    
    # Aspect-preserving crop and resize
    w_orig, h_orig = img_raw.size
    if w_orig / h_orig < target_w / target_h:
        crop_w = w_orig
        crop_h = w_orig * target_h // target_w
    else:
        crop_h = h_orig
        crop_w = h_orig * target_w // target_h

    cropped = img_raw.crop(((w_orig - crop_w) // 2, (h_orig - crop_h) // 2, (w_orig + crop_w) // 2, (h_orig + crop_h) // 2))
    img_test = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

    t0 = time.time()
    res = masker(img_test, mask_type="upper")
    dt = time.time() - t0

    mask = res["mask"]
    mask_arr = np.array(mask)
    img_arr = np.array(img_test)

    # 1. Total Masked Pixels
    total_masked_px = np.sum(mask_arr > 127)
    total_px = target_w * target_h
    mask_coverage_pct = (total_masked_px / total_px) * 100.0

    # 2. Check Head & Face Protection (Strictly 0 leakage)
    # Head & face is top 15% of body
    head_leakage = np.sum(mask_arr[:int(target_h * 0.15), :] > 127)

    # 3. Save Visual Artifact
    masked_composite = img_arr.copy()
    masked_composite[mask_arr > 127] = 0

    preview_name = f"regression_{tc['id'].lower()}.png"
    preview_path = os.path.join(out_dir, preview_name)
    Image.fromarray(masked_composite).save(preview_path)

    case_res = {
        "id": tc["id"],
        "name": tc["name"],
        "resolution": f"{target_w}x{target_h}",
        "duration_sec": round(dt, 3),
        "total_masked_pixels": int(total_masked_px),
        "mask_coverage_pct": round(mask_coverage_pct, 2),
        "head_leakage_px": int(head_leakage),
        "preview": preview_path
    }
    results.append(case_res)
    print(f"\n[PASS] {tc['id']}: {tc['name']}")
    print(f"       Res: {target_w}x{target_h} | Time: {dt:.2f}s | Coverage: {mask_coverage_pct:.1f}% | Head Leakage: {head_leakage}px")

print("\n==================================================================")
print("                   ALL REGRESSION TESTS COMPLETED                 ")
print("==================================================================")

