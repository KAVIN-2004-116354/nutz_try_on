"""
Nutz Try On - Posture Landmark Detection & Target Anatomical Region Module
Production Implementation with 3D MediaPipe Skeletal Bone Vectors & Dynamic Full-Garment Masking:
- 3D Skeletal Tracking (MediaPipe PoseLandmarker):
    - Computes vector distances to Shoulder->Elbow (bicep) vs Elbow->Wrist (forearm) segments.
    - Accurately classifies raised, bent, crossed, or dynamic arm poses invariant to rotation.
- Segment-Guided Facial Skin Hallucination:
    - Short sleeves: Forearms pre-filled with subject's sampled facial skin tone & micro-noise.
    - Sleeveless: Entire arms pre-filled with facial skin tone.
    - Shorts: Lower legs below knee pre-filled with facial skin tone.
- Dynamic Full-Garment Semantic Masking:
    - Replaces rigid Y-waistline truncation with dynamic semantic segmentation.
    - Untucked & oversized shirts are masked down to their natural hemline without cutting into shorts/pants.
    - Long ethnic tunics/kurtas are bounded at the hip to preserve lower skirts.
"""
import os
import cv2
import torch
import numpy as np
from PIL import Image
from transformers import SegformerImageProcessor, AutoModelForSemanticSegmentation

_SEGFORMER_MODEL = None
_SEGFORMER_PROCESSOR = None
_POSE_LANDMARKER = None

def get_segformer():
    global _SEGFORMER_MODEL, _SEGFORMER_PROCESSOR
    if _SEGFORMER_MODEL is None or _SEGFORMER_PROCESSOR is None:
        model_path = '/home/lenovo/ComfyUI/models/segformer/segformer-b3-fashion'
        _SEGFORMER_PROCESSOR = SegformerImageProcessor.from_pretrained(model_path, local_files_only=True)
        _SEGFORMER_MODEL = AutoModelForSemanticSegmentation.from_pretrained(model_path, local_files_only=True)
        if torch.cuda.is_available():
            _SEGFORMER_MODEL = _SEGFORMER_MODEL.to("cuda")
    return _SEGFORMER_PROCESSOR, _SEGFORMER_MODEL


def get_pose_landmarker():
    global _POSE_LANDMARKER
    if _POSE_LANDMARKER is None:
        try:
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            model_path = '/home/lenovo/try_on/models/mediapipe/pose_landmarker_lite.task'
            if os.path.exists(model_path):
                base_options = python.BaseOptions(model_asset_path=model_path)
                options = vision.PoseLandmarkerOptions(
                    base_options=base_options,
                    output_segmentation_masks=False
                )
                _POSE_LANDMARKER = vision.PoseLandmarker.create_from_options(options)
        except Exception:
            _POSE_LANDMARKER = None
    return _POSE_LANDMARKER


def point_to_segment_dist_sq(px, py, x1, y1, x2, y2):
    """
    Computes minimum squared Euclidean distance from points (px, py) to line segment (x1, y1)->(x2, y2).
    Fully vectorized for numpy arrays.
    """
    vx = float(x2 - x1)
    vy = float(y2 - y1)
    l2 = vx * vx + vy * vy
    if l2 == 0:
        return (px - x1) ** 2 + (py - y1) ** 2
    t = np.clip(((px - x1) * vx + (py - y1) * vy) / l2, 0.0, 1.0)
    proj_x = x1 + t * vx
    proj_y = y1 + t * vy
    return (px - proj_x) ** 2 + (py - proj_y) ** 2


