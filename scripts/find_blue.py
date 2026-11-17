from PIL import Image

im = Image.open('/mnt/c/Users/lenovo/.gemini/antigravity/brain/e3520d9c-dced-4b88-8ad1-6250428a996d/.user_uploaded/media_1794829721083_4b045e17.png')
w, h = im.size
blue_locs = []
for y in range(h):
    for x in range(w):
        r, g, b = im.getpixel((x, y))[:3]
        if b > 160 and b > r + 80 and b > g + 40:
            blue_locs.append((x, y, (r, g, b)))

print("Total blue pixels:", len(blue_locs))
if blue_locs:
    print("First 5 blue pixels:", blue_locs[:5])
    # Cluster locations:
    xs = [p[0] for p in blue_locs]
    ys = [p[1] for p in blue_locs]
    print(f"X range: {min(xs)} to {max(xs)}, Y range: {min(ys)} to {max(ys)}")
