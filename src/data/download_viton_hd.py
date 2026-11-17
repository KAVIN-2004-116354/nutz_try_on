import os

print("=== VITON-HD Dataset Acquisition Helper ===")
print("Project path: /home/lenovo/try_on")
print("Target directory: datasets/viton_hd")

# Ensure target directories exist
os.makedirs("datasets/viton_hd/train", exist_ok=True)
os.makedirs("datasets/viton_hd/test", exist_ok=True)

print("Directory structure ready. Ready for archive extraction.")