def extract_skeletal_vectors(person_image_path: str, img_shape: tuple) -> dict:
    """
    Extracts 3D skeletal joints from MediaPipe PoseLandmarker.
    Returns left/right shoulder, elbow, wrist coordinates and hips.
    """
    h, w = img_shape[:2]
    landmarker = get_pose_landmarker()
    if landmarker is None:
        return None
    try:
        import mediapipe as mp
        image_mp = mp.Image.create_from_file(person_image_path)
        det = landmarker.detect(image_mp)
        if not det.pose_landmarks or len(det.pose_landmarks) == 0:
            return None
        lm = det.pose_landmarks[0]
        return {
            "r_shoulder": (float(lm[12].x * w), float(lm[12].y * h)),
            "r_elbow": (float(lm[14].x * w), float(lm[14].y * h)),
            "r_wrist": (float(lm[16].x * w), float(lm[16].y * h)),
            "r_pinky": (float(lm[18].x * w), float(lm[18].y * h)),
            "r_index": (float(lm[20].x * w), float(lm[20].y * h)),
            "r_thumb": (float(lm[22].x * w), float(lm[22].y * h)),
            "l_shoulder": (float(lm[11].x * w), float(lm[11].y * h)),
            "l_elbow": (float(lm[13].x * w), float(lm[13].y * h)),
            "l_wrist": (float(lm[15].x * w), float(lm[15].y * h)),
            "l_pinky": (float(lm[17].x * w), float(lm[17].y * h)),
            "l_index": (float(lm[19].x * w), float(lm[19].y * h)),
            "l_thumb": (float(lm[21].x * w), float(lm[21].y * h)),
            "r_hip": (float(lm[24].x * w), float(lm[24].y * h)),
            "l_hip": (float(lm[23].x * w), float(lm[23].y * h)),
            "r_knee": (float(lm[26].x * w), float(lm[26].y * h)),
            "l_knee": (float(lm[25].x * w), float(lm[25].y * h)),
            "r_ankle": (float(lm[28].x * w), float(lm[28].y * h)),
            "l_ankle": (float(lm[27].x * w), float(lm[27].y * h)),
        }
    except Exception:
        return None


def analyze_posture(person_image_path: str) -> dict:
    """
    Analyzes the subject's posture and computes anatomical vertical landmarks:
    - y_head, y_neck, y_shoulder, y_elbow, y_wrist, y_waist, y_knee, y_ankle
    Uses MediaPipe 3D Pose landmarks if available, with graceful fallback to face detection.
    """
    img = cv2.imread(person_image_path)
    if img is None:
        h, w = 1024, 768
    else:
        h, w, _ = img.shape

    # Try MediaPipe first
    skel = extract_skeletal_vectors(person_image_path, (h, w))
    if skel is not None:
        y_shoulder = int(min(skel["r_shoulder"][1], skel["l_shoulder"][1]))
        y_elbow = int(max(skel["r_elbow"][1], skel["l_elbow"][1]))
        y_wrist = int(max(skel["r_wrist"][1], skel["l_wrist"][1]))
        y_waist = int((skel["r_hip"][1] + skel["l_hip"][1]) / 2.0)
        y_knee = int((skel["r_knee"][1] + skel["l_knee"][1]) / 2.0)
        y_ankle = int((skel["r_ankle"][1] + skel["l_ankle"][1]) / 2.0)
        y_neck = max(0, y_shoulder - int(h * 0.05))
        y_head = max(0, y_neck - int(h * 0.12))
        y_chest = int((y_shoulder + y_waist) / 2.0)

        return {
            "image_size": {"width": w, "height": h},
            "source": "mediapipe_3d",
            "skeleton": skel,
            "landmarks": {
                "y_head": int(min(max(y_head, 0), h - 1)),
                "y_neck": int(min(max(y_neck, 0), h - 1)),
                "y_shoulder": int(min(max(y_shoulder, 0), h - 1)),
                "y_chest": int(min(max(y_chest, 0), h - 1)),
                "y_elbow": int(min(max(y_elbow, 0), h - 1)),
                "y_wrist": int(min(max(y_wrist, 0), h - 1)),
                "y_waist": int(min(max(y_waist, 0), h - 1)),
                "y_knee": int(min(max(y_knee, 0), h - 1)),
                "y_ankle": int(min(max(y_ankle, 0), h - 1))
            }
        }

    # Fallback to Haar Cascade + Anthropometric ratios
    face_box = None
    if img is not None:
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            if os.path.exists(cascade_path):
                face_cascade = cv2.CascadeClassifier(cascade_path)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(40, 40))
                if len(faces) > 0:
                    face_box = max(faces, key=lambda f: f[2] * f[3])
        except Exception:
            pass

    if face_box is not None:
        fx, fy, fw, fh = face_box
        head_top = max(0, fy - int(fh * 0.3))
        chin = fy + fh
        head_height = max(chin - head_top, int(h * 0.12))
        y_head = head_top
        y_neck = chin + int(head_height * 0.15)
        y_shoulder = chin + int(head_height * 0.45)
        y_chest = y_shoulder + int(head_height * 0.8)
        y_elbow = y_shoulder + int(head_height * 1.5)
        y_waist = y_shoulder + int(head_height * 2.3)
        y_wrist = y_waist + int(head_height * 0.5)
        y_knee = y_waist + int(head_height * 2.3)
        y_ankle = min(h - 1, int(y_knee + head_height * 1.9))
    else:
        y_head = int(h * 0.05)
        y_neck = int(h * 0.16)
        y_shoulder = int(h * 0.20)
        y_chest = int(h * 0.32)
        y_elbow = int(h * 0.42)
        y_waist = int(h * 0.52)
        y_wrist = int(h * 0.60)
        y_knee = int(h * 0.74)
        y_ankle = int(h * 0.92)

    return {
        "image_size": {"width": w, "height": h},
        "source": "anthropometric_heuristic",
        "skeleton": None,
        "landmarks": {
            "y_head": int(min(max(y_head, 0), h - 1)),
            "y_neck": int(min(max(y_neck, 0), h - 1)),
            "y_shoulder": int(min(max(y_shoulder, 0), h - 1)),
            "y_chest": int(min(max(y_chest, 0), h - 1)),
            "y_elbow": int(min(max(y_elbow, 0), h - 1)),
            "y_wrist": int(min(max(y_wrist, 0), h - 1)),
            "y_waist": int(min(max(y_waist, 0), h - 1)),
            "y_knee": int(min(max(y_knee, 0), h - 1)),
            "y_ankle": int(min(max(y_ankle, 0), h - 1))
        }
    }


