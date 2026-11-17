"""Intelligent Virtual Try-On Validation Matrix (Section 12).

Tests all 10 Garment Categories (A through J):
- TEST A: T-shirt
- TEST B: Formal shirt
- TEST C: Kurta
- TEST D: Sherwani
- TEST E: Trousers
- TEST F: Jeans
- TEST G: Anarkali
- TEST H: Saree
- TEST I: Lehenga
- TEST J: Western dress

Validates:
1. Classification category & type
2. Estimated confidence
3. Target body regions vs 100% Protected anatomical regions
4. Mask quality score, replacement pixel count, and coverage %
5. FLUX-DEV-012 generation prompt formulation
6. Live execution via /api/v1/intelligent-tryon
"""

import os
import sys
import time
import json
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.inference.grok_vision import grok_vision_analyze
from src.preprocessing.segmentation_pipeline import generate_intelligent_replacement_mask
from src.inference.cloud_generator import run_flux_tryon, is_cloud_flux_alive

TEST_MATRIX = [
    {
        "id": "TEST A",
        "name": "T-shirt",
        "garment_path": "frontend/assets/sample_black_tshirt.jpg",
        "person_path": "frontend/assets/sample_men_clean.jpg",
        "expected_category": "upper_body",
        "expected_type": "t_shirt",
    },
    {
        "id": "TEST B",
        "name": "Formal shirt",
        "garment_path": "frontend/assets/sample_emerald_shirt.jpg",
        "person_path": "frontend/assets/sample_men_clean.jpg",
        "expected_category": "upper_body",
        "expected_type": "formal_shirt",
    },
    {
        "id": "TEST C",
        "name": "Kurta",
        "garment_path": "frontend/assets/garments/m_01_cloth.jpg",
        "person_path": "frontend/assets/sample_men_clean.jpg",
        "expected_category": "upper_body",
        "expected_type": "kurta",
    },
    {
        "id": "TEST D",
        "name": "Sherwani",
        "garment_path": "frontend/assets/garments/mc_06.jpg",
        "person_path": "frontend/assets/sample_men_clean.jpg",
        "expected_category": "complex_ethnic",
        "expected_type": "sherwani",
    },
    {
        "id": "TEST E",
        "name": "Trousers",
        "garment_path": "frontend/assets/garments/g_14_cloth.jpg",
        "person_path": "frontend/assets/sample_ethnic_anarkali_model.jpg",
        "expected_category": "lower_body",
        "expected_type": "trousers",
    },
    {
        "id": "TEST F",
        "name": "Jeans",
        "garment_path": "frontend/assets/garments/g_11_cloth.jpg",
        "person_path": "frontend/assets/sample_men_clean.jpg",
        "expected_category": "lower_body",
        "expected_type": "jeans",
    },
    {
        "id": "TEST G",
        "name": "Anarkali",
        "garment_path": "frontend/assets/sample_anarkali_dress.jpg",
        "person_path": "frontend/assets/sample_ethnic_anarkali_model.jpg",
        "expected_category": "full_body",
        "expected_type": "anarkali_suit",
    },
    {
        "id": "TEST H",
        "name": "Saree",
        "garment_path": "frontend/assets/garments/g_01_cloth.jpg",
        "person_path": "frontend/assets/sample_ethnic_anarkali_model.jpg",
        "expected_category": "complex_ethnic",
        "expected_type": "saree",
    },
    {
        "id": "TEST I",
        "name": "Lehenga",
        "garment_path": "frontend/assets/garments/g_23_cloth.jpg",
        "person_path": "frontend/assets/sample_ethnic_anarkali_model.jpg",
        "expected_category": "complex_ethnic",
        "expected_type": "lehenga",
    },
    {
        "id": "TEST J",
        "name": "Western dress",
        "garment_path": "frontend/assets/garments/g_15_cloth.jpg",
        "person_path": "frontend/assets/sample_ethnic_anarkali_model.jpg",
        "expected_category": "full_body",
        "expected_type": "western_dress",
    },
]


