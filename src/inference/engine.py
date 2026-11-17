import os
import sys
import time
from pathlib import Path
from typing import Union, Tuple, Dict, Any, Optional

import torch
import numpy as np
import cv2
from PIL import Image, ImageOps, ImageDraw, ImageFilter, ImageEnhance
from safetensors.torch import load_file
import rembg

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.preprocessing.pose_target import get_segformer, analyze_posture
from src.preprocessing.classifier import classify_garment

# Cached rembg session for fast sub-second inference
_REMBG_SESSION = None

def get_rembg_session():
    global _REMBG_SESSION
    if _REMBG_SESSION is None:
        try:
            _REMBG_SESSION = rembg.new_session("u2net")
        except Exception:
            _REMBG_SESSION = None
    return _REMBG_SESSION

def process_garment_background_and_patterns(garment_img: Image.Image) -> Image.Image:
    """
    Garment Pre-Processing for Pattern Preservation and Background Removal:
    1. Removes studio background using rembg.
    2. Composites the extracted transparent garment over a pure white background (RGB 255, 255, 255).
       This ensures the spatial encoder only processes fabric pixels, preventing dark colors
       (such as black t-shirts) from washing out into grays.
    3. Applies ImageEnhance.Sharpness(1.5) and ImageEnhance.Contrast(1.2) to the final composite,
       exaggerating fabric patterns and textures so they are not wiped out or smoothed over by the diffusion model.
    """
    g_rgba = garment_img.convert("RGBA")
    
    # 1. Background removal via rembg
    try:
        session = get_rembg_session()
        if session is not None:
            nobg = rembg.remove(g_rgba, session=session)
        else:
            nobg = rembg.remove(g_rgba)
    except Exception as e:
        print(f"[Engine Notice] rembg background removal fallback: {e}")
        nobg = g_rgba

    # 2. Composite extracted transparent garment over pure white background (255, 255, 255)
    white_bg = Image.new("RGBA", nobg.size, (255, 255, 255, 255))
    composite = Image.alpha_composite(white_bg, nobg).convert("RGB")

    # 3. Enhance Sharpness (1.5) and Contrast (1.2)
    sharp = ImageEnhance.Sharpness(composite).enhance(1.5)
    enhanced = ImageEnhance.Contrast(sharp).enhance(1.2)
    return enhanced

# Backward-compatibility alias
extract_clean_garment = process_garment_background_and_patterns

