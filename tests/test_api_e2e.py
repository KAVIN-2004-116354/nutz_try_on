import pytest
import os
import io
import base64
import urllib.request
from fastapi.testclient import TestClient
from PIL import Image
from main import app

client = TestClient(app)

PERSON_SAMPLE = "/home/lenovo/try_on/frontend/assets/sample_person_1.jpg"
GARMENT_SAMPLE = "/home/lenovo/try_on/frontend/assets/sample_emerald_shirt.jpg"

def is_comfyui_online():
    try:
        with urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False

def test_e2e_real_try_on_api():
    if not is_comfyui_online():
        pytest.skip("ComfyUI server (http://127.0.0.1:8188) is not running; skipping live generation test.")

    print("\n--- [E2E TEST] POST /api/v1/try-on Real Inference ---")
    assert os.path.exists(PERSON_SAMPLE), f"Missing {PERSON_SAMPLE}"
    assert os.path.exists(GARMENT_SAMPLE), f"Missing {GARMENT_SAMPLE}"

    with open(PERSON_SAMPLE, "rb") as fp, open(GARMENT_SAMPLE, "rb") as fg:
        files = {
            "person_image": ("person.jpg", fp.read(), "image/jpeg"),
            "garment_image": ("garment.jpg", fg.read(), "image/jpeg"),
        }
    
    data = {
        "steps": "15",
        "category": "upper_body"
    }

    # Execute request through FastAPI
    response = client.post("/api/v1/try-on?format=json", files=files, data=data)
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    result = response.json()
    assert result.get("status") == "success"
    assert "result_url" in result
    assert "image_data" in result
    assert "latency_seconds" in result
    assert "category" in result
    print(f"Latency: {result['latency_seconds']}s, Category: {result['category']}")

    # Validate returned base64 image
    img_b64 = result["image_data"]
    assert img_b64.startswith("data:image/png;base64,"), "image_data should be data URI PNG"
    raw_b64 = img_b64.replace("data:image/png;base64,", "")
    img_bytes = base64.b64decode(raw_b64)
    assert len(img_bytes) > 20000, f"Image bytes too small: {len(img_bytes)}"

    # Decode and check dimensions
    img = Image.open(io.BytesIO(img_bytes))
    print(f"Output Image Dimensions: {img.size}, Mode: {img.mode}")
    assert img.size[0] > 0 and img.size[1] > 0
    assert img.mode == "RGB" or img.mode == "RGBA"

    # Verify not blank
    extrema = img.getextrema()
    for ch_min, ch_max in extrema:
        assert ch_max > ch_min, "Output image is blank"

    # Verify saved artifact in outputs
    out_file = "/home/lenovo/try_on/outputs/nutz_tryon_latest.png"
    assert os.path.exists(out_file), f"Output file missing: {out_file}"
    print(f"Verified output file on disk: {out_file} ({os.path.getsize(out_file)} bytes)")
    print("--- [PASS] End-to-End Real Try-On API Test Succeeded! ---")

