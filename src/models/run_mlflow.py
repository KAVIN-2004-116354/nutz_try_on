import sys
import os
import torch
import mlflow
from PIL import Image, ImageDraw

# Configure MLflow to use a local SQLite database for tracking
mlflow.set_tracking_uri("sqlite:///mlruns.db")
mlflow.set_experiment("CatVTON_Baseline")

sys.path.append(os.path.abspath('src/models/CatVTON'))
from model.pipeline import CatVTONPipeline

# Define hyperparameters
SEED = 42
STEPS = 40
GUIDANCE = 2.5

print("Starting MLflow Run...")
with mlflow.start_run(run_name="baseline_reproducible_run"):
    # Log parameters to the MLflow database
    mlflow.log_param("seed", SEED)
    mlflow.log_param("inference_steps", STEPS)
    mlflow.log_param("guidance_scale", GUIDANCE)
    mlflow.log_param("model", "CatVTON")

    # Enforce determinism
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    pipeline = CatVTONPipeline(
        base_ckpt="runwayml/stable-diffusion-inpainting",
        attn_ckpt="zhengchong/CatVTON",
        attn_ckpt_version="mix",
        weight_dtype=torch.bfloat16,
        use_tf32=False,
        device='cuda'
    )

    person = Image.open('data/benchmark/person/person_1.jpg').convert('RGB').resize((768, 1024))
    garment = Image.open('data/benchmark/garment/garment_1.jpg').convert('RGB').resize((768, 1024))
    
    mask = Image.new('L', (768, 1024), color=0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle([200, 300, 568, 800], fill=255)

    generator = torch.Generator(device='cuda').manual_seed(SEED)

    print("Running generation...")
    result_image = pipeline(
        person, garment, mask,
        num_inference_steps=STEPS,
        guidance_scale=GUIDANCE,
        generator=generator
    )[0]

    output_path = 'outputs/mlflow_result.jpg'
    result_image.save(output_path)
    
    # Log the resulting image as an MLflow artifact
    mlflow.log_artifact(output_path, "generated_images")
    
    print("\n--- MLflow Tracking Complete ---")
    print(f"Artifacts and metrics saved to MLflow database.")
