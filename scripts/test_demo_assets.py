import requests

base = "http://127.0.0.1:8000/studio/assets/studio_demo/"
files = [
    "person_street.jpg",
    "chosen_linen_shirt.jpg",
    "chosen_denim_jacket.jpg",
    "chosen_jeans.jpg",
    "chosen_hat.jpg",
    "hat_catalog_1.jpg",
    "hat_catalog_2.jpg",
    "hat_catalog_3.jpg",
    "demo_tryon_result.jpg"
]

for f in files:
    r = requests.get(base + f)
    print(f, r.status_code, len(r.content))
