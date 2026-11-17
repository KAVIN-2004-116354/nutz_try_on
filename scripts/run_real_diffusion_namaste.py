import os
import sys
import time
import torch
import numpy as np
import cv2
from PIL import Image
from pathlib import Path

# Add CatVTON model paths
sys.path.insert(0, "/home/lenovo/try_on/src/models/CatVTON")
from model.cloth_masker import AutoMasker
from model.pipeline import CatVTONPipeline

def main():
    print("=== Starting Real CatVTON Latent Diffusion Inference on Namaste Kurta ===")
    t0_total = time.time()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    base_ckpt = "/home/lenovo/ComfyUI/models/catvton/stable-diffusion-inpainting"
    attn_ckpt = "/home/lenovo/ComfyUI/models/catvton"
    
    person_path = Path("/home/lenovo/try_on/frontend/assets/sample_person_1.jpg")
    cloth_path = Path("/home/lenovo/try_on/datasets/indian_viton_hd/train/cloth/ind_00000.jpg")
    
    assert person_path.exists(), f"Missing {person_path}"
    assert cloth_path.exists(), f"Missing {cloth_path}"
    
    person_img = Image.open(person_path).convert("RGB")
    cloth_img = Image.open(cloth_path).convert("RGB")
    
    # 1. Real AutoMasker (DensePose + SCHP + MediaPipe Phase 2 Knee Hemline)
    print("[Step 1/3] Generating Anatomical Knee-Length Mask via AutoMasker...")
    t0_mask = time.time()
    masker = AutoMasker(
        densepose_path=os.path.join(attn_ckpt, "DensePose"),
        schp_path=os.path.join(attn_ckpt, "SCHP"),
        device=device
    )
    
    # AutoMasker with Phase 2 Kurta silhouette
    mask_res = masker(person_img, mask_type="kurta")
    mask_pil = mask_res["mask"]
    
    out_dir = Path("/home/lenovo/try_on/outputs/phase2")
    out_dir.mkdir(parents=True, exist_ok=True)
    mask_pil.save(out_dir / "real_kurta_mask.png")
    print(f"Mask generated in {time.time() - t0_mask:.2f}s, saved to outputs/phase2/real_kurta_mask.png")
    
    # Free memory from masker before diffusion
    del masker
    torch.cuda.empty_cache()
    
    # 2. Real Latent Diffusion Pipeline
    print("[Step 2/3] Loading Real CatVTON Latent Diffusion Pipeline...")
    pipe = CatVTONPipeline(
        base_ckpt=base_ckpt,
        attn_ckpt=attn_ckpt,
        attn_ckpt_version="mix",
        weight_dtype=torch.float16,
        skip_safety_check=True,
        use_tf32=True,
        device=device
    )
    
    print("[Step 3/3] Running Diffusion Denoising Loop (30 steps, 768x1024, fp16)...")
    t0_diff = time.time()
    
    # Set seed for deterministic reproducibility
    generator = torch.Generator(device=device).manual_seed(42)
    
    results = pipe(
        image=person_img,
        condition_image=cloth_img,
        mask=mask_pil,
        num_inference_steps=30,
        guidance_scale=2.5,
        height=1024,
        width=768,
        generator=generator
    )
    
    tryon_img = results[0]
    diff_time = time.time() - t0_diff
    print(f"Latent Diffusion Inpainting completed in {diff_time:.2f}s!")
    
    tryon_img.save(out_dir / "real_diffusion_tryon_result.png")
    print(f"Saved real tryon result to: {out_dir / 'real_diffusion_tryon_result.png'}")
    
    # 3. Create 4-panel comparison
    target_size = (768, 1024)
    p_resized = person_img.resize(target_size, Image.Resampling.LANCZOS)
    c_resized = cloth_img.resize(target_size, Image.Resampling.LANCZOS)
    
    # Highlight mask overlay on person for panel 3
    p_np = np.array(p_resized).astype(np.float32)
    m_resized = mask_pil.resize(target_size, Image.Resampling.NEAREST)
    m_np = np.array(m_resized).astype(np.float32) / 255.0
    
    # Overlay mask in translucent magenta/crimson
    overlay_np = p_np.copy()
    mask_bool = m_np > 0.5
    overlay_np[mask_bool] = (0.45 * overlay_np[mask_bool] + 0.55 * np.array([220, 20, 100], dtype=np.float32))
    panel3_img = Image.fromarray(overlay_np.astype(np.uint8))
    
    def add_header(img, text, color=(255, 255, 255), bg_color=(20, 30, 45)):
        np_img = np.array(img)
        header = np.zeros((60, np_img.shape[1], 3), dtype=np.uint8)
        header[:] = bg_color
        cv2.putText(header, text, (20, 42), cv2.FONT_HERSHEY_DUPLEX, 1.0, color, 2, cv2.LINE_AA)
        combined = np.vstack([header, np_img])
        return Image.fromarray(combined)

    p1 = add_header(p_resized, "1. Person (Namaste Pose)", bg_color=(25, 35, 55))
    p2 = add_header(c_resized, "2. Indian Garment (Kurta)", bg_color=(45, 25, 45))
    p3 = add_header(panel3_img, "3. Phase 2 Knee Mask (0% Bleed)", bg_color=(55, 25, 40))
    p4 = add_header(tryon_img, "4. Real CatVTON Inpainting", bg_color=(20, 60, 40))

    total_w = target_size[0] * 4
    total_h = target_size[1] + 60
    comp = Image.new("RGB", (total_w, total_h))
    comp.paste(p1, (0, 0))
    comp.paste(p2, (target_size[0], 0))
    comp.paste(p3, (target_size[0] * 2, 0))
    comp.paste(p4, (target_size[0] * 3, 0))

    comp_file = out_dir / "namaste_kurta_tryon_composite.png"
    comp.save(comp_file, quality=95)
    print(f"Updated 4-panel composite saved to: {comp_file}")
    
    # Artifact directory copy
    art_dir = Path("/mnt/c/Users/lenovo/.gemini/antigravity/brain/30005ca1-a36a-41f8-b07d-5866e734c81c")
    if art_dir.exists():
        comp.save(art_dir / "namaste_kurta_tryon_composite.png", quality=95)
        tryon_img.save(art_dir / "real_diffusion_tryon_result.png", quality=95)
        panel3_img.save(art_dir / "real_kurta_mask_overlay.png", quality=95)
        print(f"Copied composite and result to artifacts directory {art_dir}")

    print(f"=== ALL DONE in {time.time() - t0_total:.2f}s! ===")

if __name__ == '__main__':
    main()
