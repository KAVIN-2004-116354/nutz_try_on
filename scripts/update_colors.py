import os
import glob

components_dir = "/home/lenovo/try_on/nutz-replacer/src/components"
files = glob.glob(os.path.join(components_dir, "*.tsx"))

for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        c = fh.read()
    c_new = c.replace('#7357E8', '#5B3DF0')
    c_new = c_new.replace('#5E41DA', '#4B2EE0')
    c_new = c_new.replace('#F8F9FC', '#F5F4F8')
    c_new = c_new.replace('#F3F0FF', '#F0EDFD')
    c_new = c_new.replace('#A78BFA', '#8F77F8')
    if c != c_new:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(c_new)
        print(f"Updated colors in {os.path.basename(f)}")
