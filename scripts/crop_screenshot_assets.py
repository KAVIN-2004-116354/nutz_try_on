from PIL import Image
import os

src_path = '/mnt/c/Users/lenovo/.gemini/antigravity/brain/e3520d9c-dced-4b88-8ad1-6250428a996d/.user_uploaded/media_1794829721083_4b045e17.png'
im = Image.open(src_path)

out_dir = '/home/lenovo/try_on/frontend/assets/studio_demo'
os.makedirs(out_dir, exist_ok=True)

# Let's inspect where the cards are:
# Person image in "1 Upload Your Photos":
# Looking at the screenshot, the photo has street background with a man in blue t-shirt and jeans.
person_crop = im.crop((175, 122, 280, 345))
person_crop.save(f"{out_dir}/person_street.jpg")

# Chosen garments strip (top right):
# 4 garments:
# 1) Linen Shirt:
g1 = im.crop((546, 100, 618, 230))
g1.save(f"{out_dir}/chosen_linen_shirt.jpg")

# 2) Studded Denim Jacket:
g2 = im.crop((624, 100, 696, 230))
g2.save(f"{out_dir}/chosen_denim_jacket.jpg")

# 3) Jeans:
g3 = im.crop((706, 100, 770, 230))
g3.save(f"{out_dir}/chosen_jeans.jpg")

# 4) Hat:
g4 = im.crop((778, 110, 852, 230))
g4.save(f"{out_dir}/chosen_hat.jpg")

# In "2 Select Garments" - the 3 hats in the grid:
# Hat 1:
h1 = im.crop((176, 526, 278, 715))
# wait! Height of im is 649, so y=526 is near bottom:
h1 = im.crop((176, 526, 278, 640))
h1.save(f"{out_dir}/hat_catalog_1.jpg")

# Hat 2:
h2 = im.crop((288, 526, 390, 640))
h2.save(f"{out_dir}/hat_catalog_2.jpg")

# Hat 3:
h3 = im.crop((400, 526, 502, 640))
h3.save(f"{out_dir}/hat_catalog_3.jpg")

# The Result image in "3 Result":
# In right card below "3 Result":
res_crop = im.crop((550, 360, 870, 990)) # wait, height is 649, let's check max y
res_crop = im.crop((550, 360, 870, 649))
res_crop.save(f"{out_dir}/demo_tryon_result.jpg")

print("Cropped assets saved successfully!")
