import glob
import os
from PIL import Image

user_files = glob.glob('/mnt/c/Users/lenovo/.gemini/antigravity/brain/e3520d9c-dced-4b88-8ad1-6250428a996d/.user_uploaded/*')
for f in sorted(user_files):
    try:
        im = Image.open(f)
        print(f, im.size, im.format, os.path.getsize(f))
    except Exception as e:
        print(f, e)
