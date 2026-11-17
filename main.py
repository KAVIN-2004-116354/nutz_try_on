from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, Query
from fastapi.responses import Response, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import urllib.request
import urllib.parse
import urllib.error
import json
import time
import os
import sys
import shutil
import base64
import io
import cv2
import numpy as np
import torch
from PIL import Image

# Add src to path for internal modules
sys.path.append(os.path.abspath("src"))
from preprocessing.classifier import classify_garment
from preprocessing.pose_target import analyze_posture, get_segformer

def isolate_garment_if_model_photo(garment_path: str) -> str:
    """
    If the uploaded garment image is a catalog photo of a human model wearing the garment,
    segments the garment using SegFormer and places it on a clean neutral white background.
    Prevents the reference model's posture, limbs, or background from leaking into Leffa.
    """
    try:
        posture = analyze_posture(garment_path)
        has_skeleton = posture.get("skeleton") is not None
        if has_skeleton:
            g_pil = Image.open(garment_path).convert("RGB")
            w, h = g_pil.size
            processor, model = get_segformer()
            device = "cuda" if torch.cuda.is_available() else "cpu"
            inputs = processor(images=g_pil, return_tensors="pt").to(device)
            with torch.no_grad():
                outputs = model(**inputs)
                logits = torch.nn.functional.interpolate(outputs.logits.cpu(), size=(h, w), mode="bilinear", align_corners=False)
                pred_seg = logits.argmax(dim=1)[0].numpy()

            garment_labels = [1, 2, 3, 4, 5, 6, 28, 29, 30, 32, 33, 34, 36]
            is_garment = np.isin(pred_seg, garment_labels)
            if np.any(is_garment):
                np_g = np.array(g_pil)
                isolated = np.full_like(np_g, 255)
                isolated[is_garment] = np_g[is_garment]
                isolated_path = garment_path.replace(".png", "_isolated.png").replace(".jpg", "_isolated.png")
                Image.fromarray(isolated).save(isolated_path, format="PNG")
                return isolated_path
    except Exception:
        pass
    return garment_path

MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB max image upload size

app = FastAPI(
    title="Nutz Try On Leffa Commercial API",
    description="Enterprise API Gateway powering Photorealistic 2D Diffusion Virtual Try-On (ComfyUI-Leffa + SegFormer)",
    version="2.2.0"
)

# Enable CORS for embeddable Shopify & web widgets
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COMFYUI_URL = "http://127.0.0.1:8189"  # ComfyUI Leffa port
DEMO_API_KEY = "nutz_demo_live_key_2026"

# In-memory metrics tracking
metrics = {
    "total_requests": 0,
    "successful_renders": 0,
    "latencies": []
}

# Mount static frontend (2D Studio & Widget assets)
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/studio", StaticFiles(directory=frontend_dir, html=True), name="studio")

# Mount outputs directory
outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(outputs_dir, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=outputs_dir), name="outputs")

@app.get("/")
def home():
    return RedirectResponse(url="/demo")

@app.get("/demo")
def demo_store():
    return RedirectResponse(url="/studio/demo_store.html")

@app.get("/health")
def health_check():
    comfy_ok = False
    try:
        urllib.request.urlopen(f"{COMFYUI_URL}/system_stats", timeout=3)
        comfy_ok = True
    except Exception:
        pass
    return {
        "status": "healthy" if comfy_ok else "degraded",
        "service": "Nutz Try On Leffa API",
        "version": "2.2.0",
        "comfyui_backend": "connected" if comfy_ok else "unavailable",
        "timestamp": time.time()
    }

@app.get("/api/v1/analytics")
def get_analytics():
    avg_latency = (
        round(sum(metrics["latencies"]) / len(metrics["latencies"]), 2)
        if metrics["latencies"] else 0.0
    )
    return {
        "service": "Nutz Try On Leffa",
        "total_requests": metrics["total_requests"],
        "successful_renders": metrics["successful_renders"],
        "average_latency_seconds": avg_latency,
        "success_rate": f"{(metrics['successful_renders'] / max(metrics['total_requests'], 1) * 100):.1f}%"
    }

def queue_prompt(prompt):
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
    response = urllib.request.urlopen(req, timeout=10)
    return json.loads(response.read())

def get_history(prompt_id):
    req = urllib.request.Request(f"{COMFYUI_URL}/history/{prompt_id}")
    response = urllib.request.urlopen(req, timeout=10)
    return json.loads(response.read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    req = urllib.request.Request(f"{COMFYUI_URL}/view?{url_values}")
    response = urllib.request.urlopen(req)
    return response.read()

@app.post("/api/v1/classify-garment")
async def classify_product(garment_image: UploadFile = File(...)):
    filename = os.path.basename(garment_image.filename or "garment.jpg")
    content = await garment_image.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds maximum upload size")

    try:
        img = Image.open(io.BytesIO(content))
        img.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image format")

    temp_dir = os.path.expanduser("~/ComfyUI/input")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"temp_{int(time.time()*1000)}_{filename}")
    try:
        with open(temp_path, "wb") as f:
            f.write(content)
        result = classify_garment(temp_path)
        return JSONResponse(result)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

