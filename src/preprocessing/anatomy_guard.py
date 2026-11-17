"""
Nutz Try On Enterprise Studio - Resolution-Adaptive Anatomical Protection Engine
Phase 2: Indian Fashion Intelligence Expansion
Protects:
1. Individual fingers, folded Namaste hands, wrists, wristwatches, bracelets (Phase 1).
2. Face, hair, eyeglasses, chin, beard, and neck boundaries (Phase 1).
3. Pose-aware waistline boundaries (prevents shirt from bleeding into trousers) (Phase 1).
4. Knee-length adaptive hemlines for Kurtas, Sherwanis, and Anarkalis (Phase 2).
5. Sleeve-lock multi-garment layering for Nehru Jackets / Modi Vests (Phase 2).
6. Mandarin / Bandhgala collar neckline & ethnic jewelry preservation (Phase 2).

Features:
- Resolution-adaptive morphological operations (no fixed-pixel hardcoding).
- 3D Skeletal tracking via MediaPipe PoseLandmarker (Landmarks 25 & 26 for knee bounds).
- Multi-garment sleeve preservation for layered ethnic wear.
- Integration with centralized semantic labels.
"""

import os
import math
from typing import Dict, Any, Optional, Tuple, List, Union
import cv2
import numpy as np
from PIL import Image

try:
    from src.preprocessing.semantic_labels import (
        get_unified_part_mask, get_part_mask, DatasetType, ATR_MAPPING, LIP_MAPPING
    )
except ImportError:
    from preprocessing.semantic_labels import (
        get_unified_part_mask, get_part_mask, DatasetType, ATR_MAPPING, LIP_MAPPING
    )


