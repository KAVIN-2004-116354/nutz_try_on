import sys
import os
import time
import torch
from PIL import Image, ImageDraw

# Add CatVTON to the Python path so we can import their custom pipeline directly
sys.path.append(os.path.abspath('src/models/CatVTON'))

from model.pipeline import CatVTONPipeline
from utils import init_weight_dtype

print("Initializing CatVTON Pipeline (this will download model weights ~5GB)...")
pipeline = CatVTONPipeline(
    base_ckpt="runwayml/stable-diffusion-inpainting",
    attn_ckpt="zhengchong/CatVTON",
    attn_ckpt_version="mix",
    weight_dtype=torch.bfloat16,
    use_tf32=True,
    device='cuda'
)

print("Loading synthetic benchmark images...")
person = Image.open('data/benchmark/person/person_1.jpg').convert('RGB').resize((768, 1024))
garment = Image.open('data/benchmark/garment/garment_1.jpg').convert('RGB').resize((768, 1024))

# Create a synthetic mask (bypassing the need for a heavy Detectron2 installation)
# A white rectangle represents the area where the model is allowed to generate the new clothing
mask = Image.new('L', (768, 1024), color=0)
draw = ImageDraw.Draw(mask)
draw.rectangle([200, 300, 568, 800], fill=255)

print("Running baseline inference...")
torch.cuda.reset_peak_memory_stats()
start_time = time.time()

# Run the model forward pass
result_image = pipeline(
    person,
    garment,
    mask,
    num_inference_steps=40,
    guidance_scale=2.5
)[0]

end_time = time.time()
peak_memory = torch.cuda.max_memory_allocated() / (1024**3)

result_image.save('outputs/baseline_result.jpg')

print("\n--- Baseline Run Complete ---")
print(f"Runtime: {end_time - start_time:.2f} seconds")
print(f"Peak VRAM: {peak_memory:.2f} GB")
print("Output saved to outputs/baseline_result.jpg")
