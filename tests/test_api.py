import pytest
import os
import io
from fastapi.testclient import TestClient
from PIL import Image

# Import app from main
from main import app

client = TestClient(app)

def create_dummy_image(color="blue", size=(100, 100), fmt="JPEG"):
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "comfyui_backend" in data
    assert "version" in data
    print("Health response:", data)

def test_analytics_endpoint():
    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "successful_renders" in data
    assert "average_latency_seconds" in data
    assert "success_rate" in data
    print("Analytics response:", data)

def test_classify_garment_endpoint():
    img_buf = create_dummy_image(color="green", size=(400, 500))
    files = {"garment_image": ("test_shirt.jpg", img_buf, "image/jpeg")}
    response = client.post("/api/v1/classify-garment", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "category" in data
    assert "mask_flags" in data
    assert isinstance(data["mask_flags"], dict)
    print("Classification response category:", data["category"])

def test_classify_garment_missing_file():
    response = client.post("/api/v1/classify-garment")
    assert response.status_code == 422 # Unprocessable Entity for missing required file

def test_try_on_missing_files():
    response = client.post("/api/v1/try-on")
    assert response.status_code == 422 # Validation error for missing files

def test_try_on_invalid_image_handling():
    # Sending text file as image
    files = {
        "person_image": ("bad.txt", io.BytesIO(b"not an image"), "text/plain"),
        "garment_image": ("bad2.txt", io.BytesIO(b"not an image"), "text/plain"),
    }
    response = client.post("/api/v1/try-on", files=files)
    # Backend should either reject with 400 or handle appropriately
    assert response.status_code in [400, 422, 500, 502]

from unittest.mock import patch

def test_try_on_swagger_default_category_not_rejected():
    # When Swagger UI passes default placeholder "string", backend should not reject with 400 Invalid category
    img1 = create_dummy_image(color="blue", size=(100, 100))
    img2 = create_dummy_image(color="green", size=(100, 100))
    files = {
        "person_image": ("person.jpg", img1, "image/jpeg"),
        "garment_image": ("garment.jpg", img2, "image/jpeg"),
    }
    data = {"category": "string"}
    
    # Mock queue_prompt so we test validation & preprocessing without running 40s diffusion in unit tests
    with patch("main.queue_prompt", side_effect=RuntimeError("Mock dispatch intercepted")):
        response = client.post("/api/v1/try-on", files=files, data=data)
        # Should proceed past category validation (not 400) and stop at ComfyUI dispatch (502)
        assert response.status_code == 502
        assert "Mock dispatch intercepted" in response.json().get("detail", "")

def test_classify_garment_returns_sleeve_type():
    img_buf = create_dummy_image(color="green", size=(400, 500))
    files = {"garment_image": ("test_shirt.jpg", img_buf, "image/jpeg")}
    response = client.post("/api/v1/classify-garment", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "sleeve_type" in data
    assert data["sleeve_type"] in ["sleeveless", "short_sleeve", "long_sleeve", "not_applicable"]

def test_skin_prior_module():
    from src.preprocessing.skin_prior import sample_skin_tone, apply_skin_hallucination_prior
    import tempfile
    
    # Create test person image with skin-colored face area
    buf = io.BytesIO()
    test_p = Image.new("RGB", (300, 400), color=(180, 150, 130))
    test_p.save(buf, format="JPEG")
    
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(buf.getvalue())
        temp_path = f.name
        
    try:
        skin = sample_skin_tone(temp_path)
        assert "rgb" in skin
        assert "bgr" in skin
        
        res = apply_skin_hallucination_prior(temp_path, "short_sleeve")
        assert res["status"] in ["applied", "bypassed"]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

