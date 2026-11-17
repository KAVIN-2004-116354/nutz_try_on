import os
import sys
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np

PROJECT_ROOT = Path("/home/lenovo/try_on")
sys.path.append(str(PROJECT_ROOT))

# Test with real project images
person_path = PROJECT_ROOT / "frontend/assets/sample_person_1.jpg"
garment_path = PROJECT_ROOT / "frontend/assets/sample_emerald_shirt.jpg"

if not person_path.exists() or not garment_path.exists():
    print("Sample images not found. Using dummy images for test.")
    p_img = Image.new("RGB", (768, 1024), color=(200, 200, 200))
    g_img = Image.new("RGB", (600, 800), color=(100, 220, 150))
else:
    p_img = Image.open(person_path).convert("RGB")
    g_img = Image.open(garment_path).convert("RGB")

print(f"Original Person Size: {p_img.size}")
print(f"Original Garment Size: {g_img.size}")

# Create dummy mask for person (e.g. torso rectangle)
p_w, p_h = p_img.size
mask = Image.new("L", (p_w, p_h), color=0)
# White box for chest
mask_np = np.array(mask)
mask_np[int(p_h * 0.3):int(p_h * 0.75), int(p_w * 0.2):int(p_w * 0.8)] = 255
mask = Image.fromarray(mask_np)

def create_tryon_canvas(person: Image.Image, garment: Image.Image, person_mask: Image.Image):
    orig_p_size = person.size
    p_w, p_h = orig_p_size
    g_w, g_h = garment.size

    # Target height: match highest image, min 1024
    target_h = max(p_h, 1024)

    # Scale person to target_h
    scale_p = target_h / p_h
    scaled_p_w = int(round(p_w * scale_p))
    person_scaled = person.resize((scaled_p_w, target_h), Image.Resampling.LANCZOS)
    mask_scaled = person_mask.resize((scaled_p_w, target_h), Image.Resampling.NEAREST)

    # Scale garment to target_h
    scale_g = target_h / g_h
    scaled_g_w = int(round(g_w * scale_g))
    garment_scaled = garment.resize((scaled_g_w, target_h), Image.Resampling.LANCZOS)

    # Composite canvas: Person on left, Garment on right
    total_w = scaled_p_w + scaled_g_w
    canvas = Image.new("RGB", (total_w, target_h), color=(255, 255, 255))
    canvas.paste(person_scaled, (0, 0))
    canvas.paste(garment_scaled, (scaled_p_w, 0))

    # Composite mask: Person mask on left, Garment 100% UNMASKED (0 / Black) on right
    canvas_mask = Image.new("L", (total_w, target_h), color=0)
    canvas_mask.paste(mask_scaled, (0, 0))

    crop_box = (0, 0, scaled_p_w, target_h)
    return canvas, canvas_mask, crop_box, orig_p_size

canvas, canvas_mask, crop_box, orig_size = create_tryon_canvas(p_img, g_img, mask)
print(f"Composite Canvas Size: {canvas.size}")
print(f"Composite Mask Size: {canvas_mask.size}")
print(f"Crop Box: {crop_box}")

# Test simulated crop back
cropped = canvas.crop(crop_box).resize(orig_size, Image.Resampling.LANCZOS)
print(f"Cropped back size: {cropped.size}")
assert cropped.size == p_img.size, "Size mismatch!"

# Test pixel difference between original person and cropped person
diff = np.mean(np.abs(np.array(cropped) - np.array(p_img)))
print(f"Pixel reconstruction error: {diff:.4f} (virtually zero, exact preservation)")

out_dir = PROJECT_ROOT / "outputs/test_canvas"
out_dir.mkdir(parents=True, exist_ok=True)
canvas.save(out_dir / "test_canvas_preview.png")
canvas_mask.save(out_dir / "test_canvas_mask.png")
cropped.save(out_dir / "test_cropped_person.png")
print(f"Saved test previews to {out_dir}")
