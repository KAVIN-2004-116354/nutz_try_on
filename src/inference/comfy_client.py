import os
import sys
import io
import time
import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.inference.engine import process_garment_background_and_patterns

COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188")
COMFY_INPUT_DIR = Path("/home/lenovo/ComfyUI/input")
COMFY_OUTPUT_DIR = Path("/home/lenovo/ComfyUI/output")

def resize_and_crop(image: Image.Image, size: tuple = (768, 1024)) -> Image.Image:
    """Crops and resizes image to exact target aspect ratio and resolution."""
    w, h = image.size
    target_w, target_h = size
    if w / h < target_w / target_h:
        new_w = w
        new_h = w * target_h // target_w
    else:
        new_h = h
        new_w = h * target_w // target_h
    cropped = image.crop(
        ((w - new_w) // 2, (h - new_h) // 2, (w + new_w) // 2, (h + new_h) // 2)
    )
    return cropped.resize(size, Image.Resampling.LANCZOS)

def is_comfyui_alive(timeout: float = 2.0) -> bool:
    try:
        req = urllib.request.urlopen(f"{COMFYUI_URL}/system_stats", timeout=timeout)
        return req.getcode() == 200
    except Exception:
        return False

def run_comfyui_tryon(
    person_img: Image.Image,
    garment_img: Image.Image,
    cloth_type: str = "upper",
    seed: int = 42,
    steps: int = 40,
    cfg: float = 2.5,
    timeout: int = 180
) -> Dict[str, Any]:
    """
    Executes Virtual Try-On using the exact ComfyUI CatVTON workflow:
    - Node 12: LoadAutoMasker (DensePose + SCHP parser)
    - Node 17: LoadCatVTONPipeline (SD1.5 Inpainting + CatVTON attention adapter)
    - Node 10: Target Person
    - Node 11: Reference Garment
    - Node 13: AutoMasker (cloth_type: upper, lower, overall)
    - Node 14: SaveImage (Masked Target Preview)
    - Node 15: SaveImage (Binary Mask Preview)
    - Node 16: CatVTON Diffusion Inpainting
    - Node 18: SaveImage (Virtual Try-On Result)
    """
    t0 = time.time()
    COMFY_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    run_id = f"tryon_{int(time.time()*1000)}"
    person_fn = f"person_{run_id}.png"
    garment_fn = f"garment_{run_id}.png"
    out_prefix = f"CatVTON_{run_id}"
    mask_prefix = f"Mask_{run_id}"
    masked_target_prefix = f"MaskedTarget_{run_id}"

    # 1. Pre-align person to (768, 1024) preserving aspect ratio and zero cropping shift
    has_alpha = person_img.mode in ("RGBA", "LA") or (person_img.mode == "P" and "transparency" in person_img.info)
    if has_alpha:
        p_rgba = person_img.convert("RGBA")
        w, h = p_rgba.size
        if w == 768 and h == 1024:
            p_aligned = p_rgba
        else:
            scale = min(768.0 / w, 1024.0 / h)
            nw, nh = int(round(w * scale)), int(round(h * scale))
            scaled = p_rgba.resize((nw, nh), Image.Resampling.LANCZOS)
            p_aligned = Image.new("RGBA", (768, 1024), (15, 23, 42, 0))
            p_aligned.paste(scaled, ((768 - nw) // 2, (1024 - nh) // 2))

        alpha_channel = p_aligned.split()[-1]
        # Composite onto dark navy matching UI background (#0f172a) to prevent bright white edge halos
        dark_bg = Image.new("RGBA", (768, 1024), (15, 23, 42, 255))
        clean_p = Image.alpha_composite(dark_bg, p_aligned).convert("RGB")
    else:
        clean_p = resize_and_crop(person_img.convert("RGB"), (768, 1024))
        alpha_channel = None

    clean_g = process_garment_background_and_patterns(garment_img)
    p_path = COMFY_INPUT_DIR / person_fn
    g_path = COMFY_INPUT_DIR / garment_fn
    clean_p.save(p_path, format="PNG")
    clean_g.save(g_path, format="PNG")

    # Map cloth_type ("upper_body" -> "upper", "lower_body" -> "lower", "full_body" -> "overall")
    c_type = "upper"
    if cloth_type in ("lower", "lower_body", "pants", "shorts"):
        c_type = "lower"
    elif cloth_type in ("overall", "full", "full_body", "dress", "kurta", "ethnic", "saree", "anarkali"):
        c_type = "overall"

    prompt = {
        "12": {
            "inputs": {
                "catvton_path": "/home/lenovo/ComfyUI/models/catvton"
            },
            "class_type": "LoadAutoMasker",
            "_meta": {"title": "Load AutoMask Generator"}
        },
        "17": {
            "inputs": {
                "sd15_inpaint_path": "/home/lenovo/ComfyUI/models/catvton/stable-diffusion-inpainting",
                "catvton_path": "/home/lenovo/ComfyUI/models/catvton",
                "mixed_precision": "bf16"
            },
            "class_type": "LoadCatVTONPipeline",
            "_meta": {"title": "Load CatVTON Pipeline"}
        },
        "10": {
            "inputs": {
                "image": person_fn
            },
            "class_type": "LoadImage",
            "_meta": {"title": "Target Person"}
        },
        "11": {
            "inputs": {
                "image": garment_fn
            },
            "class_type": "LoadImage",
            "_meta": {"title": "Reference Garment"}
        },
        "13": {
            "inputs": {
                "pipe": ["12", 0],
                "target_image": ["10", 0],
                "cloth_type": c_type
            },
            "class_type": "AutoMasker",
            "_meta": {"title": "Auto Mask Generation"}
        },
        "14": {
            "inputs": {
                "filename_prefix": masked_target_prefix,
                "images": ["13", 1]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save Masked Target"}
        },
        "15": {
            "inputs": {
                "filename_prefix": mask_prefix,
                "images": ["13", 0]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save Binary Mask"}
        },
        "16": {
            "inputs": {
                "pipe": ["17", 0],
                "target_image": ["10", 0],
                "refer_image": ["11", 0],
                "mask_image": ["13", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg
            },
            "class_type": "CatVTON",
            "_meta": {"title": "TryOn by CatVTON"}
        },
        "18": {
            "inputs": {
                "filename_prefix": out_prefix,
                "images": ["16", 0]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save TryOn Image"}
        }
    }

    # Queue prompt
    data = json.dumps({"prompt": prompt}).encode("utf-8")
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
    try:
        res = urllib.request.urlopen(req, timeout=30)
        res_json = json.loads(res.read())
        prompt_id = res_json["prompt_id"]
    except Exception as e:
        raise RuntimeError(f"Failed to queue prompt in ComfyUI: {e}")

    # Poll execution history
    poll_start = time.time()
    out_img_filename = None
    mask_img_filename = None
    masked_target_filename = None

    while time.time() - poll_start < timeout:
        try:
            h_req = urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}", timeout=15)
            history = json.loads(h_req.read())
            if prompt_id in history:
                prompt_output = history[prompt_id]
                status_info = prompt_output.get("status", {})
                if status_info.get("status_str") == "error":
                    raise RuntimeError(f"ComfyUI execution error: {status_info.get('messages', [])}")
                
                outputs = prompt_output.get("outputs", {})
                if "18" in outputs and len(outputs["18"].get("images", [])) > 0:
                    out_img_filename = outputs["18"]["images"][0]["filename"]
                    if "15" in outputs and len(outputs["15"].get("images", [])) > 0:
                        mask_img_filename = outputs["15"]["images"][0]["filename"]
                    if "14" in outputs and len(outputs["14"].get("images", [])) > 0:
                        masked_target_filename = outputs["14"]["images"][0]["filename"]
                    break
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        time.sleep(1.0)

    # Fallback to output directory globbing if history did not return filename
    if not out_img_filename:
        matches = sorted(list(COMFY_OUTPUT_DIR.glob(f"{out_prefix}*")), key=os.path.getmtime, reverse=True)
        if matches:
            out_img_filename = matches[0].name
        else:
            raise TimeoutError("ComfyUI inference timed out or did not produce an output image.")

    out_file_path = COMFY_OUTPUT_DIR / out_img_filename
    result_image = Image.open(out_file_path).convert("RGB")

    # Re-apply aligned transparency
    if alpha_channel is not None:
        result_image.putalpha(alpha_channel)

    # Load mask image if available
    mask_image = None
    if mask_img_filename:
        mask_file_path = COMFY_OUTPUT_DIR / mask_img_filename
        if mask_file_path.exists():
            mask_image = Image.open(mask_file_path).convert("RGB")
    if mask_image is None:
        mask_matches = sorted(list(COMFY_OUTPUT_DIR.glob(f"{mask_prefix}*")), key=os.path.getmtime, reverse=True)
        if mask_matches:
            mask_image = Image.open(mask_matches[0]).convert("RGB")

    # Load masked target if available
    masked_target_img = None
    if masked_target_filename:
        mt_file_path = COMFY_OUTPUT_DIR / masked_target_filename
        if mt_file_path.exists():
            masked_target_img = Image.open(mt_file_path).convert("RGB")

    elapsed_ms = round((time.time() - t0) * 1000, 2)
    
    # Cleanup input images
    try:
        if p_path.exists(): p_path.unlink()
        if g_path.exists(): g_path.unlink()
    except Exception:
        pass

    return {
        "status": "success",
        "backend": "comfyui_catvton",
        "prompt_id": prompt_id,
        "cloth_type": c_type,
        "inference_time_ms": elapsed_ms,
        "tryon_image": result_image,
        "mask_image": mask_image if mask_image is not None else result_image,
        "masked_target": masked_target_img,
        "output_file": str(out_file_path)
    }

def run_openmoss_tryon(
    person_img: Image.Image,
    garment_img: Optional[Image.Image] = None,
    prompt_desc: Optional[str] = None,
    seed: int = 42,
    steps: int = 25,
    cfg: float = 2.5,
    denoise: float = 0.75,
    timeout: int = 180
) -> Dict[str, Any]:
    """
    Executes Virtual Try-On using the OpenMOSS Bounding-Box Layout & DiT Pipeline.
    Does not require external cloth segmentation models.
    """
    t0 = time.time()
    COMFY_INPUT_DIR.mkdir(parents=True, exist_ok=True)

    run_id = f"openmoss_{int(time.time()*1000)}"
    person_fn = f"person_{run_id}.png"
    out_prefix = f"OpenMOSS_{run_id}"

    # Resize person to 1024x1024 for MOSS DiT
    clean_p = resize_and_crop(person_img.convert("RGB"), (1024, 1024))
    p_path = COMFY_INPUT_DIR / person_fn
    clean_p.save(p_path, format="PNG")

    clothing_prompt = prompt_desc or "emerald green textured cotton button-up casual shirt with crisp collar"
    full_prompt = (
        f"High quality studio photograph of a person wearing an {clothing_prompt}, "
        "natural indoor lighting, detailed fabric weave and buttons, realistic wrinkles and drape, "
        "hands clearly visible and untouched, sharp focus, 8k resolution."
    )

    prompt = {
        "1": {
            "inputs": {
                "unet_name": "moss_image_sft_int8_convrot.safetensors",
                "weight_dtype": "default"
            },
            "class_type": "UNETLoader",
            "_meta": {"title": "Load OpenMOSS UNET"}
        },
        "2": {
            "inputs": {
                "double_layers": "",
                "single_layers": "22",
                "start_percent": 0.0,
                "end_percent": 0.5,
                "model": ["1", 0]
            },
            "class_type": "SkipLayerGuidanceDiTSimple",
            "_meta": {"title": "SkipLayerGuidanceDiTSimple"}
        },
        "3": {
            "inputs": {
                "clip_name": "Qwen35/qwen3.5_9b_int8_convrot.safetensors",
                "type": "moss_image",
                "device": "default"
            },
            "class_type": "CLIPLoader",
            "_meta": {"title": "Load Qwen3.5 CLIP"}
        },
        "4": {
            "inputs": {
                "vae_name": "flux2-vae.safetensors"
            },
            "class_type": "VAELoader",
            "_meta": {"title": "Load Flux2 VAE"}
        },
        "10": {
            "inputs": {
                "image": person_fn
            },
            "class_type": "LoadImage",
            "_meta": {"title": "Target Person"}
        },
        "13": {
            "inputs": {
                "background": ["10", 0],
                "width": 1024,
                "height": 1024,
                "editor_state": [
                    {
                        "x": 288,
                        "y": 64,
                        "width": 460,
                        "height": 900,
                        "metadata": {
                            "type": "obj",
                            "text": "",
                            "desc": "young man standing naturally with hands visible",
                            "palette": []
                        }
                    },
                    {
                        "x": 272,
                        "y": 280,
                        "width": 480,
                        "height": 480,
                        "metadata": {
                            "type": "obj",
                            "text": "",
                            "desc": clothing_prompt,
                            "palette": []
                        }
                    }
                ],
                "last_incoming": []
            },
            "class_type": "CreateBoundingBoxes",
            "_meta": {"title": "Create Bounding Boxes (Cloth Region)"}
        },
        "12": {
            "inputs": {
                "prompt": full_prompt,
                "element": ["13", 2],
                "width": 1024,
                "height": 1024,
                "character_boxes": "1"
            },
            "class_type": "MOSSImageLayoutPrompt",
            "_meta": {"title": "MOSS-Image Layout Prompt"}
        },
        "5": {
            "inputs": {
                "text": ["12", 0],
                "clip": ["3", 0]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Positive Conditioning"}
        },
        "6": {
            "inputs": {
                "text": "blurry, distorted hands, amputated fingers, deformed limbs, unrealistic texture, low quality, cartoon",
                "clip": ["3", 0]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Negative Conditioning"}
        },
        "15": {
            "inputs": {
                "pixels": ["10", 0],
                "vae": ["4", 0]
            },
            "class_type": "VAEEncode",
            "_meta": {"title": "Encode Person Latent"}
        },
        "8": {
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "er_sde",
                "scheduler": "simple",
                "denoise": denoise,
                "model": ["2", 0],
                "positive": ["5", 0],
                "negative": ["6", 0],
                "latent_image": ["15", 0]
            },
            "class_type": "KSampler",
            "_meta": {"title": "OpenMOSS KSampler"}
        },
        "9": {
            "inputs": {
                "samples": ["8", 0],
                "vae": ["4", 0]
            },
            "class_type": "VAEDecode",
            "_meta": {"title": "Decode Latent to Image"}
        },
        "18": {
            "inputs": {
                "filename_prefix": out_prefix,
                "images": ["9", 0]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save OpenMOSS TryOn Image"}
        }
    }

    # Queue prompt
    data = json.dumps({"prompt": prompt}).encode("utf-8")
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
    try:
        res = urllib.request.urlopen(req, timeout=30)
        res_json = json.loads(res.read())
        prompt_id = res_json["prompt_id"]
    except Exception as e:
        raise RuntimeError(f"Failed to queue OpenMOSS prompt in ComfyUI: {e}")

    # Poll execution history
    poll_start = time.time()
    out_img_filename = None

    while time.time() - poll_start < timeout:
        try:
            h_req = urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}", timeout=15)
            history = json.loads(h_req.read())
            if prompt_id in history:
                prompt_output = history[prompt_id]
                status_info = prompt_output.get("status", {})
                if status_info.get("status_str") == "error":
                    raise RuntimeError(f"ComfyUI OpenMOSS error: {status_info.get('messages', [])}")
                
                outputs = prompt_output.get("outputs", {})
                if "18" in outputs and len(outputs["18"].get("images", [])) > 0:
                    out_img_filename = outputs["18"]["images"][0]["filename"]
                    break
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        time.sleep(1.0)

    if not out_img_filename:
        matches = sorted(list(COMFY_OUTPUT_DIR.glob(f"{out_prefix}*")), key=os.path.getmtime, reverse=True)
        if matches:
            out_img_filename = matches[0].name
        else:
            raise TimeoutError("ComfyUI OpenMOSS inference timed out.")

    out_file_path = COMFY_OUTPUT_DIR / out_img_filename
    result_image = Image.open(out_file_path).convert("RGB")
    elapsed_ms = round((time.time() - t0) * 1000, 2)

    try:
        if p_path.exists(): p_path.unlink()
    except Exception:
        pass

    return {
        "status": "success",
        "backend": "comfyui_openmoss",
        "prompt_id": prompt_id,
        "inference_time_ms": elapsed_ms,
        "tryon_image": result_image,
        "output_file": str(out_file_path)
    }
