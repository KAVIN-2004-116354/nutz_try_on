import os

g_dir = '/home/lenovo/try_on/frontend/assets/garments'
files = [f for f in os.listdir(g_dir) if f.endswith('.jpg') or f.endswith('.png')]
print('Total files in garments:', len(files))
cloth_files = [f for f in files if 'cloth' in f or 'mc' in f]
print('Cloth files count:', len(cloth_files))
for f in sorted(cloth_files)[:25]:
    print(f)
