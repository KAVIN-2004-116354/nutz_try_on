"""Cloud Image Generation Module (Flux.1 Dev via Nutz Railway API).

Provides client interface to the remote FLUX-DEV-012 endpoint for:
1. Dual-panel spatial reference conditioning for virtual try-on (Canvas Stitching).
2. Generating high-resolution AI fashion models on demand.
3. Inpainting / editing existing person images with strict identity preservation.
4. Health checking the remote cloud generation service.
"""

import os
import io
import base64
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union, Tuple
import requests
from dotenv import load_dotenv
from PIL import Image, ImageOps

try:
    from src.inference.category_prompts import (
        normalize_category,
        get_category_config,
        build_flux_category_prompt,
    )
except ImportError:
    from inference.category_prompts import (
        normalize_category,
        get_category_config,
        build_flux_category_prompt,
    )

logger = logging.getLogger("nutz.cloud_generator")

# Load environment
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_BASE_URL = os.getenv("IMAGE_API_BASE_URL", "https://nutz-image1284.up.railway.app").rstrip("/")
DEFAULT_MODEL = "FLUX-DEV-012"


def get_api_key() -> Optional[str]:
    return os.getenv("IMAGE_API_KEY")


def is_cloud_flux_alive(base_url: Optional[str] = None) -> bool:
    """Quick check if remote Flux API is reachable and API key is valid."""
    api_key = get_api_key()
    if not api_key:
        return False
    url = f"{base_url or DEFAULT_BASE_URL}/v1/models"
    try:
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5
        )
        return resp.status_code == 200
    except Exception:
        return False


def generate_cloud_image(
    prompt: str,
    model: str = DEFAULT_MODEL,
    size: str = "1024x1024",
    output_path: Optional[Union[str, Path]] = None,
    base_url: Optional[str] = None,
    timeout: int = 120,
) -> Optional[Image.Image]:
    """
    Generate an image using the cloud FLUX model.
    Returns PIL Image (and saves to output_path if provided).
    """
    api_key = get_api_key()
    if not api_key:
        raise ValueError("IMAGE_API_KEY is not set in environment or .env")

    url = f"{base_url or DEFAULT_BASE_URL}/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "model": model,
        "n": 1,
        "size": size,
        "response_format": "b64_json",
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    if resp.status_code != 200:
        logger.error(f"Cloud generation failed (HTTP {resp.status_code}): {resp.text}")
        raise RuntimeError(f"Cloud generation failed: HTTP {resp.status_code} - {resp.text}")

    data = resp.json().get("data", [])
    if not data:
        raise RuntimeError(f"No image data returned from API: {resp.text}")

    item = data[0]
    img: Optional[Image.Image] = None

    if "b64_json" in item and item["b64_json"]:
        raw_bytes = base64.b64decode(item["b64_json"])
        img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    elif "url" in item and item["url"]:
        img_resp = requests.get(item["url"], timeout=30)
        img_resp.raise_for_status()
        img = Image.open(io.BytesIO(img_resp.content)).convert("RGB")
    else:
        raise ValueError(f"Unrecognized response data format: {item}")

    if output_path and img:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(out_p))
        logger.info(f"Saved generated image to {out_p}")

    return img


