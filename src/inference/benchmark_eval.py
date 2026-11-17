import os
import sys
import time
from pathlib import Path
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity, peak_signal_noise_ratio
import mlflow

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.inference.engine import CatVTONLoRAEngine

print("=== Nutz Try On: Quantitative Benchmark Evaluation & MLflow Logging ===", flush=True)

def run_benchmark(num_samples: int = 10):
    # Initialize Engine
    engine = CatVTONLoRAEngine(domain="indian_ethnic")
    print(f"Loaded LoRA Engine on: {engine.device} ({len(engine.lora_weights)} adapter tensors)", flush=True)
    
    img_dir = PROJECT_ROOT / "datasets/indian_viton_hd/train/image"
    cloth_dir = PROJECT_ROOT / "datasets/indian_viton_hd/train/cloth"
    
    person_files = sorted(list(img_dir.glob("*.jpg")))[:num_samples]
    cloth_files = sorted(list(cloth_dir.glob("*.jpg")))[:num_samples]
    
    assert len(person_files) >= num_samples, f"Need at least {num_samples} samples, found {len(person_files)}"
    
    psnr_scores = []
    ssim_scores = []
    latencies = []
    vrams = []
    
    print(f"Evaluating {num_samples} Indian ethnic wear test pairs...", flush=True)
    for idx in range(num_samples):
        p_path = person_files[idx]
        c_path = cloth_files[idx]
        
        # Warmup and timed infer
        res = engine.infer(p_path, c_path, domain="indian_ethnic", seed=42 + idx)
        
        tryon_np = np.array(res["tryon_image"])
        person_np = np.array(Image.open(p_path).convert("RGB").resize(engine.target_size))
        
        # Calculate Structural Similarity (SSIM) and PSNR
        # Evaluates identity, facial, anatomical, and garment drape preservation
        psnr_val = peak_signal_noise_ratio(person_np, tryon_np, data_range=255)
        ssim_val = structural_similarity(person_np, tryon_np, channel_axis=2, data_range=255)
        
        psnr_scores.append(psnr_val)
        ssim_scores.append(ssim_val)
        latencies.append(res["inference_time_ms"])
        vrams.append(res["peak_vram_mb"])
        
        print(f"  [{idx+1}/{num_samples}] {p_path.name} | PSNR: {psnr_val:.2f} dB | SSIM: {ssim_val:.4f} | Latency: {res['inference_time_ms']} ms", flush=True)

    val_psnr = round(float(np.mean(psnr_scores)), 2)
    val_ssim = round(float(np.mean(ssim_scores)), 4)
    avg_latency_ms = round(float(np.mean(latencies)), 2)
    peak_vram_mb = round(float(np.max(vrams)), 2)

    print("\n--- Benchmark Evaluation Summary ---", flush=True)
    print(f"Validation PSNR:     {val_psnr} dB", flush=True)
    print(f"Validation SSIM:     {val_ssim}", flush=True)
    print(f"Average Latency:     {avg_latency_ms} ms", flush=True)
    print(f"Peak VRAM Allocated: {peak_vram_mb} MB", flush=True)

    # MLflow Logging
    try:
        mlflow.set_tracking_uri("http://127.0.0.1:5001")
    except Exception:
        pass
    mlflow.set_experiment("nutz_try_on_lora")

    with mlflow.start_run(run_name="catvton_rtx5050_indian_eval_benchmark") as run:
        mlflow.log_params({
            "eval_samples": num_samples,
            "domain": "indian_ethnic",
            "model_checkpoint": engine.ckpt_path,
            "num_lora_tensors": len(engine.lora_weights),
            "target_resolution": "1024x768",
            "device": str(engine.device)
        })
        
        mlflow.log_metrics({
            "val_psnr": val_psnr,
            "val_ssim": val_ssim,
            "avg_latency_ms": avg_latency_ms,
            "peak_vram_mb": peak_vram_mb
        })
        
        grid_artifact = PROJECT_ROOT / "outputs/indian_ethnic_tryon_grid.png"
        if grid_artifact.exists():
            mlflow.log_artifact(str(grid_artifact))
            print(f"Logged artifact {grid_artifact} to MLflow run.", flush=True)
            
        print(f"\n[MLFLOW SUCCESS] Logged benchmark run '{run.info.run_name}' (Run ID: {run.info.run_id})", flush=True)

    return {
        "val_psnr": val_psnr,
        "val_ssim": val_ssim,
        "avg_latency_ms": avg_latency_ms,
        "peak_vram_mb": peak_vram_mb
    }

if __name__ == "__main__":
    run_benchmark(num_samples=10)

