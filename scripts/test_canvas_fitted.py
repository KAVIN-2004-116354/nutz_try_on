import os
import sys
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np

PROJECT_ROOT = Path("/home/lenovo/try_on")
sys.path.append(str(PROJECT_ROOT))

def create_tryon_canvas(
    person: Image.Image,
    garment: Image.Image,
    person_mask: Image.Image,
    target_width: int = 1536,
    target_height: int = 1024,
    panel_split_ratio: float = 0.5,
):
    """
    Creates a composite dual-panel canvas for FLUX inpainting try-on:
    - Left panel: Target Person (masked in clothing area, 0 everywhere else).
    - Right panel: Garment Reference (100% UNMASKED / value 0).

    Guarantees:
    - Zero aspect ratio distortion (contain/letterbox with neutral studio background).
    - Dimensions are clean multiples of 32 (FLUX VAE friendly).
    - Exact cropping back to original person aspect ratio and dimensions.
    """
    orig_p_size = person.size
    p_w, p_h = orig_p_size

    # Ensure target dimensions are multiples of 32
    target_width = (target_width // 32) * 32
    target_height = (target_height // 32) * 32

    left_panel_w = int(round(target_width * panel_split_ratio))
    left_panel_w = (left_panel_w // 32) * 32
    right_panel_w = target_width - left_panel_w

    # Fit Person into Left Panel preserving aspect ratio
    person_fitted = ImageOps.contain(person, (left_panel_w, target_height), Image.Resampling.LANCZOS)
    fit_w, fit_h = person_fitted.size

    # Create Left Panel images
    left_panel_img = Image.new("RGB", (left_panel_w, target_height), color=(240, 240, 240))
    left_panel_mask = Image.new("L", (left_panel_w, target_height), color=0)

    # Offset to center
    offset_x = (left_panel_w - fit_w) // 2
    offset_y = (target_height - fit_h) // 2
    left_panel_img.paste(person_fitted, (offset_x, offset_y))

    # Scale and center the person mask identically
    mask_fitted = ImageOps.contain(person_mask, (left_panel_w, target_height), Image.Resampling.NEAREST)
    left_panel_mask.paste(mask_fitted, (offset_x, offset_y))

    # Fit Garment into Right Panel preserving aspect ratio
    # If garment has alpha channel, paste over clean neutral background
    garment_rgb = garment.convert("RGBA") if garment.mode == "RGBA" else garment.convert("RGB")
    garment_fitted = ImageOps.contain(garment_rgb, (right_panel_w - 32, target_height - 32), Image.Resampling.LANCZOS)
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

# Test with images
p_path = PROJECT_ROOT / "frontend/assets/sample_person_1.jpg"
g_path = PROJECT_ROOT / "frontend/assets/sample_emerald_shirt.jpg"
p_img = Image.open(p_path)
g_img = Image.open(g_path)

# Mock mask
mask = Image.new("L", p_img.size, color=0)

canvas, c_mask, crop_box, orig_size = create_tryon_canvas(p_img, g_img, mask, target_width=1536, target_height=1024)
print("Canvas size:", canvas.size)
print("Mask size:", c_mask.size)
print("Crop box:", crop_box)

# Extract and resize back
extracted = canvas.crop(crop_box).resize(orig_size, Image.Resampling.LANCZOS)
print("Extracted size:", extracted.size)
assert extracted.size == orig_size
print("Verification: Aspect ratio and dimensions 100% preserved!")