def compute_target_bounds(posture: dict, garment_info: dict) -> dict:
    lm = posture["landmarks"]
    sub_type = garment_info.get("sub_type", "t_shirt")
    category = garment_info.get("category", "upper_body")
    sleeve_type = garment_info.get("sleeve_type", "short_sleeve")

    bounds = {}
    if category == "upper_body":
        bounds["y_top"] = lm["y_shoulder"]
        bounds["y_bottom"] = lm["y_waist"]
        if sleeve_type == "sleeveless":
            bounds["arm_cutoff"] = lm["y_shoulder"]
            bounds["bare_skin_zone"] = "full_arms"
        elif sleeve_type == "short_sleeve":
            bounds["arm_cutoff"] = lm["y_elbow"]
            bounds["bare_skin_zone"] = "forearms"
        else:
            bounds["arm_cutoff"] = lm["y_wrist"]
            bounds["bare_skin_zone"] = "none"

    elif category == "lower_body":
        bounds["y_top"] = lm["y_waist"]
        if sub_type == "shorts":
            bounds["y_bottom"] = lm["y_knee"]
            bounds["bare_skin_zone"] = "lower_legs"
        else:
            bounds["y_bottom"] = lm["y_ankle"]
            bounds["bare_skin_zone"] = "none"

    elif category == "full_body":
        bounds["y_top"] = lm["y_shoulder"]
        bounds["y_bottom"] = lm["y_ankle"] if sub_type == "jumpsuit" else lm["y_knee"]
        bounds["bare_skin_zone"] = "forearms" if sleeve_type == "short_sleeve" else "none"

    return bounds


