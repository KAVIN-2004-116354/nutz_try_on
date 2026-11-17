import os
from PIL import Image

# Let's inspect frontend/assets
print("Assets in frontend/assets:")
for f in sorted(os.listdir('/home/lenovo/try_on/frontend/assets')):
    if f.endswith(('.jpg', '.png')):
        print(f)
