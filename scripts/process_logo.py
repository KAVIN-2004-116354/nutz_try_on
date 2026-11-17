import os
from PIL import Image
import numpy as np

src = '/home/lenovo/try_on/nutz-replacer/public/nutz_logo.jpg'
im = Image.open(src).convert('RGB')
print("Logo size:", im.size)

# Create transparent version (white text/icon, transparent background)
arr = np.array(im)
# brightness
gray = arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114

# White-on-transparent (alpha = brightness)
white_rgba = np.zeros((im.height, im.width, 4), dtype=np.uint8)
white_rgba[:, :, :3] = 255
# smooth alpha threshold
alpha = np.clip((gray.astype(float) - 20) * (255.0 / 180.0), 0, 255).astype(np.uint8)
white_rgba[:, :, 3] = alpha
Image.fromarray(white_rgba).save('/home/lenovo/try_on/nutz-replacer/public/nutz_logo_white.png')

# Dark-on-transparent (for light backgrounds: dark text/icon, transparent background)
dark_rgba = np.zeros((im.height, im.width, 4), dtype=np.uint8)
# Use #171717 as requested in the design spec
dark_rgba[:, :, 0] = 23
dark_rgba[:, :, 1] = 23
dark_rgba[:, :, 2] = 23
dark_rgba[:, :, 3] = alpha
Image.fromarray(dark_rgba).save('/home/lenovo/try_on/nutz-replacer/public/nutz_logo_dark.png')

print("Created nutz_logo_white.png and nutz_logo_dark.png successfully!")
