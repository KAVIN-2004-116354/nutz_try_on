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

r = requests.get(f"{base_url}/openapi.json", headers=headers, timeout=10)
schema = r.json()

print("--- /api/image-tasks/edits ---")
print(json.dumps(schema.get("paths", {}).get("/api/image-tasks/edits", {}), indent=2))

# Search for any references to reference_image or image in schemas
print("\n--- All Path Names in Schema ---")
for p in schema.get("paths", {}):
    print(p)
