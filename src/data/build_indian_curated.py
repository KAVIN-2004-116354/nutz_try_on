import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import numpy as np

print("=== Nutz Try On: 500-Pair Curated Indian Ethnic Dataset Builder ===", flush=True)

# Initialize MediaPipe PoseLandmarker detector once
mp_detector = None
mp_model_path = Path("models/mediapipe/pose_landmarker_lite.task")
if mp_model_path.exists():
    try:
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        
        base_options = python.BaseOptions(model_asset_path=str(mp_model_path))
        options = vision.PoseLandmarkerOptions(base_options=base_options)
        mp_detector = vision.PoseLandmarker.create_from_options(options)
        print("MediaPipe Pose Landmarker successfully initialized.", flush=True)
    except Exception as e:
        print(f"Notice initializing MediaPipe detector: {e}", flush=True)

def get_mediapipe_ethnic_mask(pil_img):
    """
    Uses local MediaPipe Pose Landmarker to:
    Generate a full-drape agnostic mask covering Kurta/Saree/Sherwani hemline down to ankles
    while protecting head and hands.
    """
    w, h = pil_img.size # (768, 1024)
    mask = Image.new("L", (w, h), color=0)
    draw = ImageDraw.Draw(mask)
    
    used_mp = False
    
    if mp_detector is not None:
        try:
            import mediapipe as mp
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.array(pil_img))
            res = mp_detector.detect(mp_image)
            
            if res.pose_landmarks:
                lm = res.pose_landmarks[0]
                # 11,12: Shoulders | 23,24: Hips | 27,28: Ankles
                sh_y = min(lm[11].y, lm[12].y) * h
                hip_y = max(lm[23].y, lm[24].y) * h
                ank_y = max(lm[27].y, lm[28].y) * h
                
                left_x = min(lm[11].x, lm[12].x, lm[23].x, lm[24].x) * w
                right_x = max(lm[11].x, lm[12].x, lm[23].x, lm[24].x) * w
                
                # Ethnic wear drape mask: collar/shoulders down past knees to ankles
                m_left = max(35, int(left_x - 90))
                m_right = min(w - 35, int(right_x + 90))
                m_top = max(160, int(sh_y - 20)) # Protect head above collar
                m_bottom = min(h - 25, int(max(hip_y + 220, ank_y - 20))) # Cover full drape
                
                draw.rounded_rectangle([m_left, m_top, m_right, m_bottom], radius=32, fill=255)
                
                # Protect hands & wrists: carve out black regions around wrist/hand keypoints (15, 16, 17, 18, 19, 20)
                hand_indices = [15, 16, 17, 18, 19, 20]
                for hi in hand_indices:
                    hx, hy = lm[hi].x * w, lm[hi].y * h
                    # If hand landmark is visible and within or near mask, protect hand
                    if lm[hi].visibility > 0.4:
                        r = 38
                        draw.ellipse([hx - r, hy - r, hx + r, hy + r], fill=0)
                
                # Protect head/face: carve out anything above nose / mouth level
                nose_y = lm[0].y * h
                if nose_y > 0:
                    draw.rectangle([0, 0, w, int(nose_y + 30)], fill=0)
                    
                used_mp = True
        except Exception:
            pass

    if not used_mp:
        # Ethnic wear fallback mask (protects head y < 190, covers kurta/saree drape down to y = 935)
        draw.rounded_rectangle([120, 190, 648, 935], radius=35, fill=255)

    return mask, used_mp

def build_dataset(max_samples=500):
    raw_persons = Path("datasets/indian_raw/persons")
    raw_cloths = Path("datasets/indian_raw/cloths")
    out_root = Path("datasets/indian_viton_hd")
    
    img_dir = out_root / "train" / "image"
    cloth_dir = out_root / "train" / "cloth"
    mask_dir = out_root / "train" / "agnostic-mask"
    
    for d in [img_dir, cloth_dir, mask_dir]:
        d.mkdir(parents=True, exist_ok=True)

    person_files = sorted(list(raw_persons.glob("*.jpg")) + list(raw_persons.glob("*.png")))
    cloth_files = sorted(list(raw_cloths.glob("*.jpg")) + list(raw_cloths.glob("*.png")))

    print(f"Found {len(person_files)} raw person images and {len(cloth_files)} raw cloth images.", flush=True)
    
    target_size = (768, 1024) # (W, H) in PIL -> (3, 1024, 768) tensor shape
    pairs = []
    mp_guided_count = 0

    num_samples = min(max_samples, len(person_files))
    print(f"Processing {num_samples} Indian ethnic wear pairs at {target_size}...", flush=True)

    for idx in range(num_samples):
        p_path = person_files[idx]
        c_path = cloth_files[idx] if idx < len(cloth_files) else p_path
        
        out_name = f"ind_{idx:05d}.jpg"
        mask_name = f"ind_{idx:05d}_mask.png"
        
        p_img = Image.open(p_path).convert("RGB").resize(target_size, Image.Resampling.LANCZOS)
        c_img = Image.open(c_path).convert("RGB").resize(target_size, Image.Resampling.LANCZOS)
        
        mask, used_mp = get_mediapipe_ethnic_mask(p_img)
        if used_mp:
            mp_guided_count += 1
            
        p_img.save(img_dir / out_name, quality=95)
        c_img.save(cloth_dir / out_name, quality=95)
        mask.save(mask_dir / mask_name)
        pairs.append(f"{out_name} {out_name}")
        
        if (idx + 1) % 100 == 0:
            print(f"  -> Built {idx + 1}/{num_samples} pairs...", flush=True)

    pair_file = out_root / "train_pairs.txt"
    with open(pair_file, "w") as f:
        f.write("\n".join(pairs) + "\n")

    print(f"\n[SUCCESS] Built {len(pairs)} curated Indian ethnic training pairs in '{out_root}'", flush=True)
    print(f"MediaPipe Pose-Guided Masks applied: {mp_guided_count}/{len(pairs)}", flush=True)
    print(f"Pair index saved to: {pair_file}", flush=True)

    # Verification checks
    assert len(list(img_dir.glob("*.jpg"))) == num_samples, f"Images mismatch: {len(list(img_dir.glob('*.jpg')))}"
    assert len(list(cloth_dir.glob("*.jpg"))) == num_samples, f"Cloths mismatch: {len(list(cloth_dir.glob('*.jpg')))}"
    assert len(list(mask_dir.glob("*.png"))) == num_samples, f"Masks mismatch: {len(list(mask_dir.glob('*.png')))}"
    with open(pair_file) as f:
        pair_lines = [l.strip() for l in f if l.strip()]
    assert len(pair_lines) == num_samples, f"Pair lines mismatch: {len(pair_lines)}"
    print("[SUCCESS] Stage 2 Complete: MediaPipe Pose-Guided Ethnic Dataset verified!", flush=True)

if __name__ == "__main__":
    build_dataset(max_samples=500)
