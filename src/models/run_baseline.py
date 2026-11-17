import sys
import os
import time
import torch
from PIL import Image, ImageDraw

# Add CatVTON to the Python path so we can import their custom pipeline directly
sys.path.append(os.path.abspath('src/models/CatVTON'))

from model.pipeline import CatVTONPipeline
from utils import init_weight_dtype

device = 'cuda' if torch.cuda.is_available() else 'cpu'
weight_dtype = torch.bfloat16 if device == 'cuda' else torch.float32

print(f"Initializing CatVTON Pipeline on {device.upper()} (this will download model weights ~5GB if not cached)...")
pipeline = CatVTONPipeline(
    base_ckpt="runwayml/stable-diffusion-inpainting",
    attn_ckpt="zhengchong/CatVTON",
    attn_ckpt_version="mix",
    weight_dtype=weight_dtype,
    use_tf32=(device == 'cuda'),
    device=device,
    skip_safety_check=True
)

print("Loading synthetic benchmark images...")
person = Image.open('data/benchmark/person/person_1.jpg').convert('RGB').resize((768, 1024))
garment = Image.open('data/benchmark/garment/garment_1.jpg').convert('RGB').resize((768, 1024))

# Create a synthetic mask (bypassing the need for a heavy Detectron2 installation)
# A white rectangle represents the area where the model is allowed to generate the new clothing
mask = Image.new('L', (768, 1024), color=0)
draw = ImageDraw.Draw(mask)
draw.rectangle([200, 300, 568, 800], fill=255)

steps = int(os.getenv("STEPS", "40"))
print(f"Running baseline inference ({steps} steps) on {device.upper()}...")
if torch.cuda.is_available():
    torch.cuda.reset_peak_memory_stats()
start_time = time.time()

# Run the model forward pass
result_image = pipeline(
    person,
    garment,
    mask,
    num_inference_steps=steps,
    guidance_scale=2.5
)[0]

end_time = time.time()
peak_memory = (torch.cuda.max_memory_allocated() / (1024**3)) if torch.cuda.is_available() else 0.0

os.makedirs('outputs', exist_ok=True)
result_image.save('outputs/baseline_result.jpg')

print("\n--- Baseline Run Complete ---")
print(f"Runtime: {end_time - start_time:.2f} seconds")
if torch.cuda.is_available():
    print(f"Peak VRAM: {peak_memory:.2f} GB")
else:
    print("Device: CPU (CUDA not detected)")
print("Output saved to outputs/baseline_result.jpg")
