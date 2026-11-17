"""
Skin Hallucination Prior & Sleeve-Length Classifier Module
Phase 1 + Phase 3 Production Implementation for Virtual Try-On

- Phase 3: Fast geometric garment sleeve-length classifier ('sleeveless', 'short_sleeve', 'long_sleeve')
- Phase 1: High-fidelity skin-tone sampler & arm prior conditioning to stop fabric color bleeding
"""

import os
import cv2
import numpy as np
from PIL import Image

def sample_skin_tone(image_input, skeleton: dict = None) -> dict:
    """
    Extracts the subject's natural skin tone with multi-zone priority:
    1. Hand & Wrist Skin (Primary): Samples directly from exposed hands and wrists using 3D skeletal joints.
    2. Neck & Upper Chest (Secondary): Samples bare skin between chin and garment collar.
    3. Facial Cheeks / Forehead (Tertiary): Samples face using adaptive HSV color space.
    4. Adaptive Image Foreground (Fallback): Samples upper body non-cloth pixels.
    Returns BGR, RGB, and Hex representations.
    """
    if isinstance(image_input, str):
        img = cv2.imread(image_input)
    elif isinstance(image_input, Image.Image):
        img = cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)
    else:
        img = image_input

    if img is None:
        return {"bgr": [115, 120, 155], "rgb": [155, 120, 115], "hex": "#9b7873", "source": "default"}

    h, w, _ = img.shape

    # 1. PRIMARY: Sample from exposed hands & wrists if skeleton is provided
    if skeleton is not None:
        hand_pts = []
        for side in ["r", "l"]:
            wrist_key = f"{side}_wrist"
            if wrist_key in skeleton:
                wx, wy = skeleton[wrist_key]
                # Include hand extremities if available
                pts = [(int(wx), int(wy))]
                for joint in ["pinky", "index", "thumb"]:
                    jk = f"{side}_{joint}"
                    if jk in skeleton:
                        pts.append((int(skeleton[jk][0]), int(skeleton[jk][1])))
                hand_pts.append(pts)

        hand_pixels = []
        for pts in hand_pts:
            if len(pts) >= 3:
                # Compute convex hull of hand joints
                hull = cv2.convexHull(np.array(pts, dtype=np.int32))
                hmask = np.zeros((h, w), dtype=np.uint8)
                cv2.fillConvexPoly(hmask, hull, 255)
            elif len(pts) > 0:
                # Circular patch around wrist
                wx, wy = pts[0]
                rad = max(18, int(w * 0.035))
                hmask = np.zeros((h, w), dtype=np.uint8)
                cv2.circle(hmask, (wx, wy), rad, 255, -1)
            else:
                continue

            # Filter valid skin: moderate saturation, adequate brightness, non-black/white
            roi_bgr = img[hmask > 0]
            if len(roi_bgr) > 0:
                hsv = cv2.cvtColor(roi_bgr.reshape(-1, 1, 3), cv2.COLOR_BGR2HSV).reshape(-1, 3)
                valid = (hsv[:, 0] <= 30) & (hsv[:, 1] >= 15) & (hsv[:, 1] <= 210) & (hsv[:, 2] >= 35) & (hsv[:, 2] <= 245)
                filtered = roi_bgr[valid]
                if len(filtered) >= 20:
                    hand_pixels.extend(filtered)

        if len(hand_pixels) >= 30:
            bgr = np.median(hand_pixels, axis=0).astype(int)
            bgr_list = [int(bgr[0]), int(bgr[1]), int(bgr[2])]
            rgb_list = [int(bgr[2]), int(bgr[1]), int(bgr[0])]
            hex_color = f"#{rgb_list[0]:02x}{rgb_list[1]:02x}{rgb_list[2]:02x}"
            return {"bgr": bgr_list, "rgb": rgb_list, "hex": hex_color, "source": "hands_and_wrists"}

    # 2. SECONDARY: Sample from neck / clavicle if shoulders are present
    if skeleton is not None and "r_shoulder" in skeleton and "l_shoulder" in skeleton:
        r_sh = skeleton["r_shoulder"]
        l_sh = skeleton["l_shoulder"]
        mid_x = int((r_sh[0] + l_sh[0]) / 2.0)
        top_y = max(0, int(min(r_sh[1], l_sh[1]) - h * 0.08))
        bot_y = int(min(r_sh[1], l_sh[1]) + h * 0.01)
        half_w = max(15, int(abs(r_sh[0] - l_sh[0]) * 0.18))

        neck_crop = img[top_y:bot_y, max(0, mid_x - half_w):min(w, mid_x + half_w)]
        if neck_crop.size > 0:
            hsv = cv2.cvtColor(neck_crop, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, np.array([0, 15, 40]), np.array([30, 220, 250]))
            pixels = neck_crop[mask > 0]
            if len(pixels) >= 30:
                bgr = np.median(pixels, axis=0).astype(int)
                bgr_list = [int(bgr[0]), int(bgr[1]), int(bgr[2])]
                rgb_list = [int(bgr[2]), int(bgr[1]), int(bgr[0])]
                hex_color = f"#{rgb_list[0]:02x}{rgb_list[1]:02x}{rgb_list[2]:02x}"
                return {"bgr": bgr_list, "rgb": rgb_list, "hex": hex_color, "source": "neck"}

    # 3. TERTIARY: Facial / neck HSV color space segmentation
    crop = img[int(h * 0.08):int(h * 0.35), int(w * 0.30):int(w * 0.70)]
    if crop.size == 0:
        crop = img[:int(h * 0.4), :]

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    lower_skin = np.array([0, 15, 35], dtype=np.uint8)
    upper_skin = np.array([32, 225, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    pixels = crop[mask > 0]
    if len(pixels) > 50:
        bgr = np.median(pixels, axis=0).astype(int)
        bgr_list = [int(bgr[0]), int(bgr[1]), int(bgr[2])]
        rgb_list = [int(bgr[2]), int(bgr[1]), int(bgr[0])]
        source = "face"
    else:
        # 4. ADAPTIVE FALLBACK: Image upper-half warm foreground median
        upper_half = img[:int(h * 0.6), :]
        gray_u = cv2.cvtColor(upper_half, cv2.COLOR_BGR2GRAY)
        fg_mask = (gray_u > 40) & (gray_u < 230)
        fg_pixels = upper_half[fg_mask]
        if len(fg_pixels) > 100:
            bgr = np.median(fg_pixels, axis=0).astype(int)
            bgr_list = [int(bgr[0]), int(bgr[1]), int(bgr[2])]
            rgb_list = [int(bgr[2]), int(bgr[1]), int(bgr[0])]
            source = "adaptive_foreground"
        else:
            bgr_list = [115, 120, 155]
            rgb_list = [155, 120, 115]
            source = "default_warm"

    hex_color = f"#{rgb_list[0]:02x}{rgb_list[1]:02x}{rgb_list[2]:02x}"
    return {"bgr": bgr_list, "rgb": rgb_list, "hex": hex_color, "source": source}


def detect_sleeve_type(garment_path: str) -> str:
    """
    Classifies garment sleeve length into 'sleeveless', 'short_sleeve', or 'long_sleeve'
    using contour geometry and width-profile analysis across 10 vertical slices.
    Runs in < 5ms.
    """
    try:
        img = cv2.imread(garment_path)
        if img is None:
            return "short_sleeve"
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bg_val = int(np.median([gray[0, 0], gray[0, -1], gray[-1, 0], gray[-1, -1]]))
        mask = (np.abs(gray.astype(np.int32) - bg_val) > 20).astype(np.uint8)

        y_indices, x_indices = np.where(mask > 0)
        if len(y_indices) == 0:
            return "short_sleeve"

        gh = y_indices.max() - y_indices.min()
        gw = x_indices.max() - x_indices.min()
        if gh == 0 or gw == 0:
            return "short_sleeve"

        # Calculate garment width along 10 vertical slices
        widths = []
        for i in range(10):
            y1 = y_indices.min() + int(i * gh / 10)
            y2 = y_indices.min() + int((i + 1) * gh / 10)
            slice_mask = mask[y1:y2, x_indices.min():x_indices.max()]
            cols = np.where(slice_mask.sum(axis=0) > 0)[0]
            widths.append(cols.max() - cols.min() if len(cols) > 0 else 0)

        max_w = max(widths)
        if max_w == 0:
            return "short_sleeve"

        mid_lower_ratio = np.median(widths[5:8]) / max_w
        aspect = gh / max(gw, 1)

        # 1. Sleeveless test: narrow profile throughout with no protruding sleeve wings
        if aspect > 1.35 and mid_lower_ratio > 0.85 and (widths[3] / max_w) < 0.90:
            return "sleeveless"
        
        # 2. Long sleeve test: sleeves extend down the sides into the middle/lower slices
        if mid_lower_ratio >= 0.75:
            return "long_sleeve"
        
        # 3. Short sleeve: upper wings protrude, and garment narrows significantly below chest
        return "short_sleeve"
    except Exception:
        return "short_sleeve"


def apply_skin_hallucination_prior(
    person_image_path: str,
    sleeve_type: str,
    output_path: str = None
) -> dict:
    """
    Phase 1 Skin Hallucination Prior:
    When a person wears long sleeves and tries on a short-sleeve or sleeveless garment,
    this function detects the person's natural skin tone and applies a soft skin-tone
    pre-fill to the exposed arm regions. This prevents CatVTON from inpainting
    garment fabric down to the wrists.
    """
    if output_path is None:
        output_path = person_image_path

    if sleeve_type == "long_sleeve":
        return {
            "status": "bypassed",
            "sleeve_type": "long_sleeve",
            "message": "Full-length garment matches or exceeds arm coverage."
        }

    try:
        img = cv2.imread(person_image_path)
        if img is None:
            return {"status": "error", "message": "Failed to read person image"}

        h, w, _ = img.shape
        skin_meta = sample_skin_tone(img)
        skin_bgr = np.array(skin_meta["bgr"], dtype=np.uint8)

        # Determine arm region cutoff based on sleeve type
        # For short sleeve: upper 40% of torso is tee sleeve; lower 60% of arm becomes skin
        # For sleeveless: entire arm from shoulder down becomes skin
        if sleeve_type == "sleeveless":
            cutoff_y_start = int(h * 0.28) # shoulder level
        else:
            cutoff_y_start = int(h * 0.40) # mid-bicep level
        
        cutoff_y_end = int(h * 0.62) # wrist level

        # Detect dark / non-skin arm clothing in the lateral regions
        left_arm_roi = (slice(cutoff_y_start, cutoff_y_end), slice(int(w * 0.15), int(w * 0.45)))
        right_arm_roi = (slice(cutoff_y_start, cutoff_y_end), slice(int(w * 0.55), int(w * 0.85)))

        conditioned_img = img.copy()
        
        # Generate subtle skin texture noise
        noise = np.random.normal(0, 4.0, img.shape).astype(np.int16)

        for roi in [left_arm_roi, right_arm_roi]:
            region = conditioned_img[roi]
            if region.size == 0:
                continue

            # Identify dark garment cloth vs already bare skin/background
            r_gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            r_hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
            
            # Mask pixels that are NOT already skin
            is_skin = cv2.inRange(r_hsv, np.array([0, 20, 45]), np.array([28, 210, 255]))
            is_dark_cloth = (r_gray < 160) & (is_skin == 0)

            if np.any(is_dark_cloth):
                cloth_mask = is_dark_cloth.astype(np.uint8) * 255
                cloth_mask_blur = cv2.GaussianBlur(cloth_mask, (15, 15), 0) / 255.0
                cloth_mask_3d = np.repeat(np.expand_dims(cloth_mask_blur, axis=-1), 3, axis=-1)

                skin_fill = np.full_like(region, skin_bgr, dtype=np.int16)
                skin_fill = np.clip(skin_fill + noise[roi], 0, 255).astype(np.uint8)

                # Softly blend skin tone into dark sleeve cloth
                blended = (skin_fill * cloth_mask_3d + region * (1.0 - cloth_mask_3d)).astype(np.uint8)
                conditioned_img[roi] = blended

        cv2.imwrite(output_path, conditioned_img)
        return {
            "status": "applied",
            "sleeve_type": sleeve_type,
            "skin_tone_rgb": skin_meta["rgb"],
            "skin_tone_hex": skin_meta["hex"],
            "output_path": output_path
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