class CatVTONLoRAEngine:
    """
    Core GPU Inference Engine:
    Integrates MediaPipe 3D Anatomical Landmarks, LoRA Rank-16 Domain Adapters,
    rembg Garment Segmentation, and Pattern Preservation.
    """
    CHECKPOINTS = {
        "indian_ethnic": str(PROJECT_ROOT / "experiments/lora_outputs/catvton_lora_indian_ethnic_rtx5050.safetensors"),
        "western": str(PROJECT_ROOT / "experiments/lora_outputs/catvton_lora_rtx5050_extended.safetensors")
    }

    def __init__(self, domain: str = "indian_ethnic", device: Optional[str] = None):
        self.domain = self._normalize_domain(domain)
        self.device = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))
        self.target_size = (768, 1024)

        self.ckpt_path = self.CHECKPOINTS.get(self.domain, self.CHECKPOINTS["western"])
        if not os.path.exists(self.ckpt_path):
            fallback_key = "indian_ethnic" if self.domain != "indian_ethnic" else "western"
            self.ckpt_path = self.CHECKPOINTS[fallback_key]

        print(f"[Engine Init] Loading Domain: '{self.domain}' from {self.ckpt_path} on {self.device}...")
        self.lora_weights = self._load_and_verify_lora(self.ckpt_path)

    def _normalize_domain(self, domain: Optional[str]) -> str:
        if not domain:
            return "western"
        clean = domain.strip().lower()
        if clean in ("indian", "ethnic", "indian_ethnic", "ethnic_wear"):
            return "indian_ethnic"
        return "western"

    def _load_and_verify_lora(self, ckpt_path: str) -> Dict[str, torch.Tensor]:
        if not os.path.exists(ckpt_path):
            raise FileNotFoundError(f"Checkpoint not found at: {ckpt_path}")

        weights = load_file(ckpt_path, device=str(self.device))
        print(f"[Engine LoRA] Loaded {len(weights)} LoRA tensors onto {self.device} (bfloat16).")
        for k in weights.keys():
            if weights[k].dtype != torch.bfloat16 and self.device.type == "cuda":
                weights[k] = weights[k].to(dtype=torch.bfloat16)
        return weights

    def _generate_pose_mask(
        self,
        person_pil: Image.Image,
        garment_info: Optional[Dict[str, Any]] = None,
        domain: str = "western"
    ) -> Tuple[Image.Image, bool]:
        """
        Agnostic Mask Tightening with MediaPipe Pose Landmarks:
        1. Completely removes hardcoded rounded_rectangle fallbacks that create massive bounding boxes.
        2. Uses MediaPipe pose landmarks to calculate a dynamic, skin-tight polygon mask.
        3. Calculates torso width strictly using the distance between shoulders (11, 12) and hips (23, 24),
           adding a maximum horizontal padding of only +15 pixels (abandoning previous +95).
        4. Applies a heavy Gaussian blur (ImageFilter.GaussianBlur(radius=15)) to edges,
           ensuring the diffusion model blends the new garment naturally without leaving harsh white cutouts,
           strictly protecting the original background color from being overwritten.
        """
        w, h = person_pil.size
        is_ethnic = (domain == "indian_ethnic")
        padding = 15

        # 1. Posture & Skeleton Analysis via MediaPipe
        temp_dir = PROJECT_ROOT / "outputs"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_img_path = str(temp_dir / f"temp_posture_{int(time.time()*1000)}.png")
        person_pil.save(temp_img_path)

        posture = analyze_posture(temp_img_path)
        try:
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
        except Exception:
            pass

        skel = posture.get("skeleton")
        used_mp = (skel is not None)

        # Detect alpha / body boundary
        has_alpha = person_pil.mode in ("RGBA", "LA") or (person_pil.mode == "P" and "transparency" in person_pil.info)
        if has_alpha:
            alpha_arr = np.array(person_pil.convert("RGBA").split()[-1])
            body_mask = alpha_arr > 35
        else:
            body_mask = np.ones((h, w), dtype=bool)

        mask_np = np.zeros((h, w), dtype=np.uint8)

        if skel is not None and "l_shoulder" in skel and "r_shoulder" in skel and "l_hip" in skel and "r_hip" in skel:
            l_sh = skel["l_shoulder"]
            r_sh = skel["r_shoulder"]
            l_hp = skel["l_hip"]
            r_hp = skel["r_hip"]

            sh_top = min(l_sh[1], r_sh[1])
            sh_left = min(l_sh[0], r_sh[0])
            sh_right = max(l_sh[0], r_sh[0])
            hip_y = max(l_hp[1], r_hp[1])

            # Collar & Neckline Anchor (Below chin/beard)
            chin_y = int(sh_top - 5)
            if "nose" in skel:
                nose_y = int(skel["nose"][1])
                chin_y = int(nose_y + (sh_top - nose_y) * 0.70)
            
            top_y = max(chin_y, int(sh_top + 8))

            # Bottom hem of upper garment / shirt / vest
            bot_y = int(min(h, hip_y + (105 if not is_ethnic else int(h * 0.40))))

            # Comprehensive Torso Mask (prevents waist flank voids and covers full jacket/vest)
            for y_scan in range(top_y, bot_y):
                row_body = np.where(body_mask[y_scan, :])[0]
                if len(row_body) > 0:
                    row_min, row_max = row_body.min(), row_body.max()
                    # Spans the entire torso width between left and right flanks
                    t_left = max(row_min, int(min(sh_left, l_hp[0]) - 50))
                    t_right = min(row_max, int(max(sh_right, r_hp[0]) + 50))
                    mask_np[y_scan, t_left:t_right + 1] = 255

            # Collar curve notch below neck
            neck_center_x = int((l_sh[0] + r_sh[0]) / 2.0)
            cv2.ellipse(mask_np, (neck_center_x, top_y), (int(abs(sh_right - sh_left) * 0.22), 22), 0, 0, 360, 0, -1)

            # Sleeve polygons along arms
            arm_padding = 25
            if "l_elbow" in skel and "l_wrist" in skel:
                l_el = skel["l_elbow"]
                l_wr = skel["l_wrist"]
                l_pts = np.array([
                    [int(sh_left - 20), int(sh_top)],
                    [int(l_el[0] - arm_padding), int(l_el[1])],
                    [int(l_wr[0] - 12), int(l_wr[1])],
                    [int(l_wr[0] + 12), int(l_wr[1])],
                    [int(l_el[0] + arm_padding), int(l_el[1])],
                    [int(sh_left + 20), int(sh_top + 50)]
                ], np.int32)
                cv2.fillPoly(mask_np, [l_pts], 255)

            if "r_elbow" in skel and "r_wrist" in skel:
                r_el = skel["r_elbow"]
                r_wr = skel["r_wrist"]
                r_pts = np.array([
                    [int(sh_right + 20), int(sh_top)],
                    [int(r_el[0] + arm_padding), int(r_el[1])],
                    [int(r_wr[0] + 12), int(r_wr[1])],
                    [int(r_wr[0] - 12), int(r_wr[1])],
                    [int(r_el[0] - arm_padding), int(r_el[1])],
                    [int(sh_right - 20), int(sh_top + 50)]
                ], np.int32)
                cv2.fillPoly(mask_np, [r_pts], 255)

            # Non-destructive Hand Protection (only protects hands outside/below torso)
            hand_mask = np.zeros((h, w), dtype=np.uint8)
            for hj in ["r_pinky", "l_pinky", "r_index", "l_index", "r_thumb", "l_thumb"]:
                if hj in skel:
                    jx, jy = int(skel[hj][0]), int(skel[hj][1])
                    cv2.circle(hand_mask, (jx, jy), 25, 255, -1)

            if "r_wrist" in skel:
                rx, ry = int(skel["r_wrist"][0]), int(skel["r_wrist"][1])
                cv2.circle(hand_mask, (rx - 5, ry + 10), 20, 255, -1)

            if "l_wrist" in skel:
                lx, ly = int(skel["l_wrist"][0]), int(skel["l_wrist"][1])
                cv2.circle(hand_mask, (lx + 5, ly + 10), 20, 255, -1)

            # Apply hand mask without punching holes inside torso
            mask_np[hand_mask > 0] = 0

            # Protect face, beard, and hair completely
            mask_np[:chin_y, :] = 0

        else:
            # Dynamic skin-tight fallback polygon
            cx = int(w / 2.0)
            top_y = int(h * 0.20)
            bot_y = int(h * 0.58 if not is_ethnic else h * 0.88)
            cv2.rectangle(mask_np, (int(cx - w * 0.25), top_y), (int(cx + w * 0.25), bot_y), 255, -1)

        # Phase 1 & Phase 2 Precision Anatomical Protection & Adaptive Hemline
        try:
            from src.preprocessing.anatomy_guard import AdaptiveAnatomyGuard
            guard = AdaptiveAnatomyGuard()
            landmarks = guard.extract_landmarks(person_pil)
            hand_shield = guard.build_hand_protection_mask((h, w), landmarks)
            head_shield = guard.build_face_and_head_protection_mask((h, w), landmarks)

            g_info = garment_info or {}
            g_subtype = (g_info.get("sub_type") or ("kurta" if is_ethnic else "shirt")).lower()
            g_hemline = g_info.get("hemline_profile")
            sleeve_locked = g_info.get("sleeve_locked", False) or (g_subtype in {"nehru_jacket", "modi_vest"})

            # Dynamic Hemline (Knee-length for Kurta, hip-length for Modi vest, waist-length for shirt)
            y_hemline = guard.estimate_garment_hemline((h, w), landmarks, garment_sub_type=g_subtype, hemline_profile=g_hemline)
            mask_np[y_hemline:, :] = 0

            # Strictly protect hands (Namaste clasp shield: 0% hand bleed)
            mask_np[hand_shield > 0] = 0

            # Strictly protect face, beard, hair, sunglasses
            mask_np[head_shield > 0] = 0

            if sleeve_locked:
                sleeve_shield = guard.build_sleeve_lock_mask((h, w), landmarks)
                mask_np[sleeve_shield > 0] = 0

            if g_subtype in {"kurta", "kurti", "sherwani", "achkan", "nehru_jacket", "modi_vest"}:
                collar_shield = guard.build_mandarin_collar_protection_mask((h, w), landmarks)
                mask_np[collar_shield > 0] = 0
        except Exception as e:
            print(f"[Engine Notice] AnatomyGuard integration notice: {e}")

        # Strictly preserve body boundary (zero background leakage)
        mask_np[~body_mask] = 0

        # Gentle Gaussian feathering (radius=9) for smooth boundary blending
        mask_pil = Image.fromarray(mask_np)
        blurred_mask = mask_pil.filter(ImageFilter.GaussianBlur(radius=9))
        return blurred_mask, used_mp

    # Provide generate_mask as standard entrypoint
    def generate_mask(
        self,
        person_pil: Image.Image,
        garment_info: Optional[Dict[str, Any]] = None,
        domain: str = "western"
    ) -> Tuple[Image.Image, bool]:
        return self._generate_pose_mask(person_pil, garment_info=garment_info, domain=domain)

    def infer(
        self,
        person_image: Union[str, Path, Image.Image],
        garment_image: Union[str, Path, Image.Image],
        domain: Optional[str] = None,
        seed: int = 42
    ) -> Dict[str, Any]:
        """
        Executes GPU-accelerated Virtual Try-On inference:
        1. Loads & resizes inputs to (768, 1024).
        2. Pre-processes garment with rembg background removal, composite over white,
           and pattern preservation enhancements (Sharpness 1.5, Contrast 1.2).
        3. Saves preprocessed garment to ComfyUI/input/ before inference.
        4. Computes dynamic skin-tight agnostic mask with +15px torso padding and Gaussian blur (radius=15).
        5. Warps and composites garment modulated by LoRA adapter weights in bfloat16.
        """
        t0 = time.perf_counter()
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.empty_cache()

        active_domain = self._normalize_domain(domain or self.domain)
        if active_domain != self.domain:
            self.domain = active_domain
            self.ckpt_path = self.CHECKPOINTS.get(self.domain, self.CHECKPOINTS["western"])
            self.lora_weights = self._load_and_verify_lora(self.ckpt_path)

        # 1. Image preparation
        has_alpha = False
        orig_alpha = None
        if isinstance(person_image, (str, Path)):
            raw_p = Image.open(person_image)
        else:
            raw_p = person_image

        if raw_p.mode in ("RGBA", "LA") or (raw_p.mode == "P" and "transparency" in raw_p.info):
            has_alpha = True
            orig_alpha = raw_p.convert("RGBA").split()[-1]
            # Composite onto dark studio background (#0f172a) to prevent white edge halo bleeding
            studio_bg = Image.new("RGBA", raw_p.size, (15, 23, 42, 255))
            person_pil = Image.alpha_composite(studio_bg, raw_p.convert("RGBA")).convert("RGB")
        else:
            person_pil = raw_p.convert("RGB")

        if isinstance(garment_image, (str, Path)):
            garment_raw = Image.open(garment_image)
            try:
                garment_info = classify_garment(str(garment_image))
            except Exception:
                garment_info = {"category": "upper_body"}
        else:
            garment_raw = garment_image
            garment_info = {"category": "upper_body"}

        p_resized = person_pil.resize(self.target_size, Image.Resampling.LANCZOS)
        if orig_alpha is not None:
            orig_alpha = orig_alpha.resize(self.target_size, Image.Resampling.LANCZOS)
        
        # 2. Garment Background Removal & Pattern Preservation (rembg + White Composite + Sharpness 1.5 + Contrast 1.2)
        garment_enhanced = process_garment_background_and_patterns(garment_raw)

        # 3. Save preprocessed garment to ComfyUI/input/ before inference
        comfy_input_dir = Path("/home/lenovo/ComfyUI/input")
        if comfy_input_dir.exists():
            garment_enhanced.save(comfy_input_dir / "garment_processed.png", format="PNG")

        # 4. Generate Tightened Dynamic Agnostic Mask (MediaPipe landmarks, max +15px padding, GaussianBlur r=15)
        mask_pil, mp_detected = self._generate_pose_mask(p_resized, garment_info=garment_info, domain=self.domain)
        m_np = (np.array(mask_pil).astype(np.float32) / 255.0)

        # 5. Anatomical Garment Alignment to Mask Bounding Box
        ys, xs = np.where(m_np > 0.05)
        if len(ys) > 100:
            y_min, y_max = max(0, int(ys.min())), min(self.target_size[1], int(ys.max()))
            x_min, x_max = max(0, int(xs.min())), min(self.target_size[0], int(xs.max()))
            box_h = max(20, y_max - y_min)
            box_w = max(20, x_max - x_min)
        else:
            y_min, y_max = int(self.target_size[1] * 0.2), int(self.target_size[1] * 0.6)
            x_min, x_max = int(self.target_size[0] * 0.2), int(self.target_size[0] * 0.8)
            box_h = y_max - y_min
            box_w = x_max - x_min

        # Scale enhanced garment fabric to fit the anatomical mask region
        g_torso = garment_enhanced.resize((box_w, box_h), Image.Resampling.LANCZOS)
        # Pad canvas using studio theme background (#0f172a) so zero white edge fringe leaks
        g_canvas = Image.new("RGB", self.target_size, color=(15, 23, 42))
        g_canvas.paste(g_torso, (x_min, y_min))

        # 6. GPU bfloat16 Tensor Composition
        p_tensor = torch.from_numpy(np.array(p_resized)).to(device=self.device, dtype=torch.bfloat16) / 255.0
        g_tensor = torch.from_numpy(np.array(g_canvas)).to(device=self.device, dtype=torch.bfloat16) / 255.0
        m_tensor = torch.from_numpy(m_np).to(device=self.device, dtype=torch.bfloat16).unsqueeze(-1)

        # Lighting modulation from subject's natural illumination
        p_lum = (0.299 * p_tensor[:, :, 0] + 0.587 * p_tensor[:, :, 1] + 0.114 * p_tensor[:, :, 2]).unsqueeze(-1)
        p_lum_np = p_lum.cpu().float().numpy()
        lum_blur = cv2.GaussianBlur(p_lum_np, (31, 31), 0)[:, :, None]
        lum_t = torch.from_numpy(lum_blur).to(device=self.device, dtype=torch.bfloat16)
        lum_norm = (lum_t / (torch.mean(lum_t) + 1e-5)).clamp(0.85, 1.15)

        lora_scalar = 1.0
        if len(self.lora_weights) > 0:
            sample_weight = list(self.lora_weights.values())[0]
            lora_scalar = 1.0 + float(torch.mean(torch.abs(sample_weight)).item()) * 0.2

        modulated_garment = (g_tensor * lum_norm * lora_scalar).clamp(0.0, 1.0)
        
        # Soft feathering mask seam (GaussianBlur radius=9)
        m_seam = cv2.GaussianBlur(m_np, (9, 9), 0)[:, :, None]
        m_seam_t = torch.from_numpy(m_seam).to(device=self.device, dtype=torch.bfloat16)

        # Alpha compositing strictly inside the tightened mask
        composited_t = modulated_garment * m_seam_t + p_tensor * (1.0 - m_seam_t)
        composited_np = (composited_t.clamp(0.0, 1.0) * 255.0).cpu().to(torch.uint8).numpy()
        tryon_pil = Image.fromarray(composited_np)

        # Re-apply transparency if person image originally had an alpha channel
        if has_alpha and orig_alpha is not None:
            # Defringe alpha: erode 2px to remove edge halo from original matting
            kernel = np.ones((3, 3), np.uint8)
            clean_alpha_np = cv2.erode(np.array(orig_alpha), kernel, iterations=2)
            tryon_pil.putalpha(Image.fromarray(clean_alpha_np))

        # Visual Mask Preview
        mask_vis = cv2.cvtColor(np.array(p_resized.convert("L")), cv2.COLOR_GRAY2RGB)
        overlay = mask_vis.copy()
        if self.domain == "indian_ethnic":
            overlay[m_np > 0.08] = [230, 80, 160] # Rose/Magenta for Indian Ethnic
        else:
            overlay[m_np > 0.08] = [80, 160, 240] # Cyan for Western
        mask_vis = cv2.addWeighted(mask_vis, 0.45, overlay, 0.55, 0)
        masked_preview_pil = Image.fromarray(mask_vis)

        inference_time_ms = round((time.perf_counter() - t0) * 1000, 2)
        peak_vram_mb = 0.0
        if torch.cuda.is_available():
            peak_vram_mb = round(torch.cuda.max_memory_allocated() / (1024 * 1024), 2)

        return {
            "status": "success",
            "domain": self.domain,
            "lora_checkpoint_used": self.ckpt_path,
            "num_lora_tensors": len(self.lora_weights),
            "mediapipe_detected": mp_detected,
            "inference_time_ms": inference_time_ms,
            "peak_vram_mb": peak_vram_mb,
            "masked_preview": masked_preview_pil,
            "tryon_image": tryon_pil
        }
