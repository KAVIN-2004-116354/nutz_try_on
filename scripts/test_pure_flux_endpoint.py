import requests
from pathlib import Path

PROJECT_ROOT = Path("/home/lenovo/try_on")
person_path = PROJECT_ROOT / "frontend/assets/sample_person_female.jpg"

files = {
    "person_image": ("person.jpg", open(person_path, "rb"), "image/jpeg")
}
data = {
    "mode": "pure_flux",
    "prompt": "luxury emerald green silk evening anarkali gown with gold zardozi borders",
    "seed": 42
}

print("Submitting Pure FLUX try-on request to localhost:8000/api/v1/intelligent-tryon...")
resp = requests.post("http://127.0.0.1:8000/api/v1/intelligent-tryon", files=files, data=data, timeout=120)
print(f"Status Code: {resp.status_code}")
if resp.status_code == 200:
    res = resp.json()
    print("SUCCESS!")
    print(f"Model: {res.get('model_used')}")
    print(f"Mode: {res.get('grok_analysis', {}).get('mode')}")
    print(f"Resolution: {res.get('width')}x{res.get('height')}")
    print(f"Inference Time: {res.get('inference_time_ms')} ms")
    print(f"Result URL: {res.get('result_url')}")
else:
    print(f"Error: {resp.text}")
