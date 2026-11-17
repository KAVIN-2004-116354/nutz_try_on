import os
from PIL import Image

g_dir = '/home/lenovo/try_on/frontend/assets/garments'
cloth_files = sorted([f for f in os.listdir(g_dir) if ('cloth' in f or 'mc' in f) and f.endswith(('.jpg', '.png'))])

print("Total cloth files:", len(cloth_files))
for f in cloth_files[:20]:
    p = os.path.join(g_dir, f)
    im = Image.open(p)
    print(f, im.size)
