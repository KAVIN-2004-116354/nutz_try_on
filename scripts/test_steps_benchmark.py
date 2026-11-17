import time
import torch
from pathlib import Path
from PIL import Image
import sys

PROJECT_ROOT = Path("/home/lenovo/try_on")
sys.path.append(str(PROJECT_ROOT))
sys.path.append("/home/lenovo/ComfyUI/custom_nodes/Comfyui-CatVTON")

from model.cloth_masker import AutoMasker
from model.pipeline import CatVTONPipeline

base_ckpt = "/home/lenovo/ComfyUI/models/catvton/stable-diffusion-inpainting"
attn_ckpt = "/home/lenovo/ComfyUI/models/catvton"

person_img = Image.open(PROJECT_ROOT / "frontend/assets/sample_person_1.jpg").convert("RGB")
garment_img = Image.open(PROJECT_ROOT / "frontend/assets/sample_emerald_shirt.jpg").convert("RGB")

masker = AutoMasker(
    densepose_path=attn_ckpt + "/DensePose",
    schp_path=attn_ckpt + "/SCHP",
    device="cuda"
)
mask_pil = masker(person_img, mask_type="upper")["mask"]

pipe = CatVTONPipeline(
    base_ckpt=base_ckpt,
    attn_ckpt=attn_ckpt,
    attn_ckpt_version="mix",
    weight_dtype=torch.float16,
    skip_safety_check=True,
    use_tf32=True,
    device="cuda"
)

for steps in [15, 20]:
    t0 = time.time()
    generator = torch.Generator(device="cuda").manual_seed(42)
    res_img = pipe(
        image=person_img,
        condition_image=garment_img,
        mask=mask_pil,
        num_inference_steps=steps,
        guidance_scale=2.5,
        height=1024,
        width=768,
        generator=generator
    )[0]
    dt = time.time() - t0
    out = PROJECT_ROOT / f"outputs/catvton_diffusion_{steps}steps.png"
    res_img.save(out)
    print(f"Steps: {steps} -> {dt:.2f}s, saved to {out.name}")
