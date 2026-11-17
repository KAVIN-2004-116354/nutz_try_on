import sys
import time
import torch
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path("/home/lenovo/try_on")
sys.path.append(str(PROJECT_ROOT))
sys.path.append("/home/lenovo/ComfyUI/custom_nodes/Comfyui-CatVTON")

_CATVTON_PIPE = None
_CATVTON_MASKER = None

def get_catvton_pipeline():
    global _CATVTON_PIPE, _CATVTON_MASKER
    if _CATVTON_PIPE is None:
        base_ckpt = "/home/lenovo/ComfyUI/models/catvton/stable-diffusion-inpainting"
        attn_ckpt = "/home/lenovo/ComfyUI/models/catvton"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        from model.cloth_masker import AutoMasker
        from model.pipeline import CatVTONPipeline
        
        print("[CatVTON Engine] Initializing AutoMasker...")
        _CATVTON_MASKER = AutoMasker(
            densepose_path=attn_ckpt + "/DensePose",
            schp_path=attn_ckpt + "/SCHP",
            device=device
        )
        
        print(f"[CatVTON Engine] Initializing CatVTON Diffusion Pipeline on {device} (fp16)...")
        _CATVTON_PIPE = CatVTONPipeline(
            base_ckpt=base_ckpt,
            attn_ckpt=attn_ckpt,
            attn_ckpt_version="mix",
            weight_dtype=torch.float16 if device == "cuda" else torch.float32,
            skip_safety_check=True,
            use_tf32=True,
            device=device
        )
        print("[CatVTON Engine] Ready!")
    return _CATVTON_PIPE, _CATVTON_MASKER

def run_direct_catvton(
    person_img: Image.Image,
    garment_img: Image.Image,
    category: str = "upper",
    steps: int = 20,
    seed: int = 42,
    guidance_scale: float = 2.5
):
    t0 = time.time()
    pipe, masker = get_catvton_pipeline()
    
    # Map category to mask_type
    cat_lower = str(category).lower()
    if cat_lower in ("lower", "lower_body", "jeans", "pants", "shorts", "formal_trousers"):
        mask_type = "lower"
    elif cat_lower in ("full", "overall", "dress", "saree", "lehenga", "anarkali", "dhoti", "western_dress"):
        mask_type = "overall"
    elif cat_lower in ("kurta", "sherwani", "achkan"):
        mask_type = "kurta"
    else:
        mask_type = "upper"
        
    mask_res = masker(person_img, mask_type=mask_type)
    mask_pil = mask_res["mask"]
    
    generator = torch.Generator(device=pipe.device).manual_seed(seed)
    res_img = pipe(
        image=person_img,
        condition_image=garment_img,
        mask=mask_pil,
        num_inference_steps=steps,
        guidance_scale=guidance_scale,
        height=1024,
        width=768,
        generator=generator
    )[0]
    
    elapsed_ms = round((time.time() - t0) * 1000, 2)
    return {
        "status": "success",
        "tryon_image": res_img,
        "mask_image": mask_pil,
        "inference_time_ms": elapsed_ms,
        "model_used": "CatVTON-Diffusion (Local GPU RTX 5050)",
    }
