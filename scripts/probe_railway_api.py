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

print(f"Base URL: {base_url}")
print(f"API Key present: {bool(api_key)}")

endpoints = ["/v1/models", "/openapi.json", "/docs", "/health", "/"]

for ep in endpoints:
    url = f"{base_url}{ep}"
    try:
        r = requests.get(url, headers=headers, timeout=6)
        content_snippet = r.text[:200].replace("\n", " ")
        print(f"GET {ep} -> HTTP {r.status_code} | Type: {r.headers.get('content-type', 'none')} | Body: {content_snippet}")
        if ep == "/v1/models" and r.status_code == 200:
            print("Models JSON:", json.dumps(r.json(), indent=2))
        elif ep == "/openapi.json" and r.status_code == 200:
            schema = r.json()
            paths = list(schema.get("paths", {}).keys())
            print("OpenAPI Paths:", paths)
            edits_schema = schema.get("paths", {}).get("/v1/images/edits", {})
            print("Edits Schema:", json.dumps(edits_schema, indent=2))
    except Exception as e:
        print(f"GET {ep} -> Error: {e}")
