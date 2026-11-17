import sys
import os
import torch
from PIL import Image, ImageDraw

# Enforce strict determinism for reproducibility
SEED = 42
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

sys.path.append(os.path.abspath('src/models/CatVTON'))
from model.pipeline import CatVTONPipeline

device = 'cuda' if torch.cuda.is_available() else 'cpu'
weight_dtype = torch.bfloat16 if device == 'cuda' else torch.float32

print(f"Initializing Deterministic Pipeline (SEED={SEED}, DEVICE={device.upper()})...")
pipeline = CatVTONPipeline(
    base_ckpt="runwayml/stable-diffusion-inpainting",
    attn_ckpt="zhengchong/CatVTON",
    attn_ckpt_version="mix",
    weight_dtype=weight_dtype,
    use_tf32=(device == 'cuda'),  
    device=device,
    skip_safety_check=True
)

# Load the real images
person = Image.open('data/benchmark/person/person_1.jpg').convert('RGB').resize((768, 1024))
garment = Image.open('data/benchmark/garment/garment_1.jpg').convert('RGB').resize((768, 1024))

# Create a synthetic mask targeting the upper body
mask = Image.new('L', (768, 1024), color=0)
draw = ImageDraw.Draw(mask)
draw.rectangle([200, 300, 568, 800], fill=255)

generator = torch.Generator(device=device).manual_seed(SEED)
steps = int(os.getenv("STEPS", "40"))

print(f"Running generation ({steps} steps) on {device.upper()}...")
result_image = pipeline(
    person,
    garment,
    mask,
    num_inference_steps=steps,
    guidance_scale=2.5,
    generator=generator
)[0]

output_path = sys.argv[1] if len(sys.argv) > 1 else 'outputs/repro_result.jpg'
os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
result_image.save(output_path)
print(f"Saved reproducible output to {output_path}\n")
