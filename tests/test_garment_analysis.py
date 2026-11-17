import os
import io
import cv2
import numpy as np
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from main import app
from src.preprocessing.classifier import (
    classify_garment,
    analyze_garment_geometry,
    detect_lower_garment_type,
    detect_sleeve_length
)
from src.preprocessing.pose_target import (
    analyze_posture,
    compute_target_bounds,
    generate_target_aware_mask
)

client = TestClient(app)

def create_synthetic_lower_garment(garment_type="shorts", size=(400, 400)):
    """Creates synthetic flat-lay lower garment images for unit testing."""
    w, h = size
    img = np.full((h, w, 3), 255, dtype=np.uint8) # White background

    if garment_type == "shorts":
        # Draw two short leg columns with a central fork
        color = (50, 100, 180) # Denim blue
        # Waistband
        cv2.rectangle(img, (int(w * 0.25), int(h * 0.2)), (int(w * 0.75), int(h * 0.45)), color, -1)
        # Left leg
        cv2.rectangle(img, (int(w * 0.25), int(h * 0.45)), (int(w * 0.46), int(h * 0.75)), color, -1)
        # Right leg
        cv2.rectangle(img, (int(w * 0.54), int(h * 0.45)), (int(w * 0.75), int(h * 0.75)), color, -1)
    elif garment_type == "pants":
        # Draw long trousers
        color = (30, 30, 40)
        cv2.rectangle(img, (int(w * 0.3), int(h * 0.1)), (int(w * 0.7), int(h * 0.3)), color, -1)
        # Left leg down to bottom
        cv2.rectangle(img, (int(w * 0.3), int(h * 0.3)), (int(w * 0.47), int(h * 0.95)), color, -1)
        # Right leg down to bottom
        cv2.rectangle(img, (int(w * 0.53), int(h * 0.3)), (int(w * 0.7), int(h * 0.95)), color, -1)
    elif garment_type == "skirt":
        # Solid A-line skirt with no central split
        color = (180, 50, 80)
        pts = np.array([
            [int(w * 0.35), int(h * 0.25)],
            [int(w * 0.65), int(h * 0.25)],
            [int(w * 0.85), int(h * 0.85)],
            [int(w * 0.15), int(h * 0.85)]
        ], np.int32)
        cv2.fillPoly(img, [pts], color)

    buf = io.BytesIO()
    Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).save(buf, format="JPEG")
    buf.seek(0)
    return buf, img


def test_tshirt_classification():
    path = "frontend/assets/sample_black_tshirt.jpg"
    if os.path.exists(path):
        res = classify_garment(path)
        assert res["category"] == "upper_body"
        assert res["sleeve_type"] == "short_sleeve"
        assert res["sub_type"] == "t_shirt"
        assert res["target_region"] == "torso_and_biceps"
        assert res["dominant_color"]["is_dark"] is True
        # Verify Kurta / Layered tunic fix: dress and coat must be True for upper body
        assert res["mask_flags"]["dress"] is True
        assert res["mask_flags"]["coat"] is True
        assert res["mask_flags"]["shirt"] is True
        assert res["mask_flags"]["vest"] is True
        assert res["mask_flags"]["sleeve"] is True


def test_long_sleeve_classification():
    path = "frontend/assets/green_shirt.jpg"
    if os.path.exists(path):
        res = classify_garment(path)
        assert res["category"] == "upper_body"
        assert res["sleeve_type"] == "long_sleeve"
        assert res["sub_type"] == "shirt"
        assert res["target_region"] == "full_upper"


