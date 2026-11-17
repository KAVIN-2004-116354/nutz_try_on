import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

base_url = os.getenv("IMAGE_API_BASE_URL", "https://nutz-image1284.up.railway.app").rstrip("/")
api_key = os.getenv("IMAGE_API_KEY")
headers = {"Authorization": f"Bearer {api_key}"}

for p in ["/version", "/api/settings"]:
    try:
        r = requests.get(f"{base_url}{p}", headers=headers, timeout=5)
        print(f"GET {p} ({r.status_code}):", r.text[:300])
    except Exception as e:
        print(f"GET {p} error:", e)
