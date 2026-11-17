import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from src.gateway.app import app, DOMAIN_CHECKPOINTS

client = TestClient(app)

def create_dummy_image(color="blue", size=(200, 200), fmt="JPEG"):
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf

def test_gateway_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "indian_ethnic" in data["supported_domains"]
    assert "western" in data["supported_domains"]

def test_gateway_domains():
    response = client.get("/v1/domains")
    assert response.status_code == 200
    data = response.json()
    domain_ids = [d["id"] for d in data["domains"]]
    assert "indian_ethnic" in domain_ids
    assert "western" in domain_ids

def test_try_on_indian_domain():
    p_buf = create_dummy_image(color="orange", size=(768, 1024))
    g_buf = create_dummy_image(color="red", size=(768, 1024))
    
    files = {
        "person_image": ("person.jpg", p_buf, "image/jpeg"),
        "garment_image": ("garment.jpg", g_buf, "image/jpeg")
    }
    data = {
        "domain": "indian_ethnic",
        "category": "full_body",
        "steps": "20"
    }
    
    response = client.post("/v1/try-on", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "success"
    assert res["domain"] == "indian_ethnic"
    assert "catvton_lora_indian_ethnic_rtx5050.safetensors" in res["selected_lora"]
    assert "image_data" in res
    assert "result_url" in res

def test_try_on_western_domain():
    p_buf = create_dummy_image(color="gray", size=(768, 1024))
    g_buf = create_dummy_image(color="navy", size=(768, 1024))
    
    files = {
        "person_image": ("person.jpg", p_buf, "image/jpeg"),
        "garment_image": ("garment.jpg", g_buf, "image/jpeg")
    }
    data = {
        "domain": "western",
        "category": "upper_body",
        "steps": "20"
    }
    
    response = client.post("/v1/try-on", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "success"
    assert res["domain"] == "western"
    assert "catvton_lora_rtx5050_extended.safetensors" in res["selected_lora"]
    assert "image_data" in res
    assert "result_url" in res

