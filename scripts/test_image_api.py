"""Utility script to test and use the external Image Generation API (Railway / Kage7).

Loads API key and base URL from .env:
  IMAGE_API_BASE_URL=https://nutz-image1284.up.railway.app
  IMAGE_API_KEY=your_key_here
"""

import argparse
import base64
import os
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

BASE_URL = os.getenv("IMAGE_API_BASE_URL", "https://nutz-image1284.up.railway.app").rstrip("/")
API_KEY = os.getenv("IMAGE_API_KEY")


def get_headers():
    if not API_KEY:
        print("[ERROR] IMAGE_API_KEY is not set.")
        print("Please configure it in .env or run the setup command.")
        sys.exit(1)
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def list_models():
    """Verify credentials and list available models."""
    url = f"{BASE_URL}/v1/models"
    print(f"Connecting to {url} ...")
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        if response.status_code == 200:
            print("[SUCCESS] API Key is valid!")
            data = response.json()
            models = data.get("data", [])
            print(f"Available models ({len(models)}):")
            for m in models:
                mid = m.get("id") if isinstance(m, dict) else str(m)
                print(f" - {mid}")
            return True
        else:
            print(f"[FAILED] HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
        return False


def generate_image(
    prompt: str,
    model: str = "FLUX-DEV-012",
    size: str = "1024x1024",
    output_path: str = "outputs/generated_test.png",
):
    """Generate an image from prompt and save to file."""
    url = f"{BASE_URL}/v1/images/generations"
    payload = {
        "prompt": prompt,
        "model": model,
        "n": 1,
        "size": size,
        "response_format": "b64_json",
    }

    print(f"Generating image with model '{model}'...")
    print(f"Prompt: {prompt}")

    try:
        response = requests.post(url, headers=get_headers(), json=payload, timeout=90)
        if response.status_code != 200:
            print(f"[ERROR] API returned {response.status_code}: {response.text}")
            return None

        result = response.json()
        data = result.get("data", [])
        if not data:
            print(f"[ERROR] No image data returned: {result}")
            return None

        img_data = data[0]
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        if "b64_json" in img_data and img_data["b64_json"]:
            image_bytes = base64.b64decode(img_data["b64_json"])
            with open(out_file, "wb") as f:
                f.write(image_bytes)
            print(f"[SUCCESS] Image saved to: {out_file}")
            return out_file
        elif "url" in img_data and img_data["url"]:
            img_url = img_data["url"]
            print(f"Downloading image from URL: {img_url} ...")
            r = requests.get(img_url, timeout=30)
            if r.status_code == 200:
                with open(out_file, "wb") as f:
                    f.write(r.content)
                print(f"[SUCCESS] Image saved to: {out_file}")
                return out_file
            else:
                print(f"[ERROR] Failed to download image from URL: HTTP {r.status_code}")
                return None
        else:
            print(f"[ERROR] Unrecognized image format in response: {img_data}")
            return None

    except Exception as e:
        print(f"[ERROR] Image generation failed: {e}")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test external image generation API.")
    parser.add_argument("--test-only", action="store_true", help="Only verify API key and list models")
    parser.add_argument("--prompt", type=str, default="A stylish fashion model wearing a high-end streetwear jacket, studio lighting, highly detailed", help="Prompt for image generation")
    parser.add_argument("--model", type=str, default="FLUX-DEV-012", help="Model name (default: FLUX-DEV-012)")
    parser.add_argument("--output", type=str, default="outputs/generated_fashion_test.png", help="Output file path")
    args = parser.parse_args()

    if args.test_only:
        list_models()
    else:
        valid = list_models()
        if valid:
            print("\nGenerating sample image...")
            generate_image(prompt=args.prompt, model=args.model, output_path=args.output)
