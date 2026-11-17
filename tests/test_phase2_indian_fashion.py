"""
Nutz Try On Enterprise Studio - Phase 2 Unit & Regression Test Suite
Validates:
1. Indian Ethnic Garment Classification (Kurta, Sherwani, Nehru Jacket, Saree Blouse, Lehenga).
2. Dynamic Hemline Adaptation (Knee-length, Mid-thigh, Cropped, Hip-length).
3. Multi-Garment Layering & Sleeve-Lock (Nehru Jacket / Modi Vest arm preservation).
4. Mandarin Collar & Jewelry Protection.
5. End-to-end Kurta and Modi Vest masking on Namaste Pose.
"""

import os
import sys
import numpy as np
import cv2
import pytest
from PIL import Image

sys.path.insert(0, "/home/lenovo/try_on")

from src.preprocessing.classifier import (
    classify_garment,
    analyze_garment_geometry,
    detect_sleeve_length,
    detect_lower_garment_type,
    detect_category_from_image
)
from src.preprocessing.anatomy_guard import AdaptiveAnatomyGuard


class MockLandmark:
    def __init__(self, x, y, z=0.0, visibility=0.99):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility


def create_mock_body_landmarks():
    """Generates a standard standing body landmark array (MediaPipe 33 keypoints)."""
    lm = [MockLandmark(0.5, 0.5) for _ in range(33)]
    # Cranial / Facial
    lm[0] = MockLandmark(0.50, 0.12)  # Nose
    lm[9] = MockLandmark(0.48, 0.16)  # Mouth left
    lm[10] = MockLandmark(0.52, 0.16) # Mouth right
    # Shoulders
    lm[11] = MockLandmark(0.38, 0.22) # Left shoulder
    lm[12] = MockLandmark(0.62, 0.22) # Right shoulder
    # Elbows
    lm[13] = MockLandmark(0.32, 0.38) # Left elbow
    lm[14] = MockLandmark(0.68, 0.38) # Right elbow
    # Wrists (Arms down)
    lm[15] = MockLandmark(0.30, 0.52) # Left wrist
    lm[16] = MockLandmark(0.70, 0.52) # Right wrist
    # Hips
    lm[23] = MockLandmark(0.42, 0.50) # Left hip
    lm[24] = MockLandmark(0.58, 0.50) # Right hip
    # Knees
    lm[25] = MockLandmark(0.44, 0.74) # Left knee
    lm[26] = MockLandmark(0.56, 0.74) # Right knee
    # Ankles
    lm[27] = MockLandmark(0.45, 0.92) # Left ankle
    lm[28] = MockLandmark(0.55, 0.92) # Right ankle
    return lm


# =============================================================================
# 1. CLASSIFICATION & GEOMETRY TESTS
# =============================================================================

def test_indian_garment_keyword_classification(tmp_path):
    """Verifies Indian silhouettes are correctly classified by filename & rule fallback."""
    test_cases = [
        ("royal_silk_kurta.jpg", "upper_body", "kurta", "knee_length", False),
        ("mens_sherwani_wedding.png", "upper_body", "sherwani", "knee_length", False),
        ("modi_jacket_khadi.jpg", "upper_body", "nehru_jacket", "hip_length", True),
        ("nehru_vest_black.jpg", "upper_body", "nehru_jacket", "hip_length", True),
        ("designer_saree_blouse.png", "upper_body", "saree_blouse", "cropped", False),
        ("bridal_lehenga_red.jpg", "lower_body", "lehenga", "ankle_length", False),
        ("silk_churidar_pyjama.jpg", "lower_body", "churidar", "ankle_length", False),
    ]

    for fname, exp_cat, exp_sub, exp_hem, exp_locked in test_cases:
        p = tmp_path / fname
        # Create a dummy image
        img = np.ones((400, 300, 3), dtype=np.uint8) * 200
        cv2.imwrite(str(p), img)

        res = classify_garment(str(p))
        assert res["category"] == exp_cat, f"Expected category {exp_cat} for {fname}, got {res['category']}"
        assert res["sub_type"] == exp_sub, f"Expected sub_type {exp_sub} for {fname}, got {res['sub_type']}"
        assert res["hemline_profile"] == exp_hem, f"Expected hemline {exp_hem} for {fname}, got {res['hemline_profile']}"
        assert res["sleeve_locked"] == exp_locked, f"Expected sleeve_locked {exp_locked} for {fname}, got {res['sleeve_locked']}"


def test_geometric_fallback_kurta_vs_blouse(tmp_path):
    """Verifies that aspect ratio heuristics distinguish long Kurtas from cropped Saree Blouses."""
    # Long Kurta geometry: tall aspect ratio (height > width)
    kurta_path = tmp_path / "ethnic_upper_1.png"
    kurta_img = np.ones((800, 450, 3), dtype=np.uint8) * 255  # white bg
    kurta_img[100:700, 100:350] = [30, 40, 180]              # red tunic shape (aspect ~ 2.4)
    cv2.imwrite(str(kurta_path), kurta_img)

    res_kurta = classify_garment(str(kurta_path), category_override="upper_body", use_vlm=False)
    assert res_kurta["sub_type"] in {"kurta", "sherwani"}, f"Long ethnic upper should be kurta, got {res_kurta['sub_type']}"
    assert res_kurta["hemline_profile"] == "knee_length"

    # Cropped Saree Blouse geometry: wide aspect ratio (height < width)
    blouse_path = tmp_path / "ethnic_upper_2.png"
    blouse_img = np.ones((400, 600, 3), dtype=np.uint8) * 255 # white bg
    blouse_img[100:260, 120:480] = [20, 160, 40]             # green cropped blouse (aspect ~ 0.44)
    cv2.imwrite(str(blouse_path), blouse_img)

    res_blouse = classify_garment(str(blouse_path), category_override="upper_body", use_vlm=False)
    assert res_blouse["sub_type"] == "saree_blouse", f"Cropped bodice should be saree_blouse, got {res_blouse['sub_type']}"
    assert res_blouse["hemline_profile"] == "cropped"