def edit_cloud_image(
    image: Union[Image.Image, str, Path, bytes],
    prompt: str,
    mask: Optional[Union[Image.Image, str, Path, bytes]] = None,
    model: str = DEFAULT_MODEL,
    output_path: Optional[Union[str, Path]] = None,
    base_url: Optional[str] = None,
    timeout: int = 120,
) -> Optional[Image.Image]:
    """
    Edit / inpaint clothing onto an existing person image using the cloud FLUX model.
    Sends multipart form to /v1/images/edits, optionally with an inpainting mask.
    """
    api_key = get_api_key()
    if not api_key:
        raise ValueError("IMAGE_API_KEY is not set in environment or .env")

    # Prepare image bytes
    img_bytes: bytes
    if isinstance(image, Image.Image):
        buf = io.BytesIO()
        rgb_img = image.convert("RGB")
        rgb_img.save(buf, format="PNG")
        img_bytes = buf.getvalue()
    elif isinstance(image, (str, Path)):
        p = Path(image)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        with open(p, "rb") as f:
            img_bytes = f.read()
    elif isinstance(image, bytes):
        img_bytes = image
    else:
        raise ValueError(f"Unsupported image input type: {type(image)}")

    # Prepare mask bytes if provided
    mask_bytes: Optional[bytes] = None
    if mask is not None:
        if isinstance(mask, Image.Image):
            mbuf = io.BytesIO()
            mask.save(mbuf, format="PNG")
            mask_bytes = mbuf.getvalue()
        elif isinstance(mask, (str, Path)):
            mp = Path(mask)
            if not mp.is_absolute():
                mp = PROJECT_ROOT / mp
            with open(mp, "rb") as mf:
                mask_bytes = mf.read()
        elif isinstance(mask, bytes):
            mask_bytes = mask

    url = f"{base_url or DEFAULT_BASE_URL}/v1/images/edits"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    files = {
        "image": ("input_person.png", img_bytes, "image/png"),
    }
    if mask_bytes is not None:
        files["mask"] = ("mask.png", mask_bytes, "image/png")

    data = {
        "prompt": prompt,
        "model": model,
        "response_format": "b64_json",
    }

    logger.info(f"Submitting image edit request to {url} (model={model}, mask={'yes' if mask_bytes else 'no'})...")
    resp = requests.post(url, headers=headers, files=files, data=data, timeout=timeout)
    if resp.status_code != 200:
        logger.error(f"Cloud image edit failed (HTTP {resp.status_code}): {resp.text}")
        raise RuntimeError(f"Cloud image edit failed: HTTP {resp.status_code} - {resp.text}")

    data_resp = resp.json().get("data", [])
    if not data_resp:
        raise RuntimeError(f"No image data returned from edits API: {resp.text}")

    item = data_resp[0]
    img: Optional[Image.Image] = None

    if "b64_json" in item and item["b64_json"]:
        raw_bytes = base64.b64decode(item["b64_json"])
        img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    elif "url" in item and item["url"]:
        img_resp = requests.get(item["url"], timeout=30)
        img_resp.raise_for_status()
        img = Image.open(io.BytesIO(img_resp.content)).convert("RGB")
    else:
        raise ValueError(f"Unrecognized response data format: {item}")

    if output_path and img:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(out_p))
        logger.info(f"Saved edited image to {out_p}")

    return img


