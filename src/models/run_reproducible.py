import sys
import os
import torch
from PIL import Image, ImageDraw

# Enforce strict determinism for reproducibility
SEED = 42
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

sys.path.append(os.path.abspath('src/models/CatVTON'))
from model.pipeline import CatVTONPipeline

print(f"Initializing Deterministic Pipeline (SEED={SEED})...")
pipeline = CatVTONPipeline(
    base_ckpt="runwayml/stable-diffusion-inpainting",
    attn_ckpt="zhengchong/CatVTON",
    attn_ckpt_version="mix",
    weight_dtype=torch.bfloat16,
    use_tf32=False,  
    device='cuda'
)

# Load the real images
person = Image.open('data/benchmark/person/person_1.jpg').convert('RGB').resize((768, 1024))
garment = Image.open('data/benchmark/garment/garment_1.jpg').convert('RGB').resize((768, 1024))

# Create a synthetic mask targeting the upper body
mask = Image.new('L', (768, 1024), color=0)
draw = ImageDraw.Draw(mask)
draw.rectangle([200, 300, 568, 800], fill=255)

generator = torch.Generator(device='cuda').manual_seed(SEED)

print("Running generation...")
result_image = pipeline(
    person,
    garment,
    mask,
    num_inference_steps=40,
    guidance_scale=2.5,
    generator=generator
)[0]

output_path = sys.argv[1] if len(sys.argv) > 1 else 'outputs/repro_result.jpg'
result_image.save(output_path)
print(f"Saved reproducible output to {output_path}\n")