def test_synthetic_shorts_detection():
    buf, img = create_synthetic_lower_garment("shorts", size=(400, 350))
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(buf.getvalue())
        tmp_path = f.name

    try:
        res = classify_garment(tmp_path, category_override="lower_body")
        assert res["category"] == "lower_body"
        assert res["lower_type"] == "shorts"
        assert res["sub_type"] == "shorts"
        assert res["target_region"] == "waist_to_knee"
        assert res["mask_flags"]["shorts"] is True
        assert res["mask_flags"]["pants"] is True
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_synthetic_pants_detection():
    buf, img = create_synthetic_lower_garment("pants", size=(300, 600))
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(buf.getvalue())
        tmp_path = f.name

    try:
        res = classify_garment(tmp_path, category_override="lower_body")
        assert res["category"] == "lower_body"
        assert res["lower_type"] == "pants"
        assert res["sub_type"] == "pants"
        assert res["target_region"] == "waist_to_ankle"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_synthetic_skirt_detection():
    buf, img = create_synthetic_lower_garment("skirt", size=(400, 400))
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(buf.getvalue())
        tmp_path = f.name

    try:
        res = classify_garment(tmp_path, category_override="lower_body")
        assert res["category"] == "lower_body"
        assert res["lower_type"] == "skirt"
        assert res["sub_type"] == "skirt"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_posture_landmark_detection():
    path = "frontend/assets/sample_person_1.jpg"
    if os.path.exists(path):
        posture = analyze_posture(path)
        assert "landmarks" in posture
        lm = posture["landmarks"]
        # Assert strict vertical anatomical ordering
        assert lm["y_head"] < lm["y_neck"]
        assert lm["y_neck"] < lm["y_shoulder"]
        assert lm["y_shoulder"] < lm["y_chest"]
        assert lm["y_chest"] < lm["y_elbow"]
        assert lm["y_elbow"] < lm["y_waist"]
        assert lm["y_waist"] < lm["y_knee"]
        assert lm["y_knee"] < lm["y_ankle"]


def test_target_bounds_calculation():
    posture = {
        "landmarks": {
            "y_head": 50,
            "y_neck": 120,
            "y_shoulder": 180,
            "y_chest": 280,
            "y_elbow": 380,
            "y_waist": 480,
            "y_wrist": 550,
            "y_knee": 720,
            "y_ankle": 900
        }
    }
    # 1. Shorts bounds
    shorts_bounds = compute_target_bounds(posture, {"category": "lower_body", "sub_type": "shorts"})
    assert shorts_bounds["y_top"] == 480 # waist
    assert shorts_bounds["y_bottom"] == 720 # knee
    assert shorts_bounds["bare_skin_zone"] == "lower_legs"

    # 2. T-shirt bounds
    tshirt_bounds = compute_target_bounds(posture, {"category": "upper_body", "sub_type": "t_shirt", "sleeve_type": "short_sleeve"})
    assert tshirt_bounds["y_top"] == 180 # shoulder
    assert tshirt_bounds["y_bottom"] == 480 # waist
    assert tshirt_bounds["arm_cutoff"] == 380 # elbow
    assert tshirt_bounds["bare_skin_zone"] == "forearms"


def test_api_classify_garment_full_metadata():
    path = "frontend/assets/sample_black_tshirt.jpg"
    if os.path.exists(path):
        with open(path, "rb") as f:
            files = {"garment_image": ("sample_black_tshirt.jpg", f, "image/jpeg")}
            res = client.post("/api/v1/classify-garment", files=files)
        assert res.status_code == 200
        data = res.json()
        assert "category" in data
        assert "sub_type" in data
        assert "sleeve_type" in data
        assert "lower_type" in data
        assert "target_region" in data
        assert "aspect_ratio" in data
        assert "dominant_color" in data


def test_api_analyze_posture_endpoint():
    path = "frontend/assets/sample_person_1.jpg"
    if os.path.exists(path):
        with open(path, "rb") as f:
            files = {"person_image": ("sample_person_1.jpg", f, "image/jpeg")}
            res = client.post("/api/v1/analyze-posture", files=files)
        assert res.status_code == 200
        data = res.json()
        assert "landmarks" in data
        assert "image_size" in data

