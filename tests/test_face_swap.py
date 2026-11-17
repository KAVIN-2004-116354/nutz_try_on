import io
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from src.gateway.app import app
from src.inference.face_swap import get_face_swap_engine

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_USER_FACE = PROJECT_ROOT / "frontend/assets/sample_person_female.jpg"
SAMPLE_GARMENT_MODEL = PROJECT_ROOT / "frontend/assets/sample_ethnic_anarkali_model.jpg"

client = TestClient(app)


def _blank_image_bytes(color="white", size=(256, 256)) -> io.BytesIO:
    buf = io.BytesIO()
    Image.new("RGB", size, color=color).save(buf, format="JPEG")
    buf.seek(0)
    return buf


def test_health_exposes_faceswap_ready():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["faceswap_ready"] is True


def test_face_swap_engine_preserves_garment_size_and_swaps_face():
    assert SAMPLE_USER_FACE.exists()
    assert SAMPLE_GARMENT_MODEL.exists()

    user_img = Image.open(SAMPLE_USER_FACE).convert("RGB")
    garment_img = Image.open(SAMPLE_GARMENT_MODEL).convert("RGB")

    engine = get_face_swap_engine()
    result = engine.swap(user_face_img=user_img, garment_model_img=garment_img)

    assert result["status"] == "success"
    swapped = result["tryon_image"]
    assert swapped.size == garment_img.size

    # Swapped output must differ from original where head/skin changed,
    # while leaving torso/skirt garment fabric unchanged.
    orig_arr = np.asarray(garment_img, dtype=np.int16)
    swap_arr = np.asarray(swapped, dtype=np.int16)
    diff = np.abs(orig_arr - swap_arr)
    assert diff.mean() > 0.1

    skirt_band_top = int(orig_arr.shape[0] * 0.66)
    skirt_band_bot = int(orig_arr.shape[0] * 0.82)
    assert np.allclose(
        orig_arr[skirt_band_top:skirt_band_bot],
        swap_arr[skirt_band_top:skirt_band_bot],
        atol=2,
    )


def test_face_swap_engine_rejects_no_face():
    engine = get_face_swap_engine()
    garment_img = Image.open(SAMPLE_GARMENT_MODEL).convert("RGB")
    blank = Image.new("RGB", (256, 256), color="white")

    with pytest.raises(ValueError, match="face"):
        engine.swap(user_face_img=blank, garment_model_img=garment_img)


