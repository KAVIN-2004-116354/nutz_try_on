import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from src.gateway.app import app

client = TestClient(app)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_PERSON = str(PROJECT_ROOT / "datasets/indian_viton_hd/train/image/ind_00000.jpg")
SAMPLE_GARMENT = str(PROJECT_ROOT / "datasets/indian_viton_hd/train/cloth/ind_00000.jpg")

def test_gateway_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["engine_ready"] is True
    assert "indian_ethnic" in data["supported_domains"]
    assert "western" in data["supported_domains"]

def test_live_engine_tryon_indian_ethnic():
    payload = {
        "person_image": SAMPLE_PERSON,
        "garment_image": SAMPLE_GARMENT,
        "domain": "indian_ethnic",
        "seed": 42
    }
    resp = client.post("/v1/try-on", json=payload)
    assert resp.status_code == 200, f"Error {resp.status_code}: {resp.text}"
    data = resp.json()
    
    assert data["status"] == "success"
    assert data["domain"] == "indian_ethnic"
    assert "catvton_lora_indian_ethnic_rtx5050.safetensors" in data["used_weights"]
    assert data["num_lora_tensors"] == 64
    assert data["inference_time_ms"] > 0
    assert data["output_image"] is not None
    assert os.path.exists(data["output_image"])
    assert Path(data["output_image"]).stat().st_size > 10000
    print("\n[Indian Ethnic Test Result]")
    print(f"  Used Weights: {data['used_weights']}")
    print(f"  Inference Latency: {data['inference_time_ms']} ms")
    print(f"  Peak VRAM: {data['peak_vram_mb']} MB")
    print(f"  Output Image: {data['output_image']}")

def test_live_engine_tryon_western():
    payload = {
        "person_image": SAMPLE_PERSON,
        "garment_image": SAMPLE_GARMENT,
        "domain": "western",
        "seed": 100
    }
    resp = client.post("/v1/try-on", json=payload)
    assert resp.status_code == 200, f"Error {resp.status_code}: {resp.text}"
    data = resp.json()
    
    assert data["status"] == "success"
    assert data["domain"] == "western"
    assert "catvton_lora_rtx5050_extended.safetensors" in data["used_weights"]
    assert data["num_lora_tensors"] == 64
    assert data["inference_time_ms"] > 0
    assert data["output_image"] is not None
    assert os.path.exists(data["output_image"])
    assert Path(data["output_image"]).stat().st_size > 10000
    print("\n[Western Test Result]")
    print(f"  Used Weights: {data['used_weights']}")
    print(f"  Inference Latency: {data['inference_time_ms']} ms")
    print(f"  Peak VRAM: {data['peak_vram_mb']} MB")
    print(f"  Output Image: {data['output_image']}")