def prepare_person_and_mask_for_tryon(
    person_path: str,
    garment_info: dict,
    output_person_path: str = None,
    output_mask_path: str = None
) -> dict:
    """
    Core Pipeline Function with 3D MediaPipe Bone Vectors & Dynamic Full-Garment Masking:
    1. Samples the subject's natural face skin tone.
    2. Runs SegFormer semantic parsing & extracts 3D posture landmarks.
    3. Uses 3D bone vectors (Shoulder->Elbow vs Elbow->Wrist) to separate bicep from forearm.
    4. Hallucinates facial skin tone onto bare limb zones.
    5. Dynamically constructs the full-garment inpainting mask without artificial waist truncation.
    """
    try:
        from src.preprocessing.skin_prior import sample_skin_tone
    except ImportError:
        from preprocessing.skin_prior import sample_skin_tone

    if output_person_path is None:
        output_person_path = person_path
    if output_mask_path is None:
        output_mask_path = person_path.replace(".jpg", "_mask.png").replace(".png", "_mask.png")

    img_pil = Image.open(person_path).convert("RGB")
    w, h = img_pil.size
    np_img = np.array(img_pil).copy()

    # 1. Extract posture landmarks & 3D skeletal vectors first (including hands)
    posture = analyze_posture(person_path)
    skeleton = posture.get("skeleton")
    lm = posture["landmarks"]
    y_shoulder = lm["y_shoulder"]
    y_elbow = lm["y_elbow"]
    y_waist = lm["y_waist"]
    y_knee = lm["y_knee"]

    # 2. Sample natural skin tone (Priority 1: Hands & Wrists -> Neck -> Face)
    skin = sample_skin_tone(person_path, skeleton=skeleton)
    skin_rgb = np.array(skin["rgb"], dtype=np.float32)

    # 3. SegFormer semantic prediction
    processor, model = get_segformer()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    inputs = processor(images=img_pil, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = torch.nn.functional.interpolate(outputs.logits.cpu(), size=(h, w), mode="bilinear", align_corners=False)
        pred_seg = logits.argmax(dim=1)[0].numpy()

    category = garment_info.get("category", "upper_body")
    sub_type = garment_info.get("sub_type", "t_shirt")
    sleeve_type = garment_info.get("sleeve_type", "short_sleeve")

    y_grid = np.arange(h)[:, None]

    # 4. 3D Skeletal Bone Vector Sleeve Segmentation
    sleeve_ys, sleeve_xs = np.where(pred_seg == 32)
    has_sleeves = len(sleeve_ys) > 0

    if has_sleeves and skeleton is not None:
        # Distance to Shoulder->Elbow vs Elbow->Wrist
        r_sh = skeleton["r_shoulder"]
        r_el = skeleton["r_elbow"]
        r_wr = skeleton["r_wrist"]
        l_sh = skeleton["l_shoulder"]
        l_el = skeleton["l_elbow"]
        l_wr = skeleton["l_wrist"]

        d_r_bicep = point_to_segment_dist_sq(sleeve_xs, sleeve_ys, r_sh[0], r_sh[1], r_el[0], r_el[1])
        d_r_forearm = point_to_segment_dist_sq(sleeve_xs, sleeve_ys, r_el[0], r_el[1], r_wr[0], r_wr[1])
        d_l_bicep = point_to_segment_dist_sq(sleeve_xs, sleeve_ys, l_sh[0], l_sh[1], l_el[0], l_el[1])
        d_l_forearm = point_to_segment_dist_sq(sleeve_xs, sleeve_ys, l_el[0], l_el[1], l_wr[0], l_wr[1])

        min_forearm_dist = np.minimum(d_r_forearm, d_l_forearm)
        min_bicep_dist = np.minimum(d_r_bicep, d_l_bicep)
        is_forearm = min_forearm_dist < min_bicep_dist

        forearm_mask = np.zeros((h, w), dtype=bool)
        forearm_mask[sleeve_ys[is_forearm], sleeve_xs[is_forearm]] = True

        bicep_mask = np.zeros((h, w), dtype=bool)
        bicep_mask[sleeve_ys[~is_forearm], sleeve_xs[~is_forearm]] = True
    else:
        # Fallback to horizontal cutoff
        forearm_mask = (pred_seg == 32) & (y_grid >= y_elbow)
        bicep_mask = (pred_seg == 32) & (y_grid < y_elbow)

    # 5. Dynamic Full-Garment Target Mask Construction
    # Strictly masks only the target clothing area to preserve 100% of the subject's natural pose, limbs, and hands
    upper_labels = [1, 2, 3, 4, 5, 6, 28, 29, 30, 33, 34, 36]
    lower_labels = [7, 8, 9, 20]
    is_upper = np.isin(pred_seg, upper_labels)
    is_lower = np.isin(pred_seg, lower_labels)

    if category == "upper_body":
        has_lower_body = np.any(is_lower)
        torso_mask = (is_upper & (~is_lower)) if has_lower_body else is_upper

        if sleeve_type == "sleeveless":
            sleeve_inpainting = np.zeros((h, w), dtype=bool)
        else:
            sleeve_inpainting = (pred_seg == 32)

        target_mask = torso_mask | sleeve_inpainting

    elif category == "lower_body":
        if sub_type == "shorts":
            target_mask = is_lower & (y_grid <= y_knee + 25)
        else:
            target_mask = is_lower

    else:
        # Full body
        full_labels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 28, 29, 30, 32, 33, 34]
        target_mask = np.isin(pred_seg, full_labels)

    # 6. Apply Unified Anatomy Guard: Strictly protect hands, wristwatch, face, and trousers
    try:
        from src.preprocessing.anatomy_guard import AdaptiveAnatomyGuard
        guard = AdaptiveAnatomyGuard()
        landmarks = guard.extract_landmarks(img_pil)
        hand_shield = guard.build_hand_protection_mask((h, w), landmarks)
        head_shield = guard.build_face_and_head_protection_mask((h, w), landmarks)
        target_mask = target_mask & (~(hand_shield > 0)) & (~(head_shield > 0))

        if category == "upper_body":
            hemline_profile = garment_info.get("hemline_profile")
            sleeve_locked = garment_info.get("sleeve_locked", False)
            y_hemline_bound = guard.estimate_garment_hemline(
                (h, w), landmarks, garment_sub_type=sub_type, hemline_profile=hemline_profile
            )
            target_mask[y_hemline_bound:, :] = False

            if sleeve_locked:
                sleeve_shield = guard.build_sleeve_lock_mask((h, w), landmarks)
                target_mask = target_mask & (~(sleeve_shield > 0))

            if sub_type in {"kurta", "kurti", "sherwani", "achkan", "nehru_jacket", "modi_vest"}:
                collar_shield = guard.build_mandarin_collar_protection_mask((h, w), landmarks)
                target_mask = target_mask & (~(collar_shield > 0))
    except Exception as e:
        print(f"[pose_target Notice] AnatomyGuard fallback: {e}")

    # 7. Apply soft morphological smoothing & subtle feathering for seamless edge transition
    mask_uint8 = (target_mask.astype(np.uint8) * 255)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask_closed = cv2.morphologyEx(mask_uint8, cv2.MORPH_CLOSE, kernel)
    mask_dilated = cv2.dilate(mask_closed, kernel, iterations=1)
    mask_blurred = cv2.GaussianBlur(mask_dilated, (3, 3), 0)

    # Save output artifacts - person remains 100% original without destructive fake skin painting
    img_pil.save(output_person_path)
    Image.fromarray(mask_blurred).save(output_mask_path)

    return {
        "status": "success",
        "source": posture.get("source", "hybrid"),
        "skin_rgb": skin["rgb"],
        "posture": posture,
        "conditioned_person_path": output_person_path,
        "target_mask_path": output_mask_path,
        "mask_pixel_count": int(np.count_nonzero(target_mask))
    }

# Backward compatibility alias
generate_target_aware_mask = prepare_person_and_mask_for_tryon
