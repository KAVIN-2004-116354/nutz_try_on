import os
import sys
import torch
from pathlib import Path
from PIL import Image

sys.path.append("/home/lenovo/ComfyUI/custom_nodes/Comfyui-CatVTON")
from model.cloth_masker import AutoMasker
from model.pipeline import CatVTONPipeline

base_ckpt = "/home/lenovo/ComfyUI/models/catvton/stable-diffusion-inpainting"
attn_ckpt = "/home/lenovo/ComfyUI/models/catvton"

print("Checking paths:")
print("Base ckpt exists:", os.path.exists(base_ckpt))
print("Attn ckpt exists:", os.path.exists(attn_ckpt))
print("CUDA available:", torch.cuda.is_available())

print("\n--- 1. Testing AutoMasker with Phase 2 Kurta ---")
masker = AutoMasker(
    densepose_path=os.path.join(attn_ckpt, "DensePose"),
    schp_path=os.path.join(attn_ckpt, "SCHP"),
    device="cuda"
)
person_img = Image.open("/home/lenovo/try_on/frontend/assets/sample_person_1.jpg")
mask_res = masker(person_img, mask_type="kurta")
mask_pil = mask_res["mask"]
mask_pil.save("/home/lenovo/try_on/outputs/phase2/real_automasker_kurta.png")
print("AutoMasker Kurta mask saved to outputs/phase2/real_automasker_kurta.png!")

print("\n--- 2. Loading Real CatVTON Diffusion Pipeline ---")
pipe = CatVTONPipeline(
    base_ckpt=base_ckpt,
    attn_ckpt=attn_ckpt,
    attn_ckpt_version="mix",
    weight_dtype=torch.float16,
    skip_safety_check=True,
    use_tf32=True,
    device="cuda"
)
print("Real CatVTON Diffusion Pipeline loaded on CUDA!")