def create_tryon_canvas(
    person: Image.Image,
    garment: Image.Image,
    person_mask: Optional[Union[Image.Image, str, Path, bytes]] = None,
    target_width: int = 1536,
    target_height: int = 1024,
    panel_split_ratio: float = 0.5,
) -> Tuple[Image.Image, Image.Image, Tuple[int, int, int, int], Tuple[int, int]]:
    """
    Creates a composite dual-panel canvas for FLUX inpainting try-on:
    - Left panel: Target Person (masked in clothing area, 0 everywhere else).
    - Right panel: Garment Reference (100% UNMASKED / value 0).

    Guarantees:
    - Zero aspect ratio distortion (contain/letterbox with neutral studio background).
    - Dimensions are clean multiples of 32 (FLUX VAE friendly).
    - Exact cropping coordinates to extract the person back after diffusion.
    """
    orig_p_size = person.size
    p_w, p_h = orig_p_size

    # Ensure RGB
    person_rgb = person.convert("RGB")
    garment_rgb = garment.convert("RGBA") if garment.mode == "RGBA" else garment.convert("RGB")

    # Parse person mask
    if person_mask is not None:
        if isinstance(person_mask, Image.Image):
            p_mask = person_mask.convert("L")
        elif isinstance(person_mask, (str, Path)):
            p_mask = Image.open(person_mask).convert("L")
        elif isinstance(person_mask, bytes):
            p_mask = Image.open(io.BytesIO(person_mask)).convert("L")
        else:
            p_mask = Image.new("L", orig_p_size, color=255)
    else:
        # Default fallback: mask center torso region
        p_mask = Image.new("L", orig_p_size, color=0)
        import numpy as np
        m_arr = np.array(p_mask)
        m_arr[int(p_h * 0.25):int(p_h * 0.8), int(p_w * 0.15):int(p_w * 0.85)] = 255
        p_mask = Image.fromarray(m_arr)

    # Ensure mask matches person size
    if p_mask.size != orig_p_size:
        p_mask = p_mask.resize(orig_p_size, Image.Resampling.NEAREST)

    # Clean multiples of 32
    target_width = (target_width // 32) * 32
    target_height = (target_height // 32) * 32

    left_panel_w = int(round(target_width * panel_split_ratio))
    left_panel_w = (left_panel_w // 32) * 32
    right_panel_w = target_width - left_panel_w

    # Fit Person into Left Panel preserving aspect ratio
    person_fitted = ImageOps.contain(person_rgb, (left_panel_w, target_height), Image.Resampling.LANCZOS)
    fit_w, fit_h = person_fitted.size

    # Create Left Panel canvas and mask
    left_panel_img = Image.new("RGB", (left_panel_w, target_height), color=(245, 245, 245))
    left_panel_mask = Image.new("L", (left_panel_w, target_height), color=0)

    # Offset to center
    offset_x = (left_panel_w - fit_w) // 2
    offset_y = (target_height - fit_h) // 2
    left_panel_img.paste(person_fitted, (offset_x, offset_y))

    # Scale and center the person mask identically
    mask_fitted = ImageOps.contain(p_mask, (left_panel_w, target_height), Image.Resampling.NEAREST)
    left_panel_mask.paste(mask_fitted, (offset_x, offset_y))

    # Fit Garment into Right Panel preserving aspect ratio
    garment_fitted = ImageOps.contain(garment_rgb, (right_panel_w - 24, target_height - 24), Image.Resampling.LANCZOS)
    g_fit_w, g_fit_h = garment_fitted.size

    right_panel_img = Image.new("RGB", (right_panel_w, target_height), color=(250, 250, 250))
    g_offset_x = (right_panel_w - g_fit_w) // 2
    g_offset_y = (target_height - g_fit_h) // 2

    if garment_fitted.mode == "RGBA":
        right_panel_img.paste(garment_fitted, (g_offset_x, g_offset_y), garment_fitted)
    else:
        right_panel_img.paste(garment_fitted, (g_offset_x, g_offset_y))

    # Build full composite canvas
    composite_canvas = Image.new("RGB", (target_width, target_height), color=(255, 255, 255))
    composite_canvas.paste(left_panel_img, (0, 0))
    composite_canvas.paste(right_panel_img, (left_panel_w, 0))

    # Build full composite mask: Left panel has clothing mask; Right panel is 100% BLACK (0)
    composite_mask = Image.new("L", (target_width, target_height), color=0)
    composite_mask.paste(left_panel_mask, (0, 0))

    # Define crop coordinates to extract the person back
    person_crop_box = (offset_x, offset_y, offset_x + fit_w, offset_y + fit_h)

    return composite_canvas, composite_mask, person_crop_box, orig_p_size


def build_spatial_canvas_prompt(
    category: Optional[str] = None,
    user_prompt: Optional[str] = None,
    garment_desc: Optional[str] = None,
) -> str:
    """
    Constructs the spatial dual-panel reference prompt for FLUX inpainting.
    Instructs the Diffusion Transformer to transfer visual features from the right panel onto the left panel.
    """
    canonical_cat = normalize_category(category or "shirt")
    cat_cfg = get_category_config(canonical_cat)
    cat_name = cat_cfg.get("name", "Garment").upper()
    cat_directive = cat_cfg.get("directive", "")

    optional_user_note = ""
    if user_prompt and user_prompt.strip():
        optional_user_note = f"\nADDITIONAL STYLING DIRECTIVE:\n{user_prompt.strip()}\n"
    elif garment_desc and garment_desc.strip():
        optional_user_note = f"\nGARMENT ATTRIBUTE GUIDANCE:\n{garment_desc.strip()}\n"

    prompt = (
        f"FLUX VIRTUAL TRY-ON — {cat_name} DUAL-PANEL SPATIAL REFERENCE TRANSFORMATION\n\n"
        f"SPATIAL COMPOSITION:\n"
        f"- LEFT PANEL: Target person photograph (face, hairstyle, skin tone, body proportions and pose).\n"
        f"- RIGHT PANEL: Authentic reference garment (authoritative visual source for clothing appearance).\n\n"
        f"OBJECTIVE:\n"
        f"Seamlessly dress the target person on the left panel in the exact {cat_name.lower()} shown in the right panel.\n\n"
        f"GARMENT DESIGN FIDELITY (MANDATORY):\n"
        f"- Transfer the exact original colors, color balance, and fabric texture from the right panel onto the person on the left.\n"
        f"- Faithfully replicate all printed patterns, character motifs, florals, checks, stripes, and graphics from the right panel.\n"
        f"- Faithfully replicate all embroidery, needlework, ornamental borders, and decorative elements from the right panel.\n"
        f"- Faithfully replicate logos, collar design, button plackets, and sleeve construction from the right panel.\n"
        f"- Adapt garment geometry naturally to the target person's existing pose with realistic fabric draping, folds, and contact shadows.\n\n"
        f"{cat_directive}\n"
        f"{optional_user_note}"
        f"IDENTITY & ANATOMY PRESERVATION (STRICT):\n"
        f"- Strictly preserve the target person's face, facial features, eyes, nose, lips, and expression.\n"
        f"- Strictly preserve hairstyle, hairline, facial hair, skin tone, and ethnicity.\n"
        f"- Strictly preserve original shoulder width, chest, waist, arms, hands, body proportions, and pose.\n"
        f"- Do not modify unmasked background or unrelated clothing.\n\n"
        f"Photorealistic commercial fashion photography, pristine studio lighting, flawless edge blending, 8k resolution masterpiece."
    )
    return prompt


def run_flux_tryon(
    person_img: Image.Image,
    garment_img: Optional[Image.Image] = None,
    garment_desc: str = "",
    custom_prompt: Optional[str] = None,
    mask_img: Optional[Union[Image.Image, str, Path, bytes]] = None,
    category: Optional[str] = None,
    output_path: Optional[Union[str, Path]] = None,
    timeout: int = 120,
    use_canvas_conditioning: bool = True,
) -> Dict[str, Any]:
    """
    Executes Virtual Try-On exclusively using the cloud FLUX-DEV-012 model.
    Guarantees photorealistic synthesis with visual reference conditioning:
    1. If garment_img is provided: Dual-panel canvas conditioning ([Person | Garment]).
    2. If garment_img is None: Direct text-guided inpainting (Pure FLUX styling mode).
    """
    import time
    start_t = time.time()

    canvas_preview: Optional[Image.Image] = None
    canvas_mask_preview: Optional[Image.Image] = None

    if garment_img is not None and use_canvas_conditioning:
        # Dual-Panel Spatial Reference Conditioning Workflow
        logger.info("Assembling dual-panel try-on canvas for FLUX visual reference conditioning...")
        canvas, canvas_mask, crop_box, orig_size = create_tryon_canvas(
            person=person_img,
            garment=garment_img,
            person_mask=mask_img,
            target_width=1536,
            target_height=1024,
        )
        canvas_preview = canvas
        canvas_mask_preview = canvas_mask

        # Formulate spatial conditioning prompt
        prompt = build_spatial_canvas_prompt(
            category=category or custom_prompt,
            user_prompt=custom_prompt,
            garment_desc=garment_desc,
        )
        logger.info(f"Submitting dual-panel canvas to FLUX with prompt snippet: {prompt[:250]}...")

        # Primary: Execute image edit via /v1/images/edits on composite canvas
        try:
            composite_result = edit_cloud_image(
                image=canvas,
                prompt=prompt,
                mask=canvas_mask,
                model=DEFAULT_MODEL,
                timeout=timeout,
            )
            # Crop the target person back from the left panel
            cropped_person = composite_result.crop(crop_box)
            # Resize back to exact original person dimensions with Lanczos
            tryon_img = cropped_person.resize(orig_size, Image.Resampling.LANCZOS)
            logger.info(f"Successfully extracted dressed person: {tryon_img.size}")
        except Exception as e:
            logger.warning(f"Dual-panel canvas edit failed ({e}), falling back to direct person edit...")
            tryon_img = edit_cloud_image(
                image=person_img,
                prompt=custom_prompt or prompt,
                mask=mask_img,
                model=DEFAULT_MODEL,
                timeout=timeout,
            )
    else:
        # Single-image text-guided inpainting (Pure FLUX mode)
        if custom_prompt and custom_prompt.strip():
            prompt = custom_prompt.strip()
        else:
            desc = garment_desc.strip() if garment_desc else "luxury fashion apparel"
            prompt = (
                f"Full-length high-fashion photography portrait: seamless virtual try-on, "
                f"change outfit to {desc}, perfectly fitted and styled, "
                f"strictly preserve model facial identity, ethnicity, expression, natural skin texture, hair, and body posture, "
                f"pristine studio lighting, 8k resolution, photorealistic masterpiece."
            )

        logger.info(f"Running single-image Flux.1 Dev Try-On with prompt: {prompt[:200]}...")
        try:
            tryon_img = edit_cloud_image(
                image=person_img,
                prompt=prompt,
                mask=mask_img,
                model=DEFAULT_MODEL,
                output_path=output_path,
                timeout=timeout,
            )
        except Exception as e:
            logger.warning(f"Flux edit endpoint failed ({e}), falling back to Flux text-to-image synthesis...")
            synthesis_prompt = (
                f"Full-body professional fashion photography of the fashion model wearing {garment_desc or 'designer outfit'}, "
                f"clean modern studio background, natural posture, photorealistic, 8k resolution, masterpiece."
            )
            tryon_img = generate_cloud_image(
                prompt=synthesis_prompt,
                model=DEFAULT_MODEL,
                size="1024x1024",
                output_path=output_path,
                timeout=timeout,
            )

    if output_path and tryon_img:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        tryon_img.save(str(out_p))
        logger.info(f"Saved edited image to {out_p}")

    latency_ms = round((time.time() - start_t) * 1000, 2)
    return {
        "status": "success",
        "tryon_image": tryon_img,
        "canvas_preview": canvas_preview,
        "canvas_mask_preview": canvas_mask_preview,
        "model_used": f"{DEFAULT_MODEL} (Flux.1 Dev Cloud)",
        "engine": "flux",
        "resolution": f"{tryon_img.width}x{tryon_img.height}",
        "inference_time_ms": latency_ms,
        "output_file": str(output_path) if output_path else None,
    }


def generate_fashion_model(
    gender: str = "female",
    ethnicity: str = "indian",
    garment_context: str = "wearing a plain neutral tank top and jeans",
    setting: str = "studio lighting, clean solid neutral grey background, full body shot",
    output_path: Optional[Union[str, Path]] = None,
) -> Optional[Image.Image]:
    """
    High-level generator for virtual try-on model baselines.
    Produces high quality full-body model photos optimized for virtual try-on inpainting.
    """
    prompt = (
        f"Full-body professional fashion catalog photography of an attractive {ethnicity} {gender} fashion model, "
        f"{garment_context}, standing upright in neutral forward-facing pose, {setting}, "
        f"photorealistic, 8k, sharp focus, natural skin texture, masterpiece."
    )
    return generate_cloud_image(prompt=prompt, output_path=output_path)