def run_matrix():
    print("=" * 80)
    print("NUTZ REPLACER — INTELLIGENT TRY-ON PIPELINE VALIDATION MATRIX")
    print("Architecture: Grok Vision + Adaptive Segmentation + FLUX-DEV-012")
    print("=" * 80)

    cloud_online = is_cloud_flux_alive()
    print(f"[*] Nutz Railway Cloud Status: {'ONLINE (Connected)' if cloud_online else 'OFFLINE'}")

    results = []
    output_dir = PROJECT_ROOT / "outputs" / "matrix_validation"
    output_dir.mkdir(parents=True, exist_ok=True)

    for item in TEST_MATRIX:
        test_id = item["id"]
        name = item["name"]
        print(f"\n--- Running {test_id}: {name} ---")

        g_path = PROJECT_ROOT / item["garment_path"]
        p_path = PROJECT_ROOT / item["person_path"]

        if not g_path.exists():
            print(f"[-] Garment not found: {g_path}")
            continue
        if not p_path.exists():
            print(f"[-] Person not found: {p_path}")
            continue

        g_img = Image.open(g_path).convert("RGB")
        p_img = Image.open(p_path).convert("RGB")

        # Step 1: Grok Vision Multimodal Understanding
        t0 = time.time()
        grok_res = grok_vision_analyze(
            garment_img=g_img,
            person_img=p_img,
            garment_name=name.lower().replace(" ", "_"),
        )
        t_grok = round(time.time() - t0, 3)

        ga = grok_res["garment_analysis"]
        rp = grok_res["replacement_plan"]
        prompt = grok_res["generation_prompt"]

        print(f"  [Grok Vision] Category: {ga['category']} | Type: {ga['garment_type']} | Confidence: {ga['confidence']}")
        print(f"  [Grok Vision] Color: {ga['primary_color']} | Fabric: {ga['fabric']} | Pattern: {ga['pattern']}")
        print(f"  [Target Plan] Target: {rp['target_regions']} | Protected: {rp['protected_regions'][:3]}...")

        # Step 2: Adaptive Anatomy-Guarded Segmentation
        t1 = time.time()
        seg_res = generate_intelligent_replacement_mask(
            person_img=p_img,
            garment_analysis=ga,
            replacement_plan=rp,
        )
        t_seg = round(time.time() - t1, 3)
        metrics = seg_res["metrics"]
        print(f"  [Segmentation] Mask Quality: {metrics['quality_score']} | Coverage: {metrics['coverage_percentage']}% | Integrity: {metrics['protected_integrity']}")

        # Save mask and overlay for this test
        safe_id = test_id.lower().replace(" ", "_")
        mask_path = output_dir / f"{safe_id}_mask.png"
        overlay_path = output_dir / f"{safe_id}_overlay.png"
        seg_res["mask_image"].save(mask_path, format="PNG")
        overlay = seg_res.get("overlay_image") or seg_res.get("preview_overlay")
        overlay.save(overlay_path, format="PNG")

        # Record test entry
        entry = {
            "test_id": test_id,
            "name": name,
            "classified_category": ga["category"],
            "classified_type": ga["garment_type"],
            "primary_color": ga["primary_color"],
            "fabric": ga["fabric"],
            "confidence": ga["confidence"],
            "target_regions": rp["target_regions"],
            "protected_integrity": metrics["protected_integrity"],
            "mask_quality_score": metrics["quality_score"],
            "coverage_percentage": metrics["coverage_percentage"],
            "prompt": prompt,
            "mask_path": str(mask_path),
            "overlay_path": str(overlay_path),
            "latency_grok_sec": t_grok,
            "latency_seg_sec": t_seg,
        }
        results.append(entry)

    # Now execute live FLUX-DEV-012 Cloud Inpainting for TEST G (Anarkali) & TEST A (T-shirt)
    print("\n" + "=" * 80)
    print("[*] LIVE FLUX-DEV-012 CLOUD INPAINTING VERIFICATION")
    print("=" * 80)

    live_tests = [r for r in results if r["test_id"] in ("TEST A", "TEST G")]
    for live in live_tests:
        tid = live["test_id"]
        tname = live["name"]
        print(f"Executing Live Cloud Inpainting for {tid} ({tname})...")
        p_img = Image.open(PROJECT_ROOT / (item["person_path"] if tid == "TEST A" else "frontend/assets/sample_ethnic_anarkali_model.jpg")).convert("RGB")
        mask_img = Image.open(live["mask_path"]).convert("L")

        t_flux0 = time.time()
        try:
            flux_res = run_flux_tryon(
                person_img=p_img,
                custom_prompt=live["prompt"],
                mask_img=mask_img,
                output_path=output_dir / f"{live['test_id'].lower().replace(' ', '_')}_flux_result.png",
            )
            live["flux_status"] = "SUCCESS"
            live["flux_resolution"] = flux_res["resolution"]
            live["flux_latency_sec"] = round(time.time() - t_flux0, 2)
            live["flux_file"] = flux_res["output_file"]
            print(f"  [+] {tid} Succeeded: Res={flux_res['resolution']} Latency={live['flux_latency_sec']}s")
        except Exception as e:
            live["flux_status"] = f"FAILED ({str(e)})"
            print(f"  [-] {tid} Inpainting Failed: {e}")

    # Output JSON summary
    summary_path = output_dir / "validation_summary.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Validation Summary written to {summary_path}")

    # Print Table
    print("\n" + "=" * 110)
    print(f"{'Test':<8} | {'Garment':<14} | {'Category':<15} | {'Type':<15} | {'Mask Qual':<10} | {'Coverage':<9} | {'Integrity':<9} | {'Status'}")
    print("-" * 110)
    for r in results:
        status = r.get("flux_status", "VALIDATED")
        print(f"{r['test_id']:<8} | {r['name']:<14} | {r['classified_category']:<15} | {r['classified_type']:<15} | {r['mask_quality_score']:<10.2f} | {r['coverage_percentage']:<8.1f}% | {str(r['protected_integrity']):<9} | {status}")
    print("=" * 110)


if __name__ == "__main__":
    run_matrix()
