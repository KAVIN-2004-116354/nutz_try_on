import sys
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path("/home/lenovo/try_on")
sys.path.append(str(PROJECT_ROOT))
from src.inference.catvton_pipeline_manager import run_direct_catvton

p = Image.open(PROJECT_ROOT / "frontend/assets/sample_person_1.jpg")
g = Image.open(PROJECT_ROOT / "frontend/assets/sample_emerald_shirt.jpg")
res = run_direct_catvton(p, g, category="shirt", steps=5)
print("Direct CatVTON success! Time:", res["inference_time_ms"])