def test_try_on_endpoint_with_face_swap_engine():
    with open(SAMPLE_USER_FACE, "rb") as f_p, open(SAMPLE_GARMENT_MODEL, "rb") as f_g:
        response = client.post(
            "/api/v1/try-on",
            files={
                "person_image": ("face.jpg", f_p, "image/jpeg"),
                "garment_image": ("model.jpg", f_g, "image/jpeg"),
            },
            data={"engine": "face_swap", "domain": "indian_ethnic", "seed": "42"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["mode"] == "face_swap"
    assert "InsightFace" in payload["used_weights"]
    assert payload["image_data"].startswith("data:image/png;base64,")
    assert payload["result_url"].startswith("/outputs/gateway_faceswap_")


def test_dedicated_face_swap_endpoint_and_422_on_missing_face():
    with open(SAMPLE_USER_FACE, "rb") as f_p, open(SAMPLE_GARMENT_MODEL, "rb") as f_g:
        ok_resp = client.post(
            "/api/v1/face-swap",
            files={
                "person_image": ("face.jpg", f_p, "image/jpeg"),
                "garment_image": ("model.jpg", f_g, "image/jpeg"),
            },
            data={"domain": "western", "seed": "7"},
        )
    assert ok_resp.status_code == 200
    assert ok_resp.json()["mode"] == "face_swap"

    with open(SAMPLE_GARMENT_MODEL, "rb") as f_g:
        bad_resp = client.post(
            "/api/v1/face-swap",
            files={
                "person_image": ("blank.jpg", _blank_image_bytes(), "image/jpeg"),
                "garment_image": ("model.jpg", f_g, "image/jpeg"),
            },
        )
    assert bad_resp.status_code == 422
    assert "face" in bad_resp.json()["detail"].lower()


def test_men_full_head_swap_replaces_head_and_preserves_kurta():
    user_path = PROJECT_ROOT / "frontend/assets/sample_men_beard.jpg"
    garment_path = PROJECT_ROOT / "frontend/assets/garments/m_01_model.jpg"
    assert user_path.exists()
    assert garment_path.exists()

    user_img = Image.open(user_path).convert("RGB")
    garment_img = Image.open(garment_path).convert("RGB")
    result = get_face_swap_engine().swap(user_face_img=user_img, garment_model_img=garment_img)

    assert result["status"] == "success"
    assert "HeadSwap" in result["lora_checkpoint_used"]
    swapped = result["tryon_image"]
    assert swapped.size == garment_img.size

    orig_arr = np.asarray(garment_img, dtype=np.int16)
    swap_arr = np.asarray(swapped, dtype=np.int16)
    top_head = np.abs(orig_arr[: int(orig_arr.shape[0] * 0.25)] - swap_arr[: int(orig_arr.shape[0] * 0.25)])
    assert top_head.mean() > 1.0

    kurta_top = int(orig_arr.shape[0] * 0.56)
    kurta_bot = int(orig_arr.shape[0] * 0.88)
    assert np.allclose(orig_arr[kurta_top:kurta_bot], swap_arr[kurta_top:kurta_bot], atol=2)


def test_cross_skin_tone_adapts_garment_neck_and_hands_to_person():
    user_path = PROJECT_ROOT / "frontend/assets/sample_men_beard.jpg"
    pale_model_path = PROJECT_ROOT / "frontend/assets/garments/mm_06.jpg"
    assert user_path.exists()
    assert pale_model_path.exists()

    user_img = Image.open(user_path).convert("RGB")
    garment_img = Image.open(pale_model_path).convert("RGB")
    result = get_face_swap_engine().swap(user_face_img=user_img, garment_model_img=garment_img)
    assert result["status"] == "success"

    orig_arr = np.asarray(garment_img, dtype=np.float32)
    swap_arr = np.asarray(result["tryon_image"], dtype=np.float32)
    h, w = orig_arr.shape[:2]

    # Pale model neck beneath chin (around 21%..24% height, 45%..55% width) should darken to match user skin
    neck_orig = orig_arr[int(h * 0.21) : int(h * 0.24), int(w * 0.45) : int(w * 0.55)].mean()
    neck_swap = swap_arr[int(h * 0.21) : int(h * 0.24), int(w * 0.45) : int(w * 0.55)].mean()
    assert neck_orig - neck_swap > 25.0

    # Vest/trouser torso block around center should stay untouched
    vest_orig = orig_arr[int(h * 0.45) : int(h * 0.70), int(w * 0.35) : int(w * 0.65)]
    vest_swap = swap_arr[int(h * 0.45) : int(h * 0.70), int(w * 0.35) : int(w * 0.65)]
    assert np.allclose(vest_orig, vest_swap, atol=2)


def test_all_frontend_sample_assets_exist_on_disk():
    html_text = (PROJECT_ROOT / "frontend/index.html").read_text(encoding="utf-8")
    js_text = (PROJECT_ROOT / "frontend/app.js").read_text(encoding="utf-8")
    import re

    refs = set(re.findall(r'assets/[A-Za-z0-9_./-]+\.(?:jpg|jpeg|png|webp)', html_text + "\n" + js_text))
    catalog_ids = re.findall(r'\["(\d{2})",\s*"[^"]+",\s*"[^"]+",\s*"(?:full_body|upper_body|lower_body)"\]', js_text)
    for gid in catalog_ids:
        refs.add(f"assets/garments/g_{gid}_model.jpg")
        refs.add(f"assets/garments/g_{gid}_cloth.jpg")
    assert len(refs) >= 100
    missing = [rel for rel in sorted(refs) if not (PROJECT_ROOT / "frontend" / rel).exists()]
    assert missing == [], f"Missing referenced frontend assets: {missing}"

