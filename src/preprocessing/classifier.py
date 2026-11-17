"""
Nutz Try On Enterprise Studio - Intelligent Garment Analyzer & Target-Aware Mask Configurator
Phase 2: Indian Fashion Intelligence Expansion
- Supports Indian Ethnic Silhouettes:
    - Upper: 'kurta' (knee-length/mid-thigh), 'sherwani' (long coat), 'nehru_jacket' / 'modi_vest' (sleeveless outer vest),
             'saree_blouse' (cropped bodice), 't_shirt', 'shirt', 'jacket', 'blazer', 'sweater', 'tank_top'
    - Lower: 'lehenga' (flared ankle-length), 'churidar' / 'dhoti' / 'pyjama', 'shorts', 'pants', 'skirt'
    - Full: 'anarkali', 'saree', 'dress', 'jumpsuit'
- Hemline Profiles: 'cropped', 'waist_length', 'hip_length', 'mid_thigh', 'knee_length', 'ankle_length'
- Multi-Garment Layering & Sleeve-Lock: Detects outer vests (Modi/Nehru jackets) to lock existing sleeves intact.
- Multimodal Zero-Shot Classification via local Qwen2.5-VL on Ollama (fallback to precision geometry & heuristic contours).
"""
import os
import io
import cv2
import json
import base64
import urllib.request
from typing import Dict, Any, Optional, Tuple
import numpy as np
from PIL import Image

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")

INDIAN_UPPER_TYPES = {"kurta", "kurti", "sherwani", "achkan", "nehru_jacket", "modi_vest", "saree_blouse", "choli"}
INDIAN_LOWER_TYPES = {"lehenga", "ghagra", "chaniya", "churidar", "dhoti", "pyjama", "salwar"}
INDIAN_FULL_TYPES = {"anarkali", "saree"}


