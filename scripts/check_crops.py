import os
from PIL import Image

out_dir = '/home/lenovo/try_on/frontend/assets/studio_demo'
for f in os.listdir(out_dir):
    im = Image.open(os.path.join(out_dir, f))
    print(f, im.size)