@app.post("/v1/try-on")
@app.post("/api/v1/try-on")
async def generate_try_on(
    person_image: UploadFile = File(...),
    garment_image: UploadFile = File(...),
    domain: str = Form("indian_ethnic"),
    category: str = Form(None),
    steps: int = Form(25),
    format: str = Query("json"),
    x_api_key: str = Header(None)
):
    """
    Nutz Try On ComfyUI-Leffa Production Endpoint
    - Auto-classifies garment category
    - Dispatches to ComfyUI-Leffa inference pipeline
    - Saves result to workspace outputs and Windows Desktop
    """
    start_time = time.time()
    metrics["total_requests"] += 1

    domain_clean = (domain or "indian_ethnic").lower().strip()
    domain_mode = "indian_ethnic" if domain_clean in ("indian", "ethnic", "ethnic_wear", "indian_ethnic") else "western"

    if category and category.strip().lower() in ("string", "auto", "none", "null", ""):
        category = None

    valid_categories = {"upper_body", "lower_body", "full_body"}
    if category and category.strip().lower() not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category '{category}'")
    if category:
        category = category.strip().lower()

    person_bytes = await person_image.read()
    garment_bytes = await garment_image.read()

    if not person_bytes or not garment_bytes:
        raise HTTPException(status_code=400, detail="Both person_image and garment_image must not be empty")

    if len(person_bytes) > MAX_UPLOAD_SIZE or len(garment_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="Image exceeds maximum upload limit")

    for name, b in [("person_image", person_bytes), ("garment_image", garment_bytes)]:
        try:
            test_img = Image.open(io.BytesIO(b))
            test_img.verify()
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid or corrupted image uploaded for {name}")

    # 1. Save uploaded images to ComfyUI input folder
    input_dir = os.path.expanduser("~/ComfyUI/input")
    os.makedirs(input_dir, exist_ok=True)

    run_id = f"{int(time.time()*1000)}"
    person_filename = f"person_{run_id}.png"
    garment_filename = f"garment_{run_id}.png"

    person_path = os.path.join(input_dir, person_filename)
    garment_path = os.path.join(input_dir, garment_filename)

    Image.open(io.BytesIO(person_bytes)).convert("RGB").save(person_path, format="PNG")
    Image.open(io.BytesIO(garment_bytes)).convert("RGB").save(garment_path, format="PNG")

    # 2. Automatically classify garment
    classification = classify_garment(garment_path, category_override=category)

    # 3. Load and update the Leffa workflow blueprint
    workflow_path = "leffa_workflow_api.json"
    if not os.path.exists(workflow_path):
        raise HTTPException(status_code=500, detail="Leffa workflow blueprint leffa_workflow_api.json not found in ~/try_on directory")

    with open(workflow_path, "r") as f:
        prompt = json.load(f)

    clean_garment_path = isolate_garment_if_model_photo(garment_path)
    clean_garment_filename = os.path.basename(clean_garment_path)

    # Patch input images for Leffa nodes
    if "10" in prompt:
        prompt["10"]["inputs"]["image"] = person_filename
    if "11" in prompt:
        prompt["11"]["inputs"]["image"] = clean_garment_filename

    # Patch Leffa parameters dynamically
    if "3" in prompt:
        prompt["3"]["inputs"]["model_type"] = "VITON-HD"
        cat = classification.get("category")
        if cat == "upper_body":
            prompt["3"]["inputs"]["garment_type"] = "Upper"
        elif cat == "lower_body":
            prompt["3"]["inputs"]["garment_type"] = "Lower"
        else:
            prompt["3"]["inputs"]["garment_type"] = "Overall"

    if "4" in prompt:
        prompt["4"]["inputs"]["filename_prefix"] = f"Leffa_ComfyUI_{run_id}"

    # 4. Dispatch request to ComfyUI
    try:
        prompt_response = queue_prompt(prompt)
        prompt_id = prompt_response["prompt_id"]
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to dispatch to ComfyUI Leffa engine: {str(e)}")

    # 5. Poll for completion
    timeout_limit = 180
    history = {}
    while time.time() - start_time < timeout_limit:
        try:
            history = get_history(prompt_id)
            if prompt_id in history:
                entry = history[prompt_id]
                status_obj = entry.get("status", {})
                if status_obj.get("status_str") == "error":
                    msgs = status_obj.get("messages", [])
                    raise HTTPException(status_code=500, detail=f"ComfyUI node execution failed: {msgs}")
                if entry.get("outputs"):
                    break
        except HTTPException:
            raise
        except Exception:
            pass
        time.sleep(1)

    # 6. Extract and return the final image
    if prompt_id in history:
        history_data = history[prompt_id]
        outputs = history_data.get("outputs", {})
        for node_id, node_output in outputs.items():
            if "images" in node_output and len(node_output["images"]) > 0:
                image_info = node_output["images"][0]
                image_bytes = get_image(image_info["filename"], image_info["subfolder"], image_info["type"])

                latency = round(time.time() - start_time, 2)
                metrics["successful_renders"] += 1
                metrics["latencies"].append(latency)

                latest_out_path = os.path.join(outputs_dir, "nutz_tryon_latest.png")
                with open(latest_out_path, "wb") as f:
                    f.write(image_bytes)

                desktop_dir = "/mnt/c/Users/lenovo/Desktop"
                if os.path.exists(desktop_dir):
                    try:
                        shutil.copyfile(latest_out_path, os.path.join(desktop_dir, "nutz_tryon_latest.png"))
                    except Exception:
                        pass

                if format == "raw":
                    return Response(
                        content=image_bytes,
                        media_type="image/png",
                        headers={
                            "X-Inference-Latency-Seconds": str(latency),
                            "X-Detected-Category": classification["category"],
                            "X-Result-Url": "/outputs/nutz_tryon_latest.png"
                        }
                    )

                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                data_uri = f"data:image/png;base64,{image_b64}"
                return JSONResponse({
                    "status": "success",
                    "domain": domain_mode,
                    "result_url": f"/outputs/nutz_tryon_latest.png?t={int(time.time())}",
                    "image_data": data_uri,
                    "latency_seconds": latency,
                    "category": classification["category"],
                    "sleeve_type": classification.get("sleeve_type", "short_sleeve")
                })

    raise HTTPException(status_code=500, detail="Inference timed out or Leffa output image was not generated")
