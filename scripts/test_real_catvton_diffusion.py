import os
import sys
import time
import torch
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path("/home/lenovo/try_on")
sys.path.append(str(PROJECT_ROOT))
sys.path.append("/home/lenovo/ComfyUI/custom_nodes/Comfyui-CatVTON")

from model.cloth_masker import AutoMasker
from model.pipeline import CatVTONPipeline

base_ckpt = "/home/lenovo/ComfyUI/models/catvton/stable-diffusion-inpainting"
attn_ckpt = "/home/lenovo/ComfyUI/models/catvton"

person_path = PROJECT_ROOT / "frontend/assets/sample_person_1.jpg"
garment_path = PROJECT_ROOT / "frontend/assets/sample_emerald_shirt.jpg"

print(f"Loading inputs: {person_path.name}, {garment_path.name}")
person_img = Image.open(person_path).convert("RGB")
garment_img = Image.open(garment_path).convert("RGB")

print("1. Creating AutoMasker...")
masker = AutoMasker(
    densepose_path=os.path.join(attn_ckpt, "DensePose"),
    schp_path=os.path.join(attn_ckpt, "SCHP"),
    device="cuda"
)
mask_res = masker(person_img, mask_type="upper")
mask_pil = mask_res["mask"]
mask_pil.save(PROJECT_ROOT / "outputs/catvton_mask_test.png")
print("Mask created and saved.")

print("2. Initializing CatVTONPipeline (fp16)...")
t0 = time.time()
pipe = CatVTONPipeline(
    base_ckpt=base_ckpt,
    attn_ckpt=attn_ckpt,
    attn_ckpt_version="mix",
    weight_dtype=torch.float16,
    skip_safety_check=True,
    use_tf32=True,
    device="cuda"
)
t_load = time.time() - t0
print(f"Pipeline initialized in {t_load:.2f}s")

print("3. Running CatVTON Diffusion (25 steps)...")
t1 = time.time()
generator = torch.Generator(device="cuda").manual_seed(42)
res_img = pipe(
    image=person_img,
    condition_image=garment_img,
    mask=mask_pil,
    num_inference_steps=25,
    guidance_scale=2.5,
    height=1024,
    width=768,
    generator=generator
)[0]
t_infer = time.time() - t1
print(f"Diffusion completed in {t_infer:.2f}s!")

out_path = PROJECT_ROOT / "outputs/real_catvton_diffusion_mint_shirt.png"
res_img.save(out_path)
print(f"Saved result to {out_path}")
