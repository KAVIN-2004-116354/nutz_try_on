"""Lightweight InsightFace (buffalo_l + INSwapper-128) face replacement engine."""

import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np
from huggingface_hub import hf_hub_download
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INSIGHTFACE_DIR = PROJECT_ROOT / "models" / "insightface"
INSWAPPER_PATH = INSIGHTFACE_DIR / "inswapper_128.onnx"
INSWAPPER_REPO = "ezioruan/inswapper_128.onnx"


def _pil_to_bgr(
    img: Image.Image, bg_rgb: Tuple[int, int, int] = (240, 240, 240)
) -> Tuple[np.ndarray, Optional[Image.Image]]:
    """Convert PIL Image to OpenCV BGR, preserving any original alpha channel."""
    has_alpha = img.mode in ("RGBA", "LA") or (
        img.mode == "P" and "transparency" in img.info
    )
    orig_alpha: Optional[Image.Image] = None
    if has_alpha:
        rgba = img.convert("RGBA")
        orig_alpha = rgba.split()[-1]
        bg = Image.new("RGBA", rgba.size, (*bg_rgb, 255))
        rgb = Image.alpha_composite(bg, rgba).convert("RGB")
    else:
        rgb = img.convert("RGB")
    return cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2BGR), orig_alpha


class FaceSwapEngine:
    """Replaces the face on a garment/model photo with the user's face."""

    def __init__(self, model_dir: Path = INSIGHTFACE_DIR) -> None:
        self.model_dir = Path(model_dir)
        self._lock = threading.Lock()
        self._face_app: Optional[FaceAnalysis] = None
        self._swapper: Optional[Any] = None

    def _ensure_loaded(self) -> None:
        if self._face_app is not None and self._swapper is not None:
            return
        with self._lock:
            if self._face_app is not None and self._swapper is not None:
                return
            self.model_dir.mkdir(parents=True, exist_ok=True)
            swapper_file = self.model_dir / "inswapper_128.onnx"
            if not swapper_file.exists():
                hf_hub_download(
                    repo_id=INSWAPPER_REPO,
                    filename="inswapper_128.onnx",
                    local_dir=str(self.model_dir),
                )

            import torch  # local import avoids heavy torch overhead during fast gateway health checks
            from rembg import new_session, remove
            from scipy.ndimage import binary_fill_holes, distance_transform_edt
            from src.models.CatVTON.model.SCHP import SCHP

            schp_ckpt = Path(
                "/home/lenovo/ComfyUI/models/catvton/SCHP/exp-schp-201908301523-atr.pth"
            )
            if not schp_ckpt.exists():
                raise FileNotFoundError(
                    f"SCHP-ATR weights not found at {schp_ckpt} for full head segmentation."
                )

            # CPUExecutionProvider & CPU PyTorch avoid VRAM contention with ComfyUI on 8GB GPUs.
            providers = ["CPUExecutionProvider"]
            face_app = FaceAnalysis(
                name="buffalo_l",
                root=str(self.model_dir),
                allowed_modules=["detection", "landmark_2d_106"],
                providers=providers,
            )
            face_app.prepare(ctx_id=-1, det_size=(640, 640), det_thresh=0.45)

            self._face_app = face_app
            self._schp = SCHP(ckpt_path=str(schp_ckpt), device="cpu")
            self._rembg_session = new_session("u2net", providers=providers)
            self._rembg_remove = remove
            self._torch = torch
            self._binary_fill_holes = binary_fill_holes
            self._distance_transform_edt = distance_transform_edt
            self._swapper = "head_swap"

    def _detect_primary_face(self, img_bgr: np.ndarray, role_label: str) -> Any:
        assert self._face_app is not None
        faces = self._face_app.get(img_bgr)
        if not faces:
            # Retry with border padding so faces touching crop edges still trigger SCRFD.
            pad = 64
            padded = cv2.copyMakeBorder(
                img_bgr, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(240, 240, 240)
            )
            faces = self._face_app.get(padded)
            for face in faces:
                face.bbox = face.bbox - pad
                if getattr(face, "kps", None) is not None:
                    face.kps = face.kps - pad
                if getattr(face, "landmark_2d_106", None) is not None:
                    face.landmark_2d_106 = face.landmark_2d_106 - pad

        if not faces:
            raise ValueError(
                f"No face detected in the {role_label}. Please upload a clear photo showing the face."
            )

        return max(
            faces,
            key=lambda f: float((f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])),
        )

    @staticmethod
    def _lower_jaw_curve(width: int, lmk_local: np.ndarray) -> np.ndarray:
        """Interpolate a strictly monotonic left-to-right lower jawline from InsightFace 106-pt landmarks."""
        lower_jaw_order = [16, 2, 3, 4, 5, 6, 7, 8, 0, 24, 23, 22, 21, 20, 19, 18]
        pts = lmk_local[lower_jaw_order]
        order = np.argsort(pts[:, 0])
        jx, jy = pts[order, 0], pts[order, 1]
        xs = np.arange(width, dtype=np.float32)
        return np.interp(xs, jx, jy, left=jy[0], right=jy[-1])

    @staticmethod
    def _decontaminate_foreground(bgr: np.ndarray, alpha: np.ndarray) -> np.ndarray:
        """Replace semi-transparent background fringe colors with inner foreground pixel tones."""
        core = cv2.erode((alpha >= 0.94).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(
            np.float32
        )
        num = cv2.GaussianBlur(bgr.astype(np.float32) * core[..., None], (19, 19), 0)
        den = cv2.GaussianBlur(core, (19, 19), 0)[..., None]
        est = np.where(den > 1e-4, num / np.maximum(den, 1e-4), bgr.astype(np.float32))
        edge = (np.clip((0.96 - alpha) / 0.35, 0.0, 1.0) * (alpha > 0.01))[..., None]
        out = bgr.astype(np.float32) * (1.0 - edge) + est * edge
        return np.clip(out, 0, 255).astype(np.uint8)

    def _prepare_source_bgr_and_alpha(
        self, pil_img: Image.Image
    ) -> tuple[np.ndarray, Optional[np.ndarray]]:
        """Extract BGR image and optional clean pre-cutout alpha without halo color bleeding."""
        has_alpha = pil_img.mode in ("RGBA", "LA") or ("transparency" in pil_img.info)
        orig_alpha: Optional[np.ndarray] = None
        if has_alpha:
            rgba = pil_img.convert("RGBA")
            alpha_arr = np.asarray(rgba.split()[3], dtype=np.float32) / 255.0
            rgb = np.asarray(rgba.convert("RGB"))
            if alpha_arr.min() < 0.98:
                orig_alpha = alpha_arr
                solid = orig_alpha > 0.75
                if solid.sum() > 100 and (~solid).sum() > 0:
                    iy, ix = self._distance_transform_edt(
                        ~solid, return_distances=False, return_indices=True
                    )
                    rgb = np.where(solid[..., None], rgb, rgb[iy, ix])
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), orig_alpha
        bgr, _ = _pil_to_bgr(pil_img)
        return bgr, None

    def _parse_head_roi(
        self,
        bgr: np.ndarray,
        bbox: np.ndarray,
        orig_alpha: Optional[np.ndarray] = None,
    ) -> tuple[tuple[int, int, int, int], np.ndarray, np.ndarray, np.ndarray]:
        """Crop an upper-body ROI around the detected face and run SCHP-ATR + rembg matting."""
        h, w = bgr.shape[:2]
        x1, y1, x2, y2 = bbox
        fw, fh = x2 - x1, y2 - y1
        cx = 0.5 * (x1 + x2)
        rx0 = max(0, int(cx - 1.9 * fw))
        rx1 = min(w, int(cx + 1.9 * fw))
        ry0 = max(0, int(y1 - 1.3 * fh))
        ry1 = min(h, int(y2 + 1.1 * fh))
        roi = bgr[ry0:ry1, rx0:rx1].copy()

        # SCHP preprocess converts PIL->ndarray expecting BGR channel order.
        with self._torch.no_grad():
            atr = np.asarray(self._schp(Image.fromarray(roi)), dtype=np.uint8)

        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        rgba = np.asarray(self._rembg_remove(Image.fromarray(roi_rgb), session=self._rembg_session))
        fg_alpha = rgba[:, :, 3].astype(np.float32) / 255.0
        if orig_alpha is not None:
            fg_alpha = np.minimum(fg_alpha, orig_alpha[ry0:ry1, rx0:rx1])
        return (rx0, ry0, rx1, ry1), roi, atr, fg_alpha

    @staticmethod
    def _clean_skin_median_lab(
        bgr: np.ndarray,
        skin_mask: np.ndarray,
        upper_y_cutoff: Optional[int] = None,
    ) -> Optional[np.ndarray]:
        """Estimate true lit human skin LAB median while filtering out facial hair and extreme shadows."""
        mask = skin_mask.copy()
        if upper_y_cutoff is not None:
            yy = np.arange(bgr.shape[0])[:, None]
            upper_mask = mask & (yy <= upper_y_cutoff)
            if upper_mask.sum() > 80:
                mask = upper_mask
        if not np.any(mask):
            return None
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        vals = lab[mask]
        valid = (vals[:, 0] > 45) & (vals[:, 0] < 245) & (vals[:, 1] >= 120) & (vals[:, 2] >= 120)
        if valid.sum() > 50:
            vals = vals[valid]
        return np.median(vals, axis=0) if len(vals) > 0 else None

    def _recolor_target_body_skin(
        self,
        tgt_bgr: np.ndarray,
        d_box: tuple[int, int, int, int],
        d_atr: np.ndarray,
        d_bbox_loc: np.ndarray,
        d_roi: np.ndarray,
        src_skin_lab: Optional[np.ndarray],
    ) -> np.ndarray:
        """Adapt all visible target neck, arm, hand, and leg skin to match the user's skin colour."""
        if src_skin_lab is None:
            return tgt_bgr

        with self._torch.no_grad():
            full_atr = np.array(self._schp(Image.fromarray(tgt_bgr)), dtype=np.uint8)
        dx0, dy0, dx1, dy1 = d_box
        full_atr[dy0:dy1, dx0:dx1] = d_atr

        d_cheek_nose_y = int(d_bbox_loc[1] + 0.68 * (d_bbox_loc[3] - d_bbox_loc[1]))
        dst_skin_lab = self._clean_skin_median_lab(d_roi, d_atr == 11, upper_y_cutoff=d_cheek_nose_y)
        if dst_skin_lab is None:
            dst_skin_lab = self._clean_skin_median_lab(
                tgt_bgr, np.isin(full_atr, [11, 12, 13, 14, 15])
            )
        if dst_skin_lab is None:
            return tgt_bgr

        src_L, src_a, src_b = [float(v) for v in src_skin_lab]
        dst_L, dst_a, dst_b = [float(v) for v in dst_skin_lab]
        if abs(src_L - dst_L) < 3.0 and abs(src_a - dst_a) < 2.0 and abs(src_b - dst_b) < 2.0:
            return tgt_bgr

        skin_classes = np.isin(full_atr, [11, 12, 13, 14, 15])
        if skin_classes.sum() < 50:
            return tgt_bgr

        tgt_lab = cv2.cvtColor(tgt_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)

        # Protect watches, bangles, collars, white shirts, and shadows inside ATR limb masks.
        da_dist = tgt_lab[..., 1] - dst_a
        db_dist = tgt_lab[..., 2] - dst_b
        chroma_dist = np.sqrt(da_dist * da_dist + db_dist * db_dist)
        chroma_keep = np.clip(1.0 - (chroma_dist - 18.0) / 14.0, 0.0, 1.0)
        lum_keep = np.clip((tgt_lab[..., 0] - 25.0) / 30.0, 0.0, 1.0)
        neutral_chroma = np.hypot(tgt_lab[..., 1] - 128.0, tgt_lab[..., 2] - 128.0)
        achroma_reject = np.clip((neutral_chroma - 4.0) / 4.0, 0.0, 1.0)
        highlight_reject = np.clip((251.0 - tgt_lab[..., 0]) / 6.0, 0.0, 1.0)

        cloth_mask = np.isin(full_atr, [1, 2, 4, 5, 6, 7, 8, 9, 10, 16, 17])
        raw_skin_w = (
            skin_classes.astype(np.float32)
            * chroma_keep
            * lum_keep
            * achroma_reject
            * highlight_reject
        )
        raw_skin_w[cloth_mask] = 0.0
        skin_w = cv2.GaussianBlur(raw_skin_w, (5, 5), 0)
        skin_w[cloth_mask] = 0.0
        skin_w = np.clip(skin_w, 0.0, 1.0)[..., None]

        dst_u = float(np.clip(dst_L / 255.0, 0.05, 0.96))
        src_u = float(np.clip(src_L / 255.0, 0.05, 0.96))
        gamma = float(np.clip(np.log(src_u) / np.log(dst_u), 0.42, 3.2))
        scale_L = float(np.clip(src_L / max(dst_L, 35.0), 0.55, 1.60))

        L_t = tgt_lab[..., 0]
        L_gamma = 255.0 * np.power(np.clip(L_t / 255.0, 1e-4, 1.0), gamma)
        L_scaled = np.clip(L_t * scale_L, 0.0, 255.0)
        L_new = 0.55 * L_gamma + 0.45 * L_scaled

        shadow_chroma_w = np.clip((L_t - 25.0) / 55.0, 0.25, 1.0)
        a_new = np.clip(tgt_lab[..., 1] + (src_a - dst_a) * 0.92 * shadow_chroma_w, 115.0, 180.0)
        b_new = np.clip(tgt_lab[..., 2] + (src_b - dst_b) * 0.92 * shadow_chroma_w, 115.0, 185.0)

        recolored_lab = tgt_lab.copy()
        recolored_lab[..., 0] = L_new
        recolored_lab[..., 1] = a_new
        recolored_lab[..., 2] = b_new
        recolored_bgr = cv2.cvtColor(
            np.clip(recolored_lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR
        )

        # Blend only on active skin pixels so untouched garment/background stay bit-exact.
        active = skin_w[..., 0] > 1e-4
        out_bgr = tgt_bgr.copy()
        if np.any(active):
            w_act = skin_w[active]
            blended = (
                tgt_bgr[active].astype(np.float32) * (1.0 - w_act)
                + recolored_bgr[active].astype(np.float32) * w_act
            )
            out_bgr[active] = np.clip(np.rint(blended), 0, 255).astype(np.uint8)
        return out_bgr

    def _build_source_head(
        self,
        s_roi: np.ndarray,
        s_atr: np.ndarray,
        s_fg: np.ndarray,
        s_lmk_loc: np.ndarray,
        s_bbox_loc: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]:
        """Isolate only the source head (hair, hat, glasses, face) above jaw/collar and extract skin colour."""
        sh, sw = s_roi.shape[:2]
        sfh = s_bbox_loc[3] - s_bbox_loc[1]
        sfw = s_bbox_loc[2] - s_bbox_loc[0]
        cx_loc = 0.5 * (s_bbox_loc[0] + s_bbox_loc[2])

        jy_s = self._lower_jaw_curve(sw, s_lmk_loc)
        yy_s = np.arange(sh, dtype=np.float32)[:, None]
        in_chin_col = np.abs(np.arange(sw)[None, :] - cx_loc) < 0.42 * sfw

        above_jaw_skin = yy_s <= (jy_s[None, :] + 0.015 * sfh)
        above_jaw_beard = yy_s <= (jy_s[None, :] + 0.04 * sfh)
        ear_line = float(max(s_lmk_loc[16, 1], s_lmk_loc[18, 1]))
        above_hair_limit = yy_s <= np.minimum(jy_s[None, :] + 0.02 * sfh, ear_line + 0.04 * sfh)

        is_cloth = np.isin(s_atr, [4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17])
        is_hair_hat = np.isin(s_atr, [1, 2])
        is_face_glass = np.isin(s_atr, [3, 11])

        keep_skin = self._binary_fill_holes(
            is_face_glass & (above_jaw_skin | (above_jaw_beard & in_chin_col))
        )
        keep_hair = is_hair_hat & above_hair_limit
        temple_y = float(min(s_lmk_loc[1, 1], s_lmk_loc[17, 1]))
        above_ear_fg = (yy_s < (temple_y + 0.25 * sfh)) & (s_fg > 0.55) & (~is_cloth)

        raw_keep = self._binary_fill_holes((keep_skin | keep_hair | above_ear_fg) & (~is_cloth))
        num_l, labels, stats, _ = cv2.connectedComponentsWithStats(raw_keep.astype(np.uint8))
        if num_l > 1:
            fcx = int(np.clip(cx_loc, 0, sw - 1))
            fcy = int(np.clip(0.5 * (s_bbox_loc[1] + s_bbox_loc[3]), 0, sh - 1))
            main_lbl = int(labels[fcy, fcx])
            if main_lbl == 0:
                main_lbl = int(np.argmax(stats[1:, cv2.CC_STAT_AREA])) + 1
            raw_keep = labels == main_lbl

        tight_fg = cv2.erode(np.clip((s_fg - 0.35) / 0.62, 0.0, 1.0), np.ones((3, 3), np.uint8))
        inner_face = cv2.erode(keep_skin.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(
            np.float32
        )
        src_alpha = np.maximum(
            tight_fg * raw_keep.astype(np.float32), inner_face * raw_keep.astype(np.float32)
        )
        keep_soft = cv2.GaussianBlur(raw_keep.astype(np.float32), (5, 5), 0)
        src_alpha = cv2.GaussianBlur(
            np.clip(np.minimum(src_alpha, keep_soft), 0.0, 1.0), (3, 3), 0
        )

        # Keep the person's authentic facial skin tone intact; only decontaminate hair/silhouette fringe.
        s_roi_clean = self._decontaminate_foreground(s_roi, src_alpha)

        s_cheek_nose_y = int(s_bbox_loc[1] + 0.68 * sfh)
        src_skin_med = self._clean_skin_median_lab(
            s_roi_clean,
            (s_atr == 11) & above_jaw_skin & (src_alpha > 0.8),
            upper_y_cutoff=s_cheek_nose_y,
        )

        return s_roi_clean, src_alpha, src_skin_med

    def _erase_exposed_target_head(
        self,
        d_roi: np.ndarray,
        d_atr: np.ndarray,
        d_fg: np.ndarray,
        d_lmk_loc: np.ndarray,
        d_bbox_loc: np.ndarray,
        warped_alpha: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Cleanly erase protruding old hair/head pixels onto pure Voronoi background without smearing clothes/chin."""
        dh, dw = d_roi.shape[:2]
        dfh = d_bbox_loc[3] - d_bbox_loc[1]
        jy_d = self._lower_jaw_curve(dw, d_lmk_loc)
        yy_d = np.arange(dh, dtype=np.float32)[:, None]
        d_above_jaw = yy_d <= (jy_d[None, :] + 0.02 * dfh)
        d_is_cloth = np.isin(d_atr, [4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17])

        # Preserve both lower neck skin and lower chin inside the jaw width so short source chins never expose wall.
        d_jaw_x0 = float(min(d_lmk_loc[16, 0], d_lmk_loc[18, 0]))
        d_jaw_x1 = float(max(d_lmk_loc[16, 0], d_lmk_loc[18, 0]))
        d_cheek_y = 0.5 * (float(d_bbox_loc[1]) + float(d_lmk_loc[0, 1]))
        xx_d = np.arange(dw, dtype=np.float32)[None, :]
        d_chin_neck_keep = (d_atr == 11) & (
            (~d_above_jaw) | ((yy_d >= d_cheek_y) & (xx_d >= d_jaw_x0) & (xx_d <= d_jaw_x1))
        )

        d_head_core = (
            np.isin(d_atr, [1, 2, 3])
            | (np.isin(d_atr, [11]) & (~d_chin_neck_keep))
            | ((d_fg > 0.08) & d_above_jaw & (~d_chin_neck_keep))
        ) & (~d_is_cloth)
        d_head_core = d_head_core & (d_above_jaw | np.isin(d_atr, [1, 2]))
        d_head_dil = (
            cv2.dilate(d_head_core.astype(np.uint8), np.ones((7, 7), np.uint8))
            & (~d_is_cloth.astype(np.uint8))
            & (~d_chin_neck_keep.astype(np.uint8))
        )

        expose_mask = (d_head_dil & (warped_alpha < 0.85).astype(np.uint8)).astype(np.uint8)
        expose_dil = (
            cv2.dilate(expose_mask, np.ones((5, 5), np.uint8))
            & (~d_is_cloth.astype(np.uint8))
            & (~d_chin_neck_keep.astype(np.uint8))
        )

        d_comp_base = d_roi.copy()
        erase_blend = np.zeros((dh, dw), dtype=np.float32)
        if expose_dil.sum() > 20:
            clean_bg = (d_atr == 0) & (d_fg < 0.04) & (~d_is_cloth) & (~d_head_dil.astype(bool))
            if clean_bg.sum() > 100:
                iy, ix = self._distance_transform_edt(
                    ~clean_bg, return_distances=False, return_indices=True
                )
                bg_canvas = d_roi[iy, ix]
            else:
                bg_canvas = d_roi.copy()
            inpainted = cv2.inpaint(bg_canvas, expose_dil, 7, cv2.INPAINT_TELEA)
            erase_blend = cv2.GaussianBlur(expose_mask.astype(np.float32), (7, 7), 0)
            erase_blend[d_is_cloth | d_chin_neck_keep] = 0.0
            eb3 = erase_blend[..., None]
            d_comp_base = np.clip(
                d_roi.astype(np.float32) * (1.0 - eb3) + inpainted.astype(np.float32) * eb3,
                0,
                255,
            ).astype(np.uint8)

        return d_comp_base, erase_blend

    def swap(
        self,
        user_face_img: Image.Image,
        garment_model_img: Image.Image,
    ) -> Dict[str, Any]:
        """Replace the full head (hair, face, hat, glasses) in ``garment_model_img`` with ``user_face_img``."""
        t0 = time.perf_counter()
        self._ensure_loaded()
        assert self._swapper is not None

        src_bgr, src_orig_alpha = self._prepare_source_bgr_and_alpha(user_face_img)
        tgt_bgr, tgt_alpha = _pil_to_bgr(garment_model_img, bg_rgb=(255, 255, 255))

        src_face = self._detect_primary_face(src_bgr, "user photo")
        tgt_face = self._detect_primary_face(
            tgt_bgr,
            "garment/model photo (head replacement requires a photo of a model wearing the outfit)",
        )

        # Estimate pure similarity alignment (scale, rotation, translation) from 5 facial anchors.
        m_sim, _ = cv2.estimateAffinePartial2D(src_face.kps, tgt_face.kps, method=cv2.LMEDS)
        if m_sim is None:
            raise ValueError("Could not align facial landmarks between source and garment photo.")

        with self._lock:
            s_box, s_roi, s_atr, s_fg = self._parse_head_roi(
                src_bgr, src_face.bbox, orig_alpha=src_orig_alpha
            )
            d_box, d_roi, d_atr, d_fg = self._parse_head_roi(tgt_bgr, tgt_face.bbox)

        rx0, ry0, _, _ = s_box
        dx0, dy0, dx1, dy1 = d_box
        dh, dw = d_roi.shape[:2]

        t_s_to_full = np.array([[1, 0, rx0], [0, 1, ry0], [0, 0, 1]], dtype=np.float64)
        t_full_to_d = np.array([[1, 0, -dx0], [0, 1, -dy0], [0, 0, 1]], dtype=np.float64)
        m_roi = (t_full_to_d @ np.vstack([m_sim, [0, 0, 1]]) @ t_s_to_full)[:2, :]

        s_lmk_loc = src_face.landmark_2d_106 - np.array([rx0, ry0])
        s_bbox_loc = src_face.bbox - np.array([rx0, ry0, rx0, ry0])
        s_roi_clean, src_head_alpha, src_skin_med = self._build_source_head(
            s_roi, s_atr, s_fg, s_lmk_loc, s_bbox_loc
        )

        d_lmk_loc = tgt_face.landmark_2d_106 - np.array([dx0, dy0])
        d_bbox_loc = tgt_face.bbox - np.array([dx0, dy0, dx0, dy0])

        with self._lock:
            recolored_tgt = self._recolor_target_body_skin(
                tgt_bgr, d_box, d_atr, d_bbox_loc, d_roi, src_skin_med
            )
        d_roi_recolored = recolored_tgt[dy0:dy1, dx0:dx1]

        warped_head = cv2.warpAffine(
            s_roi_clean,
            m_roi,
            (dw, dh),
            flags=cv2.INTER_LANCZOS4,
            borderMode=cv2.BORDER_REFLECT_101,
        )
        warped_alpha = cv2.warpAffine(
            src_head_alpha,
            m_roi,
            (dw, dh),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0.0,
        )

        d_comp_base, _ = self._erase_exposed_target_head(
            d_roi_recolored, d_atr, d_fg, d_lmk_loc, d_bbox_loc, warped_alpha
        )

        wa3 = np.clip(warped_alpha, 0.0, 1.0)[..., None]
        out_roi = np.clip(
            d_comp_base.astype(np.float32) * (1.0 - wa3) + warped_head.astype(np.float32) * wa3,
            0,
            255,
        ).astype(np.uint8)

        swapped_bgr = recolored_tgt.copy()
        swapped_bgr[dy0:dy1, dx0:dx1] = out_roi

        swapped_rgb = cv2.cvtColor(swapped_bgr, cv2.COLOR_BGR2RGB)
        out_pil = Image.fromarray(swapped_rgb)
        if tgt_alpha is not None:
            out_pil.putalpha(tgt_alpha)

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": "success",
            "lora_checkpoint_used": "InsightFace + SCHP-ATR Full HeadSwap (CPU)",
            "num_lora_tensors": 0,
            "mediapipe_detected": True,
            "inference_time_ms": elapsed_ms,
            "peak_vram_mb": 0.0,
            "tryon_image": out_pil,
            "mask_image": None,
        }


_FACE_SWAP_ENGINE: Optional[FaceSwapEngine] = None
_ENGINE_LOCK = threading.Lock()


def get_face_swap_engine() -> FaceSwapEngine:
    """Return the singleton FaceSwapEngine instance."""
    global _FACE_SWAP_ENGINE
    if _FACE_SWAP_ENGINE is None:
        with _ENGINE_LOCK:
            if _FACE_SWAP_ENGINE is None:
                _FACE_SWAP_ENGINE = FaceSwapEngine()
    return _FACE_SWAP_ENGINE

