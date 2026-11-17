import os
import sys
import time
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path("/home/lenovo/try_on")
sys.path.append(str(PROJECT_ROOT))

from src.inference.engine import CatVTONLoRAEngine

person_path = PROJECT_ROOT / "frontend/assets/sample_person_1.jpg"
garment_path = PROJECT_ROOT / "frontend/assets/sample_emerald_shirt.jpg"

print(f"Loading person: {person_path} exists? {person_path.exists()}")
print(f"Loading garment: {garment_path} exists? {garment_path.exists()}")

p_img = Image.open(person_path)
g_img = Image.open(garment_path)

print(f"Person size: {p_img.size}, mode: {p_img.mode}")
print(f"Garment size: {g_img.size}, mode: {g_img.mode}")

print("\n--- Running CatVTONLoRAEngine on RTX 5050 Laptop GPU ---")
t0 = time.time()
engine = CatVTONLoRAEngine(domain="western")
res = engine.infer(p_img, g_img, domain="western")
t_elapsed = time.time() - t0

out_path = PROJECT_ROOT / "outputs/user_case_catvton_result.png"
res["tryon_image"].save(out_path)
print(f"SUCCESS in {t_elapsed:.2f}s!")
print(f"Inference time reported: {res.get('inference_time_ms')} ms")
print(f"Saved result to {out_path}")
