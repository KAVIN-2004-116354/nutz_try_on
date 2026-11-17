import os
import sys
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

key = os.getenv("IMAGE_API_KEY")
base_url = os.getenv("IMAGE_API_BASE_URL", "https://nutz-image1284.up.railway.app").rstrip("/")
model = "FLUX-DEV-012"

print(f"API Base URL: {base_url}")
print(f"Model: {model}")
print(f"API Key present: {bool(key)}")

# Test 1: Image Edit Endpoint
edit_url = f"{base_url}/v1/images/edits"
img_path = PROJECT_ROOT / "frontend/assets/sample_person_female.jpg"

if img_path.exists():
    with open(img_path, "rb") as f:
        img_bytes = f.read()

    files = {"image": ("person.jpg", img_bytes, "image/jpeg")}
    data = {
        "prompt": "Indian woman wearing a luxurious green silk anarkali suit with gold zari embroidery, photorealistic",
        "model": model,
        "response_format": "b64_json"
    }
    print(f"\n[Test 1] Testing /v1/images/edits with input image ({len(img_bytes)} bytes)...")
    try:
        resp = requests.post(edit_url, headers={"Authorization": f"Bearer {key}"}, files=files, data=data, timeout=30)
        print(f"Edit endpoint HTTP status: {resp.status_code}")
        print(f"Edit endpoint response text: {resp.text[:300]}")
    except Exception as e:
        print(f"Edit endpoint error: {e}")

# Test 2: Text-to-Image Generation (Flux.1 Dev Synthesizer)
gen_url = f"{base_url}/v1/images/generations"
gen_payload = {
    "prompt": "Full-body professional fashion photography of an Indian woman model wearing a luxurious green silk anarkali suit with gold embroidery, clean studio background, 8k resolution, highly detailed, photorealistic, masterpiece",
    "model": model,
    "size": "1024x1024",
    "response_format": "b64_json"
}
print(f"\n[Test 2] Testing /v1/images/generations (1024x1024)...")
try:
    resp = requests.post(gen_url, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, json=gen_payload, timeout=60)
    print(f"Generations endpoint HTTP status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        item = data["data"][0]
        b64 = item.get("b64_json", "")
        print(f"Success! Received base64 image length: {len(b64)}")
        out_file = PROJECT_ROOT / "outputs/flux_dev_test_tryon.png"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "wb") as f:
            f.write(base64.b64decode(b64))
        print(f"Saved test output image to {out_file}")
    else:
        print(f"Generations error: {resp.text[:300]}")
except Exception as e:
    print(f"Generations exception: {e}")