def classify_with_qwen_vl(garment_path: str) -> Optional[dict]:
    """
    Zero-Shot Multimodal Garment Classification using local Qwen-VL (qwen2.5vl:3b) on Ollama.
    Supports Western and Indian ethnic garments (Kurta, Sherwani, Nehru Jacket, Saree Blouse, Lehenga).
    """
    try:
        with open(garment_path, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode("utf-8")

        prompt = (
            "Analyze this clothing image and output ONLY a JSON object with these keys:\n"
            "{\n"
            '  "category": "upper_body" or "lower_body" or "full_body",\n'
            '  "sub_type": "kurta" or "sherwani" or "nehru_jacket" or "saree_blouse" or "lehenga" or "churidar" or "t_shirt" or "shirt" or "jacket" or "blazer" or "sweater" or "tank_top" or "shorts" or "pants" or "skirt" or "dress" or "anarkali",\n'
            '  "sleeve_type": "sleeveless" or "short_sleeve" or "three_quarter_sleeve" or "long_sleeve" or "not_applicable",\n'
            '  "hemline_profile": "cropped" or "waist_length" or "hip_length" or "mid_thigh" or "knee_length" or "ankle_length",\n'
            '  "is_outer_vest": true or false,\n'
            '  "is_dark": true or false\n'
            "}"
        )

        payload = {
            "model": "qwen2.5vl:3b",
            "prompt": prompt,
            "images": [b64_img],
            "stream": False,
            "format": "json"
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(f"{OLLAMA_URL}/api/generate", data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            raw_text = res.get("response", "{}")
            parsed = json.loads(raw_text)
            return parsed
    except Exception:
        return None


def analyze_garment_geometry(garment_path: str) -> dict:
    """
    Extracts geometric features from a garment flat-lay or ghost mannequin photo.
    Returns aspect ratio, wing span, crotch split presence, bottom flare ratio, and dominant color.
    """
    try:
        img = cv2.imread(garment_path)
        if img is None:
            return {
                "aspect_ratio": 1.0,
                "has_crotch_split": False,
                "wing_ratio": 1.0,
                "flare_ratio": 1.0,
                "dominant_color": {"rgb": [128, 128, 128], "hex": "#808080", "is_dark": False}
            }

        h, w, _ = img.shape
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Estimate background color from the four corners
        corners = [gray[0, 0], gray[0, -1], gray[-1, 0], gray[-1, -1]]
        bg_val = int(np.median(corners))
        foreground_mask = (np.abs(gray.astype(np.int32) - bg_val) > 20).astype(np.uint8)

        y_indices, x_indices = np.where(foreground_mask > 0)
        if len(y_indices) == 0:
            return {
                "aspect_ratio": 1.0,
                "has_crotch_split": False,
                "wing_ratio": 1.0,
                "flare_ratio": 1.0,
                "dominant_color": {"rgb": [128, 128, 128], "hex": "#808080", "is_dark": False}
            }

        y_min, y_max = int(y_indices.min()), int(y_indices.max())
        x_min, x_max = int(x_indices.min()), int(x_indices.max())
        gh = max(y_max - y_min, 1)
        gw = max(x_max - x_min, 1)
        aspect_ratio = round(float(gh) / float(gw), 3)

        # Dominant color & luminance inside foreground mask
        fg_pixels = img[foreground_mask > 0]
        if len(fg_pixels) > 0:
            median_bgr = np.median(fg_pixels, axis=0).astype(int)
            rgb = [int(median_bgr[2]), int(median_bgr[1]), int(median_bgr[0])]
            luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
            is_dark = luminance < 80.0
            hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        else:
            rgb = [128, 128, 128]
            is_dark = False
            hex_color = "#808080"

        # Check for crotch split in lower half (differentiates pants/shorts/churidar from skirts/lehenga)
        lower_crop = foreground_mask[y_min + int(gh * 0.65):y_max, x_min:x_max]
        has_crotch_split = False
        if lower_crop.size > 0:
            col_density = lower_crop.sum(axis=0)
            mid_start = int(len(col_density) * 0.35)
            mid_end = int(len(col_density) * 0.65)
            if mid_end > mid_start:
                center_min = np.min(col_density[mid_start:mid_end])
                lateral_max = max(np.max(col_density[:mid_start]), np.max(col_density[mid_end:]), 1)
                if (center_min / lateral_max) < 0.25:
                    has_crotch_split = True

        # Wing span ratio (chest width vs sleeve width)
        upper_slice = foreground_mask[y_min + int(gh * 0.15):y_min + int(gh * 0.35), x_min:x_max]
        mid_slice = foreground_mask[y_min + int(gh * 0.45):y_min + int(gh * 0.65), x_min:x_max]
        upper_cols = np.where(upper_slice.sum(axis=0) > 0)[0]
        mid_cols = np.where(mid_slice.sum(axis=0) > 0)[0]
        upper_w = float(upper_cols.max() - upper_cols.min()) if len(upper_cols) > 0 else float(gw)
        mid_w = float(mid_cols.max() - mid_cols.min()) if len(mid_cols) > 0 else float(gw)
        wing_ratio = round(upper_w / max(mid_w, 1.0), 3)

        # Flare ratio: bottom hem width vs mid/waist width (identifies flared Lehengas & Anarkalis)
        bottom_slice = foreground_mask[y_min + int(gh * 0.85):y_max, x_min:x_max]
        bottom_cols = np.where(bottom_slice.sum(axis=0) > 0)[0]
        bottom_w = float(bottom_cols.max() - bottom_cols.min()) if len(bottom_cols) > 0 else float(gw)
        flare_ratio = round(bottom_w / max(mid_w, 1.0), 3)

        return {
            "aspect_ratio": aspect_ratio,
            "has_crotch_split": has_crotch_split,
            "wing_ratio": wing_ratio,
            "flare_ratio": flare_ratio,
            "dominant_color": {
                "rgb": rgb,
                "hex": hex_color,
                "is_dark": is_dark
            }
        }
    except Exception:
        return {
            "aspect_ratio": 1.0,
            "has_crotch_split": False,
            "wing_ratio": 1.0,
            "flare_ratio": 1.0,
            "dominant_color": {"rgb": [128, 128, 128], "hex": "#808080", "is_dark": False}
        }


def detect_sleeve_length(garment_path: str, geometry: dict = None) -> str:
    """
    Classifies upper garment sleeve length into 'sleeveless', 'short_sleeve', or 'long_sleeve'.
    Handles folded outerwear (denim jackets, blazers, sweaters, coats, kurtas, sherwanis).
    """
    fname = os.path.basename(garment_path).lower()
    if any(k in fname for k in ["nehru", "modi", "vest", "waistcoat", "bundi", "koti", "tank", "sleeveless"]):
        return "sleeveless"
    if any(k in fname for k in ["sherwani", "achkan", "jacket", "blazer", "coat", "suit", "sweater", "hoodie"]):
        return "long_sleeve"
    if any(k in fname for k in ["kurta", "kurti"]):
        # Kurtas are overwhelmingly full-sleeve unless specified
        return "long_sleeve"
    if any(k in fname for k in ["blouse", "choli"]):
        return "short_sleeve"

    try:
        from src.preprocessing.skin_prior import detect_sleeve_type
        return detect_sleeve_type(garment_path)
    except Exception:
        try:
            from preprocessing.skin_prior import detect_sleeve_type
            return detect_sleeve_type(garment_path)
        except Exception:
            return "short_sleeve"


def detect_lower_garment_type(garment_path: str, geometry: dict = None) -> str:
    """
    Classifies lower body garment into 'shorts', 'pants', 'skirt', 'lehenga', or 'churidar'.
    """
    fname = os.path.basename(garment_path).lower()
    if any(k in fname for k in ["lehenga", "ghagra", "chaniya"]):
        return "lehenga"
    if any(k in fname for k in ["churidar", "dhoti", "pyjama", "salwar"]):
        return "churidar"
    if "short" in fname:
        return "shorts"
    if any(k in fname for k in ["pant", "trouser", "jean", "sweatpant", "legging"]):
        return "pants"
    if "skirt" in fname:
        return "skirt"

    if geometry is None:
        geometry = analyze_garment_geometry(garment_path)

    has_split = geometry.get("has_crotch_split", False)
    aspect = geometry.get("aspect_ratio", 1.0)
    flare = geometry.get("flare_ratio", 1.0)

    if not has_split:
        if flare > 1.4 or aspect > 1.2:
            return "lehenga"
        return "skirt"

    if aspect < 1.15:
        return "shorts"
    elif aspect > 1.45:
        return "churidar"
    else:
        return "pants"


def detect_category_from_image(garment_path: str, geometry: dict = None) -> str:
    """
    Infers broad category ('upper_body', 'lower_body', 'full_body').
    Incorporates Indian ethnic terminology.
    """
    fname = os.path.basename(garment_path).lower()
    if any(k in fname for k in ["pant", "short", "skirt", "trouser", "jean", "lehenga", "ghagra", "churidar", "dhoti", "salwar"]):
        return "lower_body"
    if any(k in fname for k in ["dress", "jumpsuit", "gown", "anarkali", "saree"]):
        return "full_body"
    if any(k in fname for k in ["kurta", "kurti", "sherwani", "achkan", "nehru", "modi", "blouse", "choli", "shirt", "tee", "top", "jacket", "blazer", "vest"]):
        return "upper_body"

    if geometry is None:
        geometry = analyze_garment_geometry(garment_path)

    aspect = geometry.get("aspect_ratio", 1.0)
    has_split = geometry.get("has_crotch_split", False)

    if aspect >= 1.85:
        return "full_body"
    elif aspect >= 1.25 and has_split:
        return "lower_body"
    elif has_split and aspect < 1.15:
        return "lower_body"
    else:
        return "upper_body"


def classify_garment(garment_path: str, category_override: str = None, use_vlm: bool = True) -> dict:
    """
    Comprehensive garment classifier supporting Western and Indian Ethnic Garments:
    1. Direct catalog/filename keyword prioritization for instant (<5ms) zero-latency classification.
    2. Zero-Shot Multimodal Visual Understanding via local Qwen2.5-VL for generic/unnamed images.
    3. Resilient OpenCV geometric & contour fallback (aspect ratio, flare, wing span).
    """
    fname = os.path.basename(garment_path).lower()
    geometry = analyze_garment_geometry(garment_path)

    # 1. High-Priority Catalog / Filename Keyword Matching
    has_explicit_keyword = False
    keyword_sub_type = None
    keyword_category = None
    keyword_sleeve = None
    keyword_hemline = None
    keyword_is_vest = False

    if any(k in fname for k in ["nehru", "modi", "bundi", "koti", "waistcoat", "vest"]):
        has_explicit_keyword = True
        keyword_category = "upper_body"
        keyword_sub_type = "nehru_jacket"
        keyword_sleeve = "sleeveless"
        keyword_hemline = "hip_length"
        keyword_is_vest = True
    elif any(k in fname for k in ["blouse", "choli", "crop"]):
        has_explicit_keyword = True
        keyword_category = "upper_body"
        keyword_sub_type = "saree_blouse"
        keyword_sleeve = detect_sleeve_length(garment_path, geometry)
        keyword_hemline = "cropped"
    elif any(k in fname for k in ["sherwani", "achkan"]):
        has_explicit_keyword = True
        keyword_category = "upper_body"
        keyword_sub_type = "sherwani"
        keyword_sleeve = "long_sleeve"
        keyword_hemline = "knee_length"
    elif any(k in fname for k in ["kurta", "kurti", "tunic", "pathani"]):
        has_explicit_keyword = True
        keyword_category = "upper_body"
        keyword_sub_type = "kurta"
        keyword_sleeve = detect_sleeve_length(garment_path, geometry)
        keyword_hemline = "knee_length"
    elif any(k in fname for k in ["lehenga", "ghagra", "chaniya"]):
        has_explicit_keyword = True
        keyword_category = "lower_body"
        keyword_sub_type = "lehenga"
        keyword_sleeve = "not_applicable"
        keyword_hemline = "ankle_length"
    elif any(k in fname for k in ["churidar", "dhoti", "pyjama", "salwar"]):
        has_explicit_keyword = True
        keyword_category = "lower_body"
        keyword_sub_type = "churidar"
        keyword_sleeve = "not_applicable"
        keyword_hemline = "ankle_length"

    if has_explicit_keyword:
        source = "catalog_keyword_rules"
        category = category_override or keyword_category
        sub_type = keyword_sub_type
        sleeve_type = keyword_sleeve
        hemline_profile = keyword_hemline
        is_outer_vest = keyword_is_vest
        lower_type = sub_type if category == "lower_body" else "not_applicable"

    else:
        # 2. Try Qwen-VL Vision Model for Generic/Unnamed Images
        qwen_info = classify_with_qwen_vl(garment_path) if use_vlm else None

        if qwen_info and "category" in qwen_info and "sleeve_type" in qwen_info:
            category = category_override or qwen_info.get("category", "upper_body")
            sub_type = qwen_info.get("sub_type", "t_shirt")
            sleeve_type = qwen_info.get("sleeve_type", "short_sleeve")
            hemline_profile = qwen_info.get("hemline_profile", "waist_length")
            is_outer_vest = bool(qwen_info.get("is_outer_vest", False))
            is_dark = bool(qwen_info.get("is_dark", geometry["dominant_color"]["is_dark"]))
            geometry["dominant_color"]["is_dark"] = is_dark
            source = "qwen2.5_vl"
            lower_type = sub_type if category == "lower_body" else "not_applicable"
        else:
            # 3. Fallback to OpenCV geometric heuristics
            source = "opencv_geometry_indian_rules"
            category = category_override if category_override in ["upper_body", "lower_body", "full_body"] else detect_category_from_image(garment_path, geometry)
            sleeve_type = "not_applicable"
            lower_type = "not_applicable"
            sub_type = "standard"
            hemline_profile = "waist_length"
            is_outer_vest = False

            if category == "upper_body":
                aspect = geometry.get("aspect_ratio", 1.0)
                wing = geometry.get("wing_ratio", 1.0)
                if aspect > 1.30:
                    sub_type = "kurta"
                    sleeve_type = "long_sleeve"
                    hemline_profile = "knee_length"
                elif aspect < 0.85:
                    sub_type = "saree_blouse"
                    sleeve_type = "short_sleeve"
                    hemline_profile = "cropped"
                elif 1.05 <= aspect <= 1.30 and wing <= 1.15:
                    sub_type = "nehru_jacket"
                    sleeve_type = "sleeveless"
                    hemline_profile = "hip_length"
                    is_outer_vest = True
                else:
                    sleeve_type = detect_sleeve_length(garment_path, geometry)
                    if sleeve_type == "sleeveless":
                        sub_type = "tank_top"
                        hemline_profile = "waist_length"
                    elif sleeve_type == "short_sleeve":
                        sub_type = "t_shirt"
                        hemline_profile = "waist_length"
                    else:
                        sub_type = "shirt"
                        hemline_profile = "waist_length"

            elif category == "lower_body":
                lower_type = detect_lower_garment_type(garment_path, geometry)
                sub_type = lower_type
                hemline_profile = "mid_thigh" if lower_type == "shorts" else "ankle_length"

            elif category == "full_body":
                sub_type = "dress" if not geometry.get("has_crotch_split") else "jumpsuit"
                sleeve_type = detect_sleeve_length(garment_path, geometry)
                hemline_profile = "ankle_length"

    # Derive target anatomical region and sleeve-locking flag
    sleeve_locked = is_outer_vest or (sub_type in {"nehru_jacket", "modi_vest"})

    if category == "upper_body":
        if sleeve_locked:
            target_region = "torso_only_sleeve_locked"
        elif sleeve_type == "sleeveless":
            target_region = "torso_only"
        elif sleeve_type == "short_sleeve":
            target_region = "torso_and_biceps"
        else:
            target_region = "full_upper"
    elif category == "lower_body":
        target_region = f"waist_to_{hemline_profile}"
    else:
        target_region = "full_body"

    # Base Mask Flags for ComfyUI SegFormer B3 Fashion
    flags = {
        "shirt": False, "top": False, "sweater": False, "cardigan": False,
        "jacket": False, "vest": False, "pants": False, "shorts": False,
        "skirt": False, "coat": False, "dress": False, "jumpsuit": False,
        "cape": False, "glasses": False, "hat": False, "hairaccessory": False,
        "tie": False, "glove": False, "watch": False, "belt": False,
        "legwarmer": False, "tights": False, "sock": False, "shoe": False,
        "bagwallet": False, "scarf": False, "umbrella": False, "hood": False,
        "collar": False, "lapel": False, "epaulette": False, "sleeve": False,
        "pocket": False, "neckline": False, "buckle": False, "zipper": False,
        "applique": False, "bead": False, "bow": False, "flower": False,
        "fringe": False, "ribbon": False, "rivet": False, "ruffle": False,
        "sequin": False, "tassel": False
    }

    if category == "upper_body":
        flags.update({
            "shirt": True,
            "top": True,
            "sweater": True,
            "cardigan": True,
            "jacket": True,
            "vest": True,
            "collar": True,
            "lapel": True,
            "sleeve": (sleeve_type != "sleeveless" and not sleeve_locked),
            "neckline": True,
            "pocket": True,
            "zipper": True,
            "hood": True,
            "dress": (sub_type in {"kurta", "sherwani"}),  # Enable long silhouette masking
            "coat": True,
            "pants": False,
            "shorts": False,
            "skirt": False
        })
    elif category == "lower_body":
        flags.update({
            "pants": True,
            "shorts": True,
            "skirt": True,
            "belt": True,
            "dress": (sub_type == "lehenga"),
            "shirt": False,
            "top": False
        })
    elif category == "full_body":
        flags.update({
            "dress": True,
            "jumpsuit": True,
            "shirt": True,
            "top": True,
            "skirt": True,
            "coat": True,
            "sleeve": (sleeve_type != "sleeveless"),
            "collar": True,
            "neckline": True
        })

    return {
        "source": source,
        "category": category,
        "sub_type": sub_type,
        "sleeve_type": sleeve_type,
        "hemline_profile": hemline_profile,
        "sleeve_locked": sleeve_locked,
        "is_outer_vest": is_outer_vest,
        "target_region": target_region,
        "aspect_ratio": geometry.get("aspect_ratio", 1.0),
        "flare_ratio": geometry.get("flare_ratio", 1.0),
        "dominant_color": geometry.get("dominant_color", {}),
        "mask_flags": flags
    }
