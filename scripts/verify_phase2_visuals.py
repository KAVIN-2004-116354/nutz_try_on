import os
import sys
import numpy as np
import cv2
from PIL import Image

sys.path.insert(0, "/home/lenovo/try_on")
from src.preprocessing.anatomy_guard import AdaptiveAnatomyGuard

img_path = "/home/lenovo/try_on/frontend/assets/sample_person_1.jpg"
out_dir = "/home/lenovo/try_on/outputs/phase2"
os.makedirs(out_dir, exist_ok=True)

img_pil = Image.open(img_path)
w, h = img_pil.size
img_np = np.array(img_pil.convert("RGB"))

guard = AdaptiveAnatomyGuard()
landmarks = guard.extract_landmarks(img_pil)

# Hemlines
y_waist = guard.estimate_pose_aware_waistline((h, w), landmarks)
y_kurta = guard.estimate_garment_hemline((h, w), landmarks, garment_sub_type="kurta")
y_nehru = guard.estimate_garment_hemline((h, w), landmarks, garment_sub_type="nehru_jacket")
y_blouse = guard.estimate_garment_hemline((h, w), landmarks, garment_sub_type="saree_blouse")

# Protection shields
hands = guard.build_hand_protection_mask((h, w), landmarks)
head = guard.build_face_and_head_protection_mask((h, w), landmarks)
sleeve_lock = guard.build_sleeve_lock_mask((h, w), landmarks)
mandarin = guard.build_mandarin_collar_protection_mask((h, w), landmarks)

print(f"Image Resolution: {w}x{h}")
print(f"Saree Blouse Hemline: y={y_blouse}px")
print(f"Standard Shirt Hemline: y={y_waist}px")
print(f"Nehru Jacket Hemline: y={y_nehru}px")
print(f"Knee-Length Kurta Hemline: y={y_kurta}px")

# Create annotated visualization
comp = img_np.copy()

# Draw hemline lines
cv2.line(comp, (0, y_blouse), (w, y_blouse), (255, 105, 180), 3) # Pink = Saree Blouse
cv2.putText(comp, f"Saree Blouse (Cropped): y={y_blouse}px", (20, y_blouse - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 105, 180), 2)

cv2.line(comp, (0, y_waist), (w, y_waist), (0, 0, 255), 3)       # Red = Shirt Waistline
cv2.putText(comp, f"Western Shirt (Waistline): y={y_waist}px", (20, y_waist - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

cv2.line(comp, (0, y_nehru), (w, y_nehru), (0, 165, 255), 3)    # Orange = Nehru Jacket
cv2.putText(comp, f"Nehru Jacket (Hip-Length): y={y_nehru}px", (20, y_nehru - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

cv2.line(comp, (0, y_kurta), (w, y_kurta), (0, 255, 0), 3)      # Green = Kurta Knee
cv2.putText(comp, f"Indian Kurta (Knee-Length): y={y_kurta}px", (20, y_kurta - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

# Overlay Namaste hand protection shield in semi-transparent cyan
hand_overlay = comp.copy()
hand_overlay[hands > 0] = [0, 255, 255] # Cyan
comp = cv2.addWeighted(comp, 0.7, hand_overlay, 0.3, 0)

# Overlay Sleeve-Lock protection shield in semi-transparent yellow
sleeve_overlay = comp.copy()
sleeve_overlay[sleeve_lock > 0] = [255, 255, 0] # Yellow
comp = cv2.addWeighted(comp, 0.8, sleeve_overlay, 0.2, 0)

out_comp_path = os.path.join(out_dir, "phase2_indian_fashion_visualization.png")
cv2.imwrite(out_comp_path, cv2.cvtColor(comp, cv2.COLOR_RGB2BGR))
print(f"Saved visualization to: {out_comp_path}")