class AdaptiveAnatomyGuard:
    """
    Precision anatomy protection system for Virtual Try-On.
    Calculates dynamic safety buffers scaled to detected subject proportions and image resolution.
    Supports Western silhouettes and Indian ethnic garments (Kurta, Sherwani, Nehru Jacket, Saree Blouse).
    """

    def __init__(self, mp_task_path: str = "/home/lenovo/try_on/models/mediapipe/pose_landmarker_lite.task"):
        self.mp_task_path = mp_task_path
        self._detector = None

    def _get_detector(self):
        if self._detector is None and os.path.exists(self.mp_task_path):
            try:
                from mediapipe.tasks import python
                from mediapipe.tasks.python import vision
                base_options = python.BaseOptions(model_asset_path=self.mp_task_path)
                options = vision.PoseLandmarkerOptions(base_options=base_options)
                self._detector = vision.PoseLandmarker.create_from_options(options)
            except Exception as e:
                print(f"[AnatomyGuard Warning] MediaPipe init failed: {e}")
                self._detector = None
        return self._detector

    def extract_landmarks(self, image: Union[np.ndarray, Image.Image]) -> Optional[Any]:
        """Runs MediaPipe 3D PoseLandmarker and returns landmarks."""
        detector = self._get_detector()
        if detector is None:
            return None
        try:
            import mediapipe as mp
            if isinstance(image, Image.Image):
                np_img = np.array(image.convert("RGB"))
            else:
                np_img = image if image.ndim == 3 else cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=np_img)
            result = detector.detect(mp_img)
            if result.pose_landmarks and len(result.pose_landmarks) > 0:
                return result.pose_landmarks[0]
        except Exception as e:
            print(f"[AnatomyGuard Warning] Landmark detection failed: {e}")
        return None

    def build_hand_protection_mask(
        self,
        image_shape: Tuple[int, int],
        landmarks: Optional[Any],
        schp_atr: Optional[np.ndarray] = None,
        schp_lip: Optional[np.ndarray] = None,
        densepose: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Builds a resolution-adaptive hand and wristwatch protection mask (uint8: 0 or 255).
        - Uses convex polygons connecting wrists and finger tips.
        - Detects Namaste pose (clasped hands) and builds an integrated hands-wrist shield.
        - Extends coverage to include wristwatch and bracelets along the forearm vector.
        - Fuses DensePose hand labels (indices 3, 4) to protect all individual fingers up to fingertips.
        - Incorporates SCHP arm/hand semantic pixels for boundary fidelity.
        """
        h, w = image_shape[:2]
        hand_mask = np.zeros((h, w), dtype=np.uint8)

        # Fused DensePose hand segmentation (unconditional fingertip & palm protection)
        if densepose is not None:
            dp_hands = ((densepose == 3) | (densepose == 4)).astype(np.uint8) * 255
            hand_mask = cv2.bitwise_or(hand_mask, dp_hands)

        if landmarks is None:
            if schp_atr is not None or schp_lip is not None:
                arms_mask = np.zeros((h, w), dtype=np.uint8)
                if schp_atr is not None:
                    arms_mask |= get_unified_part_mask(schp_atr, "arms", DatasetType.ATR)
                if schp_lip is not None:
                    arms_mask |= get_unified_part_mask(schp_lip, "arms", DatasetType.LIP)
                hand_mask = cv2.bitwise_or(hand_mask, (arms_mask * 255).astype(np.uint8))
            return hand_mask

        lm = landmarks

        # Hand landmark definitions
        left_hand_indices = [15, 17, 19, 21]    # Left: wrist, pinky, index, thumb
        right_hand_indices = [16, 18, 20, 22]  # Right: wrist, pinky, index, thumb
        elbow_indices = {15: 13, 16: 14}       # Left wrist -> Left elbow (13), Right wrist -> Right elbow (14)

        # Check visibility
        l_vis = any(lm[i].visibility > 0.30 for i in left_hand_indices)
        r_vis = any(lm[i].visibility > 0.30 for i in right_hand_indices)

        # Check Namaste Clasp Pose: Left wrist (15) and Right wrist (16) are close horizontally & vertically
        is_namaste = False
        if l_vis and r_vis:
            wrist_dist = math.hypot((lm[15].x - lm[16].x) * w, (lm[15].y - lm[16].y) * h)
            shoulder_span = abs(lm[11].x - lm[12].x) * w
            if shoulder_span > 0 and wrist_dist < (shoulder_span * 0.45):
                is_namaste = True

        all_hand_pts = []

        for hand_set, wrist_idx in [(left_hand_indices, 15), (right_hand_indices, 16)]:
            pts = []
            for idx in hand_set:
                if lm[idx].visibility > 0.25:
                    px = int(np.clip(lm[idx].x * w, 0, w - 1))
                    py = int(np.clip(lm[idx].y * h, 0, h - 1))
                    pts.append([px, py])
                    all_hand_pts.append([px, py])

            if len(pts) >= 3:
                pts_np = np.array(pts, dtype=np.int32)
                min_x, min_y = pts_np.min(axis=0)
                max_x, max_y = pts_np.max(axis=0)
                hand_w = max(max_x - min_x, 1)
                hand_h = max(max_y - min_y, 1)
                hand_diag = math.hypot(hand_w, hand_h)

                adaptive_buffer = int(np.clip(hand_diag * 0.12, 4, max(w, h) * 0.04))

                # Wristwatch & Bracelet extension: extend 20% along vector from wrist towards elbow
                elbow_idx = elbow_indices[wrist_idx]
                if lm[elbow_idx].visibility > 0.25:
                    wx, wy = lm[wrist_idx].x * w, lm[wrist_idx].y * h
                    ex, ey = lm[elbow_idx].x * w, lm[elbow_idx].y * h
                    dx, dy = ex - wx, ey - wy
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        watch_dist = min(dist * 0.25, hand_diag * 0.35)
                        watch_x = int(np.clip(wx + (dx / dist) * watch_dist, 0, w - 1))
                        watch_y = int(np.clip(wy + (dy / dist) * watch_dist, 0, h - 1))
                        pts.append([watch_x, watch_y])
                        all_hand_pts.append([watch_x, watch_y])

                hull = cv2.convexHull(np.array(pts, dtype=np.int32))
                cv2.fillPoly(hand_mask, [hull], 255)

                for p in pts:
                    cv2.circle(hand_mask, tuple(p), adaptive_buffer, 255, -1)

        # In Namaste Pose: Bridge both hands into a single continuous convex polygon
        if is_namaste and len(all_hand_pts) >= 6:
            namaste_hull = cv2.convexHull(np.array(all_hand_pts, dtype=np.int32))
            cv2.fillPoly(hand_mask, [namaste_hull], 255)
            close_kernel_size = max(5, int(min(w, h) * 0.012))
            close_kernel_size = close_kernel_size if close_kernel_size % 2 == 1 else close_kernel_size + 1
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_kernel_size, close_kernel_size))
            hand_mask = cv2.morphologyEx(hand_mask, cv2.MORPH_CLOSE, kernel)

        # Adaptive final dilation
        dilate_size = max(3, int(min(w, h) * 0.006))
        dilate_size = dilate_size if dilate_size % 2 == 1 else dilate_size + 1
        d_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilate_size, dilate_size))
        hand_mask = cv2.dilate(hand_mask, d_kernel, iterations=1)

        return hand_mask

    def build_face_and_head_protection_mask(
        self,
        image_shape: Tuple[int, int],
        landmarks: Optional[Any],
        schp_atr: Optional[np.ndarray] = None,
        schp_lip: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Builds a resolution-adaptive head, face, eyeglasses, hair, beard, and neck protection mask (uint8: 0 or 255).
        """
        h, w = image_shape[:2]
        head_mask = np.zeros((h, w), dtype=np.uint8)

        # 1. Integrate SCHP Face, Hair, and Sunglasses
        if schp_atr is not None:
            head_mask |= (get_unified_part_mask(schp_atr, "face", DatasetType.ATR) * 255)
            head_mask |= (get_unified_part_mask(schp_atr, "hair", DatasetType.ATR) * 255)
            head_mask |= (get_part_mask(schp_atr, ["Sunglasses", "Hat"], DatasetType.ATR) * 255)
        if schp_lip is not None:
            head_mask |= (get_unified_part_mask(schp_lip, "face", DatasetType.LIP) * 255)
            head_mask |= (get_unified_part_mask(schp_lip, "hair", DatasetType.LIP) * 255)
            head_mask |= (get_part_mask(schp_lip, ["Sunglasses", "Hat"], DatasetType.LIP) * 255)

        # 2. Geometric Face & Neck Anchor via MediaPipe
        if landmarks is not None:
            lm = landmarks
            nose_y = int(lm[0].y * h)
            nose_x = int(lm[0].x * w)
            mouth_y = int(max(lm[9].y, lm[10].y) * h)
            chin_y = int(mouth_y + max((mouth_y - nose_y) * 1.4, h * 0.04))

            # Shoulder landmarks define lateral head and neck scale
            l_sh_x, l_sh_y = int(lm[11].x * w), int(lm[11].y * h)
            r_sh_x, r_sh_y = int(lm[12].x * w), int(lm[12].y * h)
            shoulder_width = max(abs(r_sh_x - l_sh_x), int(w * 0.20))

            # Protect face & cranium with an ellipse so rectangular corners do not clip shoulders/collar
            face_rx = max(12, int(shoulder_width * 0.28))
            face_cy = max(0, int(nose_y - max((mouth_y - nose_y) * 0.3, h * 0.015)))
            face_ry = max(20, int(chin_y - face_cy))
            cv2.ellipse(head_mask, (nose_x, face_cy), (face_rx, face_ry), 0, 0, 360, 255, -1)
            crown_top = max(0, face_cy - face_ry)
            head_mask[:crown_top + int(face_ry * 0.4), max(0, nose_x - face_rx):min(w, nose_x + face_rx)] = 255

            # Protect neck triangle down to clavicle line only where SCHP does not detect clothing
            clavicle_y = int(min(l_sh_y, r_sh_y) + (max(l_sh_y, r_sh_y) - min(l_sh_y, r_sh_y)) * 0.5)
            clavicle_y = max(clavicle_y, chin_y)
            neck_half_w = int(shoulder_width * 0.14)
            neck_mask = np.zeros((h, w), dtype=np.uint8)
            neck_pts = np.array([
                [nose_x - neck_half_w, chin_y],
                [nose_x + neck_half_w, chin_y],
                [nose_x + int(neck_half_w * 0.7), clavicle_y],
                [nose_x - int(neck_half_w * 0.7), clavicle_y]
            ], dtype=np.int32)
            cv2.fillPoly(neck_mask, [neck_pts], 255)
            if schp_atr is not None:
                neck_mask[get_unified_part_mask(schp_atr, "upper_clothes", DatasetType.ATR) > 0] = 0
            if schp_lip is not None:
                cloth_lip = (
                    (get_unified_part_mask(schp_lip, "upper_clothes", DatasetType.LIP) > 0)
                    | (get_part_mask(schp_lip, ["Coat"], DatasetType.LIP) > 0)
                )
                neck_mask[cloth_lip] = 0
            head_mask |= neck_mask

        return head_mask

    def estimate_pose_aware_waistline(
        self,
        image_shape: Tuple[int, int],
        landmarks: Optional[Any],
        schp_atr: Optional[np.ndarray] = None,
        schp_lip: Optional[np.ndarray] = None
    ) -> int:
        """
        Computes the anatomical boundary between upper torso garments and lower trousers/skirts.
        Returns the integer Y-coordinate (pixel row).
        """
        h, w = image_shape[:2]

        # 1. Hip joint baseline from MediaPipe
        y_hip = None
        if landmarks is not None:
            lm = landmarks
            l_hip_vis = lm[23].visibility > 0.25
            r_hip_vis = lm[24].visibility > 0.25
            if l_hip_vis and r_hip_vis:
                y_hip = int(((lm[23].y + lm[24].y) / 2.0) * h)
            elif l_hip_vis:
                y_hip = int(lm[23].y * h)
            elif r_hip_vis:
                y_hip = int(lm[24].y * h)

        # 2. Pants / Skirt top boundary from SCHP
        pants_mask = np.zeros((h, w), dtype=np.uint8)
        if schp_atr is not None:
            pants_mask |= get_unified_part_mask(schp_atr, "pants", DatasetType.ATR)
            pants_mask |= get_unified_part_mask(schp_atr, "skirt", DatasetType.ATR)
        if schp_lip is not None:
            pants_mask |= get_unified_part_mask(schp_lip, "pants", DatasetType.LIP)
            pants_mask |= get_unified_part_mask(schp_lip, "skirt", DatasetType.LIP)

        pants_y_indices = np.where(pants_mask > 0)[0]
        if len(pants_y_indices) > 0:
            schp_pants_top = int(np.percentile(pants_y_indices, 2))
            if y_hip is not None:
                return int(np.clip(schp_pants_top, y_hip - int(h * 0.08), y_hip + int(h * 0.08)))
            return schp_pants_top

        if y_hip is not None:
            return y_hip

        return int(h * 0.52)

    # =========================================================================
    # PHASE 2: INDIAN FASHION INTELLIGENCE EXTENSIONS
    # =========================================================================

    def estimate_garment_hemline(
        self,
        image_shape: Tuple[int, int],
        landmarks: Optional[Any],
        garment_sub_type: str = "shirt",
        schp_atr: Optional[np.ndarray] = None,
        schp_lip: Optional[np.ndarray] = None,
        hemline_profile: Optional[str] = None
    ) -> int:
        """
        Dynamically calculates the lower hemline boundary (Y-coordinate pixel row) for upper-body garments.
        Supports:
        - 'cropped' (saree_blouse, choli): stops at ribcage above waist.
        - 'waist_length' (t_shirt, standard shirt): stops at pose-aware waistline.
        - 'hip_length' (nehru_jacket, modi_vest, blazer): extends past waist to mid-hip.
        - 'mid_thigh' (short kurta, pathani): midpoint between hip and knee.
        - 'knee_length' (kurta, sherwani, achkan): extends all the way down to MediaPipe knees (landmarks 25/26).
        """
        h, w = image_shape[:2]
        y_waist = self.estimate_pose_aware_waistline(image_shape, landmarks, schp_atr, schp_lip)

        # 1. Resolve effective profile
        profile = hemline_profile
        if not profile:
            if garment_sub_type in {"saree_blouse", "choli"}:
                profile = "cropped"
            elif garment_sub_type in {"nehru_jacket", "modi_vest", "blazer", "jacket"}:
                profile = "hip_length"
            elif garment_sub_type in {"kurta", "kurti", "sherwani", "achkan", "anarkali"}:
                profile = "knee_length"
            else:
                profile = "waist_length"

        # 2. Case: Cropped (Saree Blouse / Choli)
        if profile == "cropped":
            # Ends approx 8% of height above the waistline
            return max(int(h * 0.35), y_waist - int(h * 0.08))

        # 3. Case: Waist-length (Shirt / T-shirt)
        if profile == "waist_length":
            return y_waist

        # 4. Extract hip and knee coordinates for extended profiles
        y_hip = y_waist
        y_knee = None

        if landmarks is not None:
            lm = landmarks
            # Hip coordinates
            l_hip_vis = lm[23].visibility > 0.20
            r_hip_vis = lm[24].visibility > 0.20
            if l_hip_vis and r_hip_vis:
                y_hip = int(((lm[23].y + lm[24].y) / 2.0) * h)
            elif l_hip_vis:
                y_hip = int(lm[23].y * h)
            elif r_hip_vis:
                y_hip = int(lm[24].y * h)

            # Knee coordinates: MediaPipe 25 (LEFT_KNEE), 26 (RIGHT_KNEE)
            l_knee_vis = lm[25].visibility > 0.20
            r_knee_vis = lm[26].visibility > 0.20
            if l_knee_vis and r_knee_vis:
                y_knee = int(((lm[25].y + lm[26].y) / 2.0) * h)
            elif l_knee_vis:
                y_knee = int(lm[25].y * h)
            elif r_knee_vis:
                y_knee = int(lm[26].y * h)

        if y_knee is None:
            # Anthropometric fallback: knees are approx 74% of height in full body
            y_knee = min(h - 1, int(h * 0.74))

        # Ensure knee is below hip
        if y_knee <= y_hip:
            y_knee = min(h - 1, int(y_hip + h * 0.25))

        # 5. Case: Hip-length (Nehru Jacket / Modi Vest / Blazer)
        if profile == "hip_length":
            return min(h - 1, int(y_hip + h * 0.06))

        # 6. Case: Mid-thigh (Short Kurta / Tunic)
        if profile == "mid_thigh":
            return min(h - 1, int(y_hip + 0.50 * (y_knee - y_hip)))

        # 7. Case: Knee-length (Standard Kurta / Sherwani / Achkan)
        # Sits slightly above or at the knee cap, protecting lower leg trousers/churidar
        knee_buffer = int(h * 0.02)
        return min(h - 1, max(y_hip, y_knee - knee_buffer))

    def build_sleeve_lock_mask(
        self,
        image_shape: Tuple[int, int],
        landmarks: Optional[Any],
        schp_atr: Optional[np.ndarray] = None,
        schp_lip: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Builds a sleeve & arm protection mask (uint8: 0 or 255) for multi-garment layering.
        When layering a sleeveless Nehru Jacket or Modi Vest over a Kurta/shirt:
        Subtracting this mask ensures existing sleeves are 100% locked and preserved.
        """
        h, w = image_shape[:2]
        sleeve_mask = np.zeros((h, w), dtype=np.uint8)

        # 1. Semantic arm pixels from SCHP ATR and LIP
        if schp_atr is not None:
            sleeve_mask |= (get_unified_part_mask(schp_atr, "arms", DatasetType.ATR) * 255)
        if schp_lip is not None:
            sleeve_mask |= (get_unified_part_mask(schp_lip, "arms", DatasetType.LIP) * 255)

        # 2. Geometric skeletal corridor from MediaPipe (Shoulder -> Elbow -> Wrist)
        if landmarks is not None:
            lm = landmarks
            arm_pairs = [
                (11, 13, 15),  # Left: Shoulder -> Elbow -> Wrist
                (12, 14, 16)   # Right: Shoulder -> Elbow -> Wrist
            ]
            sh_width = abs(lm[11].x - lm[12].x) * w
            corridor_thickness = max(8, int(sh_width * 0.22))

            for sh_idx, el_idx, wr_idx in arm_pairs:
                if lm[sh_idx].visibility > 0.20 and lm[el_idx].visibility > 0.20:
                    pt_sh = (int(lm[sh_idx].x * w), int(lm[sh_idx].y * h))
                    pt_el = (int(lm[el_idx].x * w), int(lm[el_idx].y * h))
                    cv2.line(sleeve_mask, pt_sh, pt_el, 255, corridor_thickness)

                if lm[el_idx].visibility > 0.20 and lm[wr_idx].visibility > 0.20:
                    pt_el = (int(lm[el_idx].x * w), int(lm[el_idx].y * h))
                    pt_wr = (int(lm[wr_idx].x * w), int(lm[wr_idx].y * h))
                    cv2.line(sleeve_mask, pt_el, pt_wr, 255, corridor_thickness)

        # Morphological closing to make sleeve coverage continuous
        k_size = max(5, int(min(w, h) * 0.015))
        k_size = k_size if k_size % 2 == 1 else k_size + 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
        sleeve_mask = cv2.morphologyEx(sleeve_mask, cv2.MORPH_CLOSE, kernel)

        return sleeve_mask

    def build_mandarin_collar_protection_mask(
        self,
        image_shape: Tuple[int, int],
        landmarks: Optional[Any],
        schp_atr: Optional[np.ndarray] = None,
        schp_lip: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Builds protection for high Bandhgala / Mandarin necklines, chin, beard, and jewelry.
        - Preserves chin, jawline, and neck accessories (Mangalsutra, necklaces, chains).
        - Leaves the clavicle collar placket open for crisp collar rendering.
        """
        h, w = image_shape[:2]
        collar_protect = np.zeros((h, w), dtype=np.uint8)

        # 1. Protect jewelry and scarves
        if schp_atr is not None:
            # ATR class 11: Scarf / tie / necklace
            collar_protect |= (get_part_mask(schp_atr, ["Scarf"], DatasetType.ATR) * 255)
        if schp_lip is not None:
            collar_protect |= (get_part_mask(schp_lip, ["Scarf"], DatasetType.LIP) * 255)

        # 2. Geometric chin and jaw protection
        if landmarks is not None:
            lm = landmarks
            nose_y = int(lm[0].y * h)
            nose_x = int(lm[0].x * w)
            mouth_y = int(max(lm[9].y, lm[10].y) * h)
            chin_y = int(mouth_y + max((mouth_y - nose_y) * 1.3, h * 0.035))

            sh_w = max(abs(int(lm[11].x * w) - int(lm[12].x * w)), int(w * 0.20))
            jaw_half_w = int(sh_w * 0.25)

            # Protect jaw area up to chin_y
            jaw_rect = np.array([
                [nose_x - jaw_half_w, nose_y],
                [nose_x + jaw_half_w, nose_y],
                [nose_x + jaw_half_w, chin_y],
                [nose_x - jaw_half_w, chin_y]
            ], dtype=np.int32)
            cv2.fillPoly(collar_protect, [jaw_rect], 255)

        return collar_protect