# =============================================================================
# 2. DYNAMIC HEMLINE ADAPTATION TESTS
# =============================================================================

def test_dynamic_hemline_adaptation():
    """Validates that Kurta extends to knees while shirts and cropped blouses stop higher."""
    guard = AdaptiveAnatomyGuard()
    landmarks = create_mock_body_landmarks()
    img_shape = (1000, 600)  # h=1000, w=600

    # 1. Standard Western Shirt: stops at waist (~500px)
    y_shirt = guard.estimate_garment_hemline(img_shape, landmarks, garment_sub_type="shirt")
    assert 480 <= y_shirt <= 540, f"Shirt hemline should be at waist (~500), got {y_shirt}"

    # 2. Cropped Saree Blouse: stops at ribcage above waist (<450px)
    y_blouse = guard.estimate_garment_hemline(img_shape, landmarks, garment_sub_type="saree_blouse")
    assert y_blouse < y_shirt, f"Saree blouse hemline ({y_blouse}) must be higher than shirt ({y_shirt})"
    assert y_blouse <= 440, f"Saree blouse hemline expected <= 440, got {y_blouse}"

    # 3. Nehru Jacket: hip length (~550px)
    y_nehru = guard.estimate_garment_hemline(img_shape, landmarks, garment_sub_type="nehru_jacket")
    assert y_shirt < y_nehru < 600, f"Nehru jacket hemline ({y_nehru}) must be between waist ({y_shirt}) and mid-thigh"

    # 4. Long Kurta: extends down to knees (~720px)
    y_kurta = guard.estimate_garment_hemline(img_shape, landmarks, garment_sub_type="kurta")
    assert y_kurta >= 700, f"Kurta hemline ({y_kurta}) must reach knee area (~720-740)"
    assert y_kurta > y_nehru + 100, f"Kurta ({y_kurta}) must be significantly longer than Nehru jacket ({y_nehru})"


# =============================================================================
# 3. SLEEVE-LOCK MULTI-GARMENT LAYERING TESTS
# =============================================================================

def test_sleeve_lock_arm_protection():
    """Validates that build_sleeve_lock_mask covers both arms and protects existing sleeves."""
    guard = AdaptiveAnatomyGuard()
    landmarks = create_mock_body_landmarks()
    img_shape = (1000, 600)
    h, w = img_shape

    sleeve_mask = guard.build_sleeve_lock_mask(img_shape, landmarks)
    assert sleeve_mask.shape == (h, w)
    assert np.count_nonzero(sleeve_mask) > 1000, "Sleeve lock mask must cover arm corridors"

    # Left elbow (0.32 * 600 = 192, 0.38 * 1000 = 380)
    # Right elbow (0.68 * 600 = 408, 0.38 * 1000 = 380)
    assert sleeve_mask[380, 192] == 255, "Left arm corridor must be protected"
    assert sleeve_mask[380, 408] == 255, "Right arm corridor must be protected"

    # Center torso (0.50 * 600 = 300, 0.35 * 1000 = 350) should NOT be covered by sleeve lock
    assert sleeve_mask[350, 300] == 0, "Torso center must NOT be in the sleeve lock mask"


# =============================================================================
# 4. MANDARIN COLLAR & JEWELRY PROTECTION TESTS
# =============================================================================

def test_mandarin_collar_protection():
    """Validates that build_mandarin_collar_protection_mask protects jawline & chin."""
    guard = AdaptiveAnatomyGuard()
    landmarks = create_mock_body_landmarks()
    img_shape = (1000, 600)

    collar_mask = guard.build_mandarin_collar_protection_mask(img_shape, landmarks)
    assert collar_mask.shape == img_shape

    # Chin & lower face center (0.50 * 600 = 300, 0.16 * 1000 = 160)
    assert collar_mask[160, 300] == 255, "Chin/jawline must be protected for high Mandarin collars"


# =============================================================================
# 5. REAL IMAGE INTEGRATION ON NAMASTE POSE
# =============================================================================

def test_real_image_kurta_vs_shirt_hemlines():
    """Validates hemline calculation on real sample_person_1.jpg (Namaste Pose)."""
    img_path = "/home/lenovo/try_on/frontend/assets/sample_person_1.jpg"
    if not os.path.exists(img_path):
        pytest.skip(f"Sample image not found at {img_path}")

    pil_img = Image.open(img_path)
    w, h = pil_img.size

    guard = AdaptiveAnatomyGuard()
    landmarks = guard.extract_landmarks(pil_img)
    assert landmarks is not None, "MediaPipe must detect landmarks on sample_person_1.jpg"

    y_waist = guard.estimate_pose_aware_waistline((h, w), landmarks)
    y_kurta = guard.estimate_garment_hemline((h, w), landmarks, garment_sub_type="kurta")
    y_nehru = guard.estimate_garment_hemline((h, w), landmarks, garment_sub_type="nehru_jacket")

    # The Kurta hemline must be substantially below the waistline
    assert y_kurta > y_waist + int(h * 0.10), f"Kurta hemline ({y_kurta}) must extend at least 10% below waist ({y_waist})"
    assert y_nehru > y_waist, f"Nehru jacket ({y_nehru}) must extend below waistline ({y_waist})"
    assert y_kurta > y_nehru, f"Kurta ({y_kurta}) must be longer than Nehru jacket ({y_nehru})"
