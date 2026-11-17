import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DatasetAnnotator")

def initialize_annotation_pipeline():
    logger.info("Initializing Custom Pose & Garment Auto-Isolation Pipeline...")
    logger.info("Hooking into existing modules: SegFormer (fashion parsing) & MediaPipe (3D pose).")
    
    # Target directories for custom annotated dataset
    custom_dir = Path("datasets/custom_pose")
    for sub in ["image", "cloth", "cloth_mask", "agnostic_mask", "image_parse"]:
        (custom_dir / sub).mkdir(parents=True, exist_ok=True)
        
    logger.info("Dataset directories for custom pipeline successfully verified/created at datasets/custom_pose/")

if __name__ == "__main__":
    initialize_annotation_pipeline()
