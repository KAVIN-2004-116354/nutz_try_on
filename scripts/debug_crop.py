from PIL import Image
import numpy as np
import sys
sys.path.append("/home/lenovo/try_on")

p = Image.open("/home/lenovo/try_on/frontend/assets/sample_person_1.jpg").convert("RGB")
g = Image.open("/home/lenovo/try_on/frontend/assets/sample_emerald_shirt.jpg").convert("RGB")

from src.inference.cloud_generator import create_tryon_canvas
c, m, b, s = create_tryon_canvas(p, g, None)
print("Crop box:", b)
print("Canvas size:", c.size)
p_cropped = c.crop(b)
print("Cropped size:", p_cropped.size)
p_rec = p_cropped.resize(s, Image.Resampling.LANCZOS)
print("p_rec size:", p_rec.size, "p size:", p.size)

diff = np.mean(np.abs(np.array(p_rec, dtype=float) - np.array(p, dtype=float)))
print("Pixel diff between downscaled+upscaled and original:", diff)

# Save images to inspect
p.save("/home/lenovo/try_on/outputs/test_canvas/p_orig.png")
p_rec.save("/home/lenovo/try_on/outputs/test_canvas/p_rec.png")
