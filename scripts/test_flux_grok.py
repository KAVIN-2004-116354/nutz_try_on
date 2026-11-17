import sys
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path("/home/lenovo/try_on")
sys.path.append(str(PROJECT_ROOT))

from src.inference.grok_vision import grok_vision_analyze

g_pil = Image.open(PROJECT_ROOT / "frontend/assets/sample_emerald_shirt.jpg")
p_pil = Image.open(PROJECT_ROOT / "frontend/assets/sample_person_1.jpg")

res = grok_vision_analyze(g_pil, p_pil, garment_name="sample_emerald_shirt.jpg")
print("Detected Primary Color:", res["garment_analysis"]["primary_color"])
print("Detected Pattern:", res["garment_analysis"]["pattern"])
print("\n--- GENERATION PROMPT (Snippet) ---")
print(res["generation_prompt"][:400])
print("\n--- ATTRIBUTES LINE IN PROMPT ---")
for line in res["generation_prompt"].split("\n"):
    if "REFERENCE GARMENT VISUAL ATTRIBUTES" in line or "color:" in line:
        print(line)
