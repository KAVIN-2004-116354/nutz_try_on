from PIL import Image

im = Image.open('/mnt/c/Users/lenovo/.gemini/antigravity/brain/e3520d9c-dced-4b88-8ad1-6250428a996d/.user_uploaded/media_1794829721083_4b045e17.png')
# Sample background color around top margin
print("Top background color:", im.getpixel((50, 50)))
# Sample card background color
print("Card 1 background color:", im.getpixel((200, 100)))
# Sample blue button color
# Generate Try-On is around x=820, y=335
print("Button color:", im.getpixel((820, 335)))
# Sample active pill color
# Hat pill is around x=360, y=456
print("Active pill color:", im.getpixel((360, 456)))
