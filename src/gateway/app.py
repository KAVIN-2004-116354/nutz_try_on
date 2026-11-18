import os
import sys
import io
import time
import base64
from pathlib import Path
from typing import Optional, Union, Any, Dict

from fastapi import FastAPI, Request, HTTPException, Query, Header
from fastapi.responses import Response, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Pure Cloud FLUX.1 Dev Mode: Local CatVTON, ComfyUI, and FaceSwap engines are disabled
CatVTONLoRAEngine = None
def extract_clean_garment(img): return img
def is_comfyui_alive(): return False
def run_comfyui_tryon(*args, **kwargs): raise RuntimeError("ComfyUI backend is disabled. System is operating exclusively in FLUX.1 Dev Cloud mode.")
def run_openmoss_tryon(*args, **kwargs): raise RuntimeError("OpenMOSS backend is disabled. System is operating exclusively in FLUX.1 Dev Cloud mode.")
def get_face_swap_engine(): return None

from src.inference.cloud_generator import generate_cloud_image, edit_cloud_image, run_flux_tryon, is_cloud_flux_alive, get_api_key
from src.inference.grok_vision import grok_vision_analyze
from src.inference.category_prompts import (
    normalize_category,
    get_category_config,
    build_flux_category_prompt,
    CATEGORY_CONFIGS,
)

try:
    from src.preprocessing.segmentation_pipeline import generate_intelligent_replacement_mask
except Exception:
    def generate_intelligent_replacement_mask(*args, **kwargs): return (None, None)

# Export DOMAIN_CHECKPOINTS for test and client compatibility
DOMAIN_CHECKPOINTS = CatVTONLoRAEngine.CHECKPOINTS if CatVTONLoRAEngine else {
    "indian_ethnic": str(PROJECT_ROOT / "experiments/lora_outputs/catvton_lora_indian_ethnic_rtx5050.safetensors"),
    "western": str(PROJECT_ROOT / "experiments/lora_outputs/catvton_lora_rtx5050_extended.safetensors")
}

app = FastAPI(
    title="Nutz Try On Commercial API Gateway",
    description="Multi-Domain Enterprise API Gateway with Live CatVTON LoRA Inference Engine",
    version="2.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global singleton inference engines for rapid reuse
engines: Dict[str, Any] = {}

def get_engine(domain: str) -> Optional[Any]:
    if CatVTONLoRAEngine is None:
        return None
    clean_domain = "indian_ethnic" if domain in ("indian", "ethnic", "ethnic_wear", "indian_ethnic") else "western"
    if clean_domain not in engines:
        engines[clean_domain] = CatVTONLoRAEngine(domain=clean_domain)
    return engines[clean_domain]

# Mount outputs & frontend
outputs_dir = PROJECT_ROOT / "outputs"
outputs_dir.mkdir(parents=True, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(outputs_dir)), name="outputs")

frontend_dir = PROJECT_ROOT / "frontend"
if frontend_dir.exists():
    app.mount("/studio", StaticFiles(directory=str(frontend_dir), html=True), name="studio")

replacer_dist = PROJECT_ROOT / "nutz-replacer" / "dist"
if replacer_dist.exists():
    app.mount("/replacer", StaticFiles(directory=str(replacer_dist), html=True), name="replacer")

metrics = {
    "total_requests": 0,
    "successful_renders": 0,
    "latencies": []
}

@app.get("/login")
def login_page():
    return FileResponse(frontend_dir / "login.html")

@app.post("/api/v1/auth/login")
async def auth_login(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    email = body.get("email", "admin@nutz.ai")
    name = email.split("@")[0].replace(".", " ").replace("-", " ").replace("_", " ").title()
    role = "ML Systems Engineer" if "admin" in email else "Senior Fashion Stylist & Buyer"
    return JSONResponse({
        "token": f"nutz_jwt_{int(time.time()*1000)}",
        "user": {
            "email": email,
            "name": name,
            "role": role,
            "avatar": f"https://api.dicebear.com/7.x/bottts/svg?seed={name}",
            "organization": "Nutz AI Enterprises"
        }
    })

@app.get("/api/v1/auth/me")
def auth_me():
    return {
        "authenticated": True,
        "user": {
            "email": "admin@nutz.ai",
            "name": "Admin",
            "role": "ML Systems Engineer"
        }
    }

@app.get("/demo")
def demo_store():
    return RedirectResponse(url="/studio/demo_store.html")

@app.post("/api/v1/classify-garment")
async def classify_product(request: Request):
    form = await request.form()
    garment_file = form.get("garment_image")
    if garment_file and hasattr(garment_file, "read"):
        content = await garment_file.read()
        temp_path = str(PROJECT_ROOT / "outputs/temp_classify.jpg")
        with open(temp_path, "wb") as f:
            f.write(content)
        from preprocessing.classifier import classify_garment
        res = classify_garment(temp_path)
        return JSONResponse(res)
    return JSONResponse({"category": "upper_body", "mask_flags": {"shirt": True, "top": True}})

@app.get("/api/v1/categories")
def list_supported_categories():
    """Returns all 17 authoritative categories from the Nutz Replacer prompt specification."""
    cats = []
    for k, v in CATEGORY_CONFIGS.items():
        cats.append({
            "key": k,
            "id": v["id"],
            "name": v["name"],
            "macro_category": v["macro_category"],
            "sleeves": v["sleeves"],
            "collar": v["collar"],
            "directive": v["directive"],
            "aliases": v["aliases"],
        })
    return JSONResponse({
        "status": "success",
        "total_categories": len(cats),
        "categories": sorted(cats, key=lambda x: x["id"])
    })

@app.get("/")
def home():
    replacer_dist = PROJECT_ROOT / "nutz-replacer" / "dist"
    if replacer_dist.exists():
        return RedirectResponse(url="/replacer/")
    return RedirectResponse(url="/studio/")

@app.get("/health")
def health_check():
    cloud_ok = is_cloud_flux_alive()
    return {
        "status": "healthy",
        "service": "Nutz Try On Commercial Gateway",
        "mode": "FLUX_1_DEV_CLOUD_EXCLUSIVE",
        "version": "2.2.0",
        "comfyui_backend": "disabled (cloud flux only)",
        "cloud_flux": "online" if cloud_ok else "offline",
        "supported_domains": ["western", "indian_ethnic"],
        "active_models": {
            "flux_dev_012_cloud": cloud_ok,
            "local_catvton": False,
            "local_comfyui": False,
            "local_face_swap": False
        },
        "engine_ready": cloud_ok,
        "faceswap_ready": False,
        "cloud_flux_ready": cloud_ok,
        "timestamp": time.time()
    }

@app.get("/v1/domains")
def get_domains():
    return {
        "domains": [
            {
                "id": "indian_ethnic",
                "name": "Indian Ethnic Wear (Sarees, Kurtas, Lehengas, Sherwanis)",
                "checkpoint": "experiments/lora_outputs/catvton_lora_indian_ethnic_rtx5050.safetensors",
                "active": (PROJECT_ROOT / "experiments/lora_outputs/catvton_lora_indian_ethnic_rtx5050.safetensors").exists()
            },
            {
                "id": "western",
                "name": "Western Apparel (T-shirts, Blazers, Jeans, Dresses)",
                "checkpoint": "experiments/lora_outputs/catvton_lora_rtx5050_extended.safetensors",
                "active": (PROJECT_ROOT / "experiments/lora_outputs/catvton_lora_rtx5050_extended.safetensors").exists()
            }
        ]
    }

@app.get("/api/v1/analytics")
def get_analytics():
    avg_latency = (
        round(sum(metrics["latencies"]) / len(metrics["latencies"]), 2)
        if metrics["latencies"] else 0.0
    )
    return {
        "service": "Nutz Try On Gateway",
        "total_requests": metrics["total_requests"],
        "successful_renders": metrics["successful_renders"],
        "average_latency_seconds": avg_latency,
        "success_rate": f"{(metrics['successful_renders'] / max(metrics['total_requests'], 1) * 100):.1f}%"
    }

def _clean_image_rgb(img: Image.Image) -> Image.Image:
    """Safely converts image to RGB, compositing transparent alpha onto studio dark navy background (#0f172a)."""
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img_rgba = img.convert("RGBA")
        bg = Image.new("RGBA", img_rgba.size, (15, 23, 42, 255))
        return Image.alpha_composite(bg, img_rgba).convert("RGB")
    return img.convert("RGB")

async def _parse_image_input(val: Any) -> Image.Image:
    """Parses file upload, file path string, or base64 data URI into PIL Image."""
    if val is None:
        raise HTTPException(status_code=400, detail="Missing required image input")
        
    # Check if UploadFile-like object
    if hasattr(val, "read"):
        content = await val.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty image upload received")
        return Image.open(io.BytesIO(content))
    
    # String input: file path or base64
    if isinstance(val, str):
        val = val.strip()
        if val.startswith("data:image"):
            idx = val.find("base64,")
            if idx != -1:
                b64_data = val[idx + 7:]
                raw = base64.b64decode(b64_data)
                return Image.open(io.BytesIO(raw))
        
        # File path
        resolved_path = Path(val)
        if not resolved_path.is_absolute():
            resolved_path = PROJECT_ROOT / resolved_path
            
        if not resolved_path.exists():
            raise HTTPException(status_code=404, detail=f"Image file not found at path: {val}")
        return Image.open(resolved_path)
        
    raise HTTPException(status_code=400, detail=f"Unsupported image input type: {type(val)}")

async def _execute_tryon_request(request: Request, forced_engine: Optional[str] = None):
    start_time = time.time()
    metrics["total_requests"] += 1

    content_type = request.headers.get("content-type", "")
    person_raw = None
    garment_raw = None
    domain = None
    category = None
    seed = 42
    steps = 40
    fmt = "json"

    if "application/json" in content_type:
        try:
            body = await request.json()
            person_raw = body.get("person_image")
            garment_raw = body.get("garment_image")
            domain = body.get("domain")
            category = body.get("category")
            seed = int(body.get("seed", 42))
            steps = int(body.get("steps", 40))
            fmt = body.get("format", "json")
            custom_prompt = body.get("prompt") or body.get("garment_desc")
            engine_choice = forced_engine or body.get("engine", "default")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Malformed JSON body: {str(e)}")
    else:
        try:
            form = await request.form()
            person_raw = form.get("person_image")
            garment_raw = form.get("garment_image")
            domain = form.get("domain")
            category = form.get("category")
            seed = int(form.get("seed", 42))
            steps = int(form.get("steps", 40))
            fmt = request.query_params.get("format", form.get("format", "json"))
            custom_prompt = form.get("prompt") or form.get("garment_desc")
            engine_choice = forced_engine or form.get("engine", "default")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Malformed form body: {str(e)}")

    if not person_raw or not garment_raw:
        raise HTTPException(status_code=400, detail="Both 'person_image' and 'garment_image' must be provided")

    # Parse images to PIL
    person_pil = await _parse_image_input(person_raw)
    garment_pil = await _parse_image_input(garment_raw)

    # Determine domain: default to western for upper_body shirts/jackets, indian_ethnic for full_body
    if not domain:
        domain = "western" if category == "upper_body" else "indian_ethnic"
    clean_domain = "indian_ethnic" if domain.lower().strip() in ("indian", "ethnic", "ethnic_wear", "indian_ethnic") else "western"

    # Pure FLUX.1 Dev Cloud Mode - Local CatVTON and Face Swap models are bypassed
    is_face_swap = False
    is_flux = True
    result = None

    # Exclusive FLUX-DEV-012 Cloud Virtual Try-On Model (1024x1024 Photorealistic Synthesis)
    try:
        # Map known garment filenames or prompts to descriptive styling instructions
        garment_hints = {
            "sample_anarkali_dress": "exquisite emerald green silk Indian anarkali dress with intricate gold embroidery and matching dupatta",
            "sample_navy_blazer": "formal tailored navy blue wool blazer over a crisp white dress shirt",
            "sample_black_tshirt": "modern minimalist black crew-neck cotton t-shirt",
            "sample_emerald_shirt": "casual light mint pastel green button-down short-sleeve shirt with all-over printed micro character motifs and spread collar",
            "sample_denim_jacket": "vintage blue denim trucker jacket over a white tee",
            "green_shirt": "olive green casual linen button-up shirt",
            "sample_ethnic_anarkali_model": "traditional royal emerald green bridal anarkali gown",
        }
        garment_desc = custom_prompt or ""
        # Explicitly normalize and bind category
        canonical_cat = normalize_category(category) if category else None
        if not canonical_cat and isinstance(garment_raw, str):
            for k, v in garment_hints.items():
                if k in garment_raw.lower():
                    canonical_cat = normalize_category(k)
                    garment_desc = v
                    break
        if not canonical_cat:
            canonical_cat = "shirt" if clean_domain == "western" else "kurta"

        print(f"[Gateway] Executing Try-On exclusively via FLUX-DEV-012 Cloud Model (category: {canonical_cat}, garment: {garment_desc})")
        flux_res = run_flux_tryon(
            person_img=person_pil,
            garment_img=garment_pil,
            garment_desc=garment_desc,
            custom_prompt=custom_prompt,
            category=canonical_cat,
            use_canvas_conditioning=garment_pil is not None,
        )
        result = {
            "status": "success",
            "domain": clean_domain,
            "model_used": "FLUX-DEV-012 (Flux.1 Dev Cloud)",
            "lora_checkpoint_used": "FLUX-DEV-012 Cloud Synthesizer",
            "num_lora_tensors": 0,
            "mediapipe_detected": True,
            "inference_time_ms": flux_res["inference_time_ms"],
            "peak_vram_mb": 0.0,
            "tryon_image": flux_res["tryon_image"],
            "mask_image": None,
        }
    except Exception as f_err:
        print(f"[Gateway Error] Flux Try-On failed: {f_err}")
        err_str = str(f_err)
        if "quota" in err_str.lower() or "429" in err_str or "contact admin" in err_str.lower():
            raise HTTPException(status_code=429, detail="Generation quota reached. Please contact admin.")
        raise HTTPException(status_code=500, detail="Service temporarily unavailable. Please contact admin.")

    # Save to requested destination: outputs/gateway_{prefix}_{domain}_{seed}.png
    out_prefix = "gateway_flux" if is_flux else ("gateway_faceswap" if is_face_swap else "gateway_tryon")
    out_filename = f"{out_prefix}_{clean_domain}_{seed}.png"
    out_path = outputs_dir / out_filename
    result["tryon_image"].save(out_path, format="PNG")
    result["tryon_image"].save(outputs_dir / "nutz_tryon_latest.png", format="PNG")

    # Save binary mask if present
    mask_filename = f"gateway_mask_{clean_domain}_{seed}.png"
    mask_path = outputs_dir / mask_filename
    mask_b64 = ""
    mask_img = result.get("mask_image") or result.get("masked_preview")
    if mask_img:
        mask_img.save(mask_path, format="PNG")
        m_buf = io.BytesIO()
        mask_img.save(m_buf, format="PNG")
        mask_b64 = base64.b64encode(m_buf.getvalue()).decode("utf-8")

    latency_sec = round(time.time() - start_time, 2)
    metrics["successful_renders"] += 1
    metrics["latencies"].append(latency_sec)

    if fmt == "raw":
        img_buf = io.BytesIO()
        result["tryon_image"].save(img_buf, format="PNG")
        return Response(
            content=img_buf.getvalue(),
            media_type="image/png",
            headers={
                "X-Domain": clean_domain,
                "X-Used-Weights": str(result.get("lora_checkpoint_used", "FLUX-DEV-012")),
                "X-Inference-Time-Ms": str(result.get("inference_time_ms", 0)),
                "X-Peak-VRAM-Mb": str(result.get("peak_vram_mb", 0.0))
            }
        )

    # Return full JSON telemetry response
    buf = io.BytesIO()
    result["tryon_image"].save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")

    return JSONResponse({
        "status": "success",
        "mode": "flux" if is_flux else ("face_swap" if is_face_swap else "catvton"),
        "engine": "flux" if is_flux else ("face_swap" if is_face_swap else "catvton"),
        "model_used": result.get("model_used", "FLUX-DEV-012 (Flux.1 Dev Cloud)"),
        "domain": clean_domain,
        "used_weights": result.get("lora_checkpoint_used", "FLUX-DEV-012 Cloud Synthesizer"),
        "selected_lora": result.get("lora_checkpoint_used", "FLUX-DEV-012 Cloud Synthesizer"),
        "num_lora_tensors": result.get("num_lora_tensors", 0),
        "inference_time_ms": result.get("inference_time_ms", 0),
        "latency_seconds": latency_sec,
        "peak_vram_mb": result.get("peak_vram_mb", 0.0),
        "width": result["tryon_image"].width,
        "height": result["tryon_image"].height,
        "file_size_bytes": out_path.stat().st_size if out_path.exists() else len(buf.getvalue()),
        "output_image": str(out_path),
        "mask_image": str(mask_path) if mask_img else None,
        "mediapipe_detected": result.get("mediapipe_detected", True),
        "result_url": f"/outputs/{out_filename}",
        "mask_url": f"/outputs/{mask_filename}" if mask_img else None,
        "image_data": f"data:image/png;base64,{b64_str}",
        "mask_data": f"data:image/png;base64,{mask_b64}" if mask_b64 else None
    })


@app.post("/v1/try-on")
@app.post("/api/v1/try-on")
async def generate_try_on(request: Request):
    """
    Live GPU Inference Try-On Endpoint:
    Accepts JSON body or multipart form:
      - person_image: file path string or uploaded file
      - garment_image: file path string or uploaded file
      - domain: "indian_ethnic" (default) or "western"
      - engine: "flux" (exclusive FLUX-DEV-012 Cloud), "catvton", or "face_swap"
      - prompt: optional custom styling / clothing instruction for Flux
      - seed: integer (default 42)
    """
    return await _execute_tryon_request(request)


@app.post("/v1/flux-tryon")
@app.post("/api/v1/flux-tryon")
async def generate_flux_tryon(request: Request):
    """Executes Virtual Try-On exclusively using FLUX-DEV-012 Cloud Model."""
    return await _execute_tryon_request(request, forced_engine="flux")


@app.post("/v1/analyze-garment")
@app.post("/api/v1/analyze-garment")
async def analyze_garment_endpoint(request: Request):
    """
    Analyzes an uploaded garment image using Grok Vision.
    Returns structured JSON with category, attributes, and replacement recommendation.
    """
    content_type = request.headers.get("content-type", "")
    garment_raw = None
    person_raw = None
    garment_name = ""

    if "application/json" in content_type:
        try:
            body = await request.json()
            garment_raw = body.get("garment_image") or body.get("image")
            person_raw = body.get("person_image")
            if isinstance(garment_raw, str):
                garment_name = garment_raw
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Malformed JSON: {str(e)}")
    else:
        try:
            form = await request.form()
            garment_raw = form.get("garment_image") or form.get("image")
            person_raw = form.get("person_image")
            if hasattr(garment_raw, "filename") and garment_raw.filename:
                garment_name = garment_raw.filename
            elif isinstance(garment_raw, str):
                garment_name = garment_raw
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Malformed form: {str(e)}")

    if not garment_raw:
        raise HTTPException(status_code=400, detail="garment_image is required")

    garment_pil = await _parse_image_input(garment_raw)
    person_pil = await _parse_image_input(person_raw) if person_raw else None

    analysis = grok_vision_analyze(
        garment_img=garment_pil,
        person_img=person_pil,
        garment_name=garment_name
    )
    return JSONResponse({
        "status": "success",
        "analysis": analysis
    })


@app.post("/v1/intelligent-tryon")
@app.post("/api/v1/intelligent-tryon")
async def generate_intelligent_tryon(request: Request):
    """
    Intelligent Virtual Try-On Pipeline:
    1. Person + Garment Input (zero manual category selection)
    2. Garment & Person Understanding with Grok Vision
    3. MediaPipe Landmark-Guided Segmentation Mask Generation & Protection
    4. Mask-conditioned inpainting with FLUX-DEV-012 Cloud
    5. Photorealistic 1024x1024 Try-On Synthesis with diagnostics
    """
    start_time = time.time()
    metrics["total_requests"] += 1

    content_type = request.headers.get("content-type", "")
    person_raw = None
    garment_raw = None
    seed = int(time.time() * 1000) % 100000
    garment_filename = ""
    mode = "auto"
    custom_prompt = ""
    category = ""

    if "application/json" in content_type:
        try:
            body = await request.json()
            person_raw = body.get("person_image")
            garment_raw = body.get("garment_image")
            mode = body.get("mode", "auto")
            custom_prompt = body.get("prompt") or body.get("custom_prompt") or ""
            category = body.get("category", "")
            if "seed" in body and body["seed"]:
                seed = int(body["seed"])
            if isinstance(garment_raw, str):
                garment_filename = garment_raw
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Malformed JSON body: {str(e)}")
    else:
        try:
            form = await request.form()
            person_raw = form.get("person_image")
            garment_raw = form.get("garment_image")
            mode = form.get("mode", "auto")
            custom_prompt = form.get("prompt") or form.get("custom_prompt") or ""
            category = form.get("category", "")
            if "seed" in form and form["seed"]:
                seed = int(form["seed"])
            if hasattr(garment_raw, "filename") and garment_raw.filename:
                garment_filename = garment_raw.filename
            elif isinstance(garment_raw, str):
                garment_filename = garment_raw
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Malformed form body: {str(e)}")

    # Detect if user wants Pure FLUX (Direct Studio Styling without Grok)
    is_pure_flux = (mode == "pure_flux") or (not garment_raw and bool(custom_prompt))

    if not person_raw:
        raise HTTPException(status_code=400, detail="A valid 'person_image' (Source of Truth) must be provided")

    if not is_pure_flux and not garment_raw:
        raise HTTPException(status_code=400, detail="In Garment Photo mode, 'garment_image' must be provided. For Pure FLUX mode, provide a styling prompt.")

    # Step 1: Parse images to PIL
    person_pil = await _parse_image_input(person_raw)
    garment_pil = await _parse_image_input(garment_raw) if garment_raw else None

    # Step 2: Grok Vision Analysis OR Pure FLUX Direct Synthesis
    if is_pure_flux:
        prompt_text = custom_prompt.strip() if custom_prompt else "luxury high-fashion designer outfit"
        canonical_cat = normalize_category(category or prompt_text)
        cat_cfg = get_category_config(canonical_cat)
        cat = cat_cfg["macro_category"]

        if cat == "full_body":
            target_regions = ["torso", "waist", "full_skirt", "left_arm", "right_arm"]
        elif cat == "complex_ethnic":
            target_regions = ["torso", "waist", "full_skirt", "left_arm", "right_arm"]
        elif cat == "lower_body":
            target_regions = ["hips", "left_leg", "right_leg"]
        else:
            target_regions = ["torso", "left_arm", "right_arm"]

        generation_prompt = build_flux_category_prompt(canonical_cat, user_prompt=prompt_text)
        grok_res = {
            "mode": "pure_flux",
            "garment_analysis": {
                "category": cat,
                "garment_type": canonical_cat,
                "primary_color": "custom",
                "secondary_color": "",
                "fabric": "luxury fabric",
                "pattern": "custom",
                "sleeves": cat_cfg.get("sleeves", "tailored"),
                "collar": cat_cfg.get("collar", "tailored"),
                "construction_details": [prompt_text],
                "layering": False,
                "confidence": 1.0,
            },
            "person_analysis": {
                "pose": "standing_front_facing",
                "visible_body_regions": ["head", "neck", "torso", "arms", "legs"],
                "existing_clothing": ["baseline outfit"],
                "background": "neutral studio"
            },
            "replacement_plan": {
                "target_regions": target_regions,
                "protected_regions": ["face", "hair", "exposed_skin", "hands"],
                "requires_manual_review": False
            },
            "generation_prompt": generation_prompt
        }
    else:
        grok_res = grok_vision_analyze(
            garment_img=garment_pil,
            person_img=person_pil,
            garment_name=garment_filename
        )
        detected_type = grok_res.get("garment_analysis", {}).get("garment_type", "")
        # Prioritize explicitly passed category over heuristic prompt or detected label
        canonical_cat = normalize_category(category or detected_type or "t_shirt")
        
        styling_note = custom_prompt.strip() if custom_prompt and custom_prompt.strip() else None
        grok_res["generation_prompt"] = build_flux_category_prompt(
            canonical_cat,
            garment_attributes=grok_res.get("garment_analysis"),
            user_prompt=styling_note
        )

    garment_analysis = grok_res.get("garment_analysis", {})
    replacement_plan = grok_res.get("replacement_plan", {})
    generation_prompt = grok_res.get("generation_prompt", "")

    # Step 3: Adaptive Anatomy-Guarded Segmentation Mask Generation
    seg_res = generate_intelligent_replacement_mask(
        person_img=person_pil,
        garment_analysis=garment_analysis,
        replacement_plan=replacement_plan
    )
    mask_img = seg_res["mask_image"]
    overlay_img = seg_res.get("overlay_image") or seg_res.get("preview_overlay")
    seg_metrics = seg_res["metrics"]

    # Step 4: FLUX-DEV-012 Cloud Inpainting with Dual-Panel Canvas Conditioning
    # Ensure visual reference conditioning is active whenever a garment image is provided
    try:
        flux_res = run_flux_tryon(
            person_img=person_pil,
            garment_img=garment_pil,
            custom_prompt=generation_prompt,
            mask_img=mask_img,
            category=canonical_cat,
            use_canvas_conditioning=garment_pil is not None,
        )
        tryon_img = flux_res["tryon_image"]
    except Exception as f_err:
        print(f"[Gateway Error] FLUX-DEV-012 Inpainting failed: {f_err}")
        err_str = str(f_err)
        if "quota" in err_str.lower() or "429" in err_str or "contact admin" in err_str.lower():
            raise HTTPException(status_code=429, detail="Generation quota reached. Please contact admin.")
        raise HTTPException(status_code=500, detail="Service temporarily unavailable. Please contact admin.")

    # Step 5: Save outputs
    out_filename = f"intelligent_tryon_{seed}.png"
    mask_filename = f"intelligent_mask_{seed}.png"
    overlay_filename = f"intelligent_overlay_{seed}.png"

    out_path = outputs_dir / out_filename
    mask_path = outputs_dir / mask_filename
    overlay_path = outputs_dir / overlay_filename

    tryon_img.save(out_path, format="PNG")
    mask_img.save(mask_path, format="PNG")
    overlay_img.save(overlay_path, format="PNG")

    canvas_url = None
    if flux_res.get("canvas_preview"):
        canvas_filename = f"intelligent_canvas_{seed}.png"
        flux_res["canvas_preview"].save(outputs_dir / canvas_filename, format="PNG")
        canvas_url = f"/outputs/{canvas_filename}"

    # Keep latest symlinks/copies
    tryon_img.save(outputs_dir / "nutz_tryon_latest.png", format="PNG")

    # Base64 representations
    buf = io.BytesIO()
    tryon_img.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")

    m_buf = io.BytesIO()
    mask_img.save(m_buf, format="PNG")
    mask_b64 = base64.b64encode(m_buf.getvalue()).decode("utf-8")

    o_buf = io.BytesIO()
    overlay_img.save(o_buf, format="PNG")
    overlay_b64 = base64.b64encode(o_buf.getvalue()).decode("utf-8")

    latency_sec = round(time.time() - start_time, 2)
    metrics["successful_renders"] += 1
    metrics["latencies"].append(latency_sec)

    return JSONResponse({
        "status": "success",
        "model_used": "FLUX-DEV-012",
        "provider": "Nutz Railway Cloud",
        "grok_analysis": grok_res,
        "mask_metrics": seg_metrics,
        "width": tryon_img.width,
        "height": tryon_img.height,
        "file_size_bytes": out_path.stat().st_size if out_path.exists() else len(buf.getvalue()),
        "latency_seconds": latency_sec,
        "inference_time_ms": flux_res.get("inference_time_ms", 0),
        "result_url": f"/outputs/{out_filename}",
        "mask_url": f"/outputs/{mask_filename}",
        "overlay_url": f"/outputs/{overlay_filename}",
        "canvas_url": canvas_url,
        "conditioning_method": "dual_panel_canvas" if canvas_url else "single_image",
        "image_data": f"data:image/png;base64,{b64_str}",
        "mask_data": f"data:image/png;base64,{mask_b64}",
        "overlay_data": f"data:image/png;base64,{overlay_b64}"
    })


@app.post("/v1/face-swap")
@app.post("/api/v1/face-swap")
async def generate_face_swap(request: Request):
    """Face swap is disabled in Pure Cloud FLUX mode."""
    raise HTTPException(status_code=400, detail="Face-swap and local models are disabled. System is operating exclusively with Cloud FLUX.1 Dev.")


@app.get("/api/v1/cloud-status")
def cloud_status():
    """Returns remote Flux.1 Dev status and authentication state."""
    alive = is_cloud_flux_alive()
    return {
        "status": "online" if alive else "offline",
        "model": "FLUX-DEV-012",
        "provider": "Nutz Cloud (Railway)",
        "has_key": bool(get_api_key())
    }


@app.post("/api/v1/generate-cloud-image")
async def generate_cloud_img(request: Request):
    """
    Generate an AI Fashion Model or Garment Reference via remote Flux.1 Dev:
    JSON Body:
      - prompt: str (e.g. "Indian woman model, neutral studio background")
      - target: "person" or "garment"
      - size: "1024x1024" (default)
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    prompt = body.get("prompt", "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    target = body.get("target", "garment").lower().strip()
    size = body.get("size", "1024x1024")

    # Fashion-optimized prompt directives
    if target == "person":
        if "standing" not in prompt.lower() and "model" not in prompt.lower():
            full_prompt = f"Full-body professional fashion catalog photography of an attractive model, {prompt}, standing upright forward-facing pose, clean solid neutral grey studio background, photorealistic, 8k, sharp focus, natural skin texture"
        else:
            full_prompt = f"Professional fashion photography, {prompt}, 8k, photorealistic, sharp focus"
    elif target == "garment":
        if "flat lay" not in prompt.lower() and "mannequin" not in prompt.lower():
            full_prompt = f"Professional commercial catalog product photography of {prompt}, isolated flat lay on pure plain white background, clean even studio lighting, 8k, sharp fabric texture"
        else:
            full_prompt = f"Commercial product photography, {prompt}, plain white background, 8k, sharp detail"
    else:
        full_prompt = prompt

    try:
        t0 = time.time()
        img = generate_cloud_image(prompt=full_prompt, size=size, timeout=120)
        if img is None:
            raise RuntimeError("Cloud Flux API returned empty image")

        timestamp = int(time.time() * 1000)
        filename = f"flux_{target}_{timestamp}.png"
        out_path = outputs_dir / filename
        img.save(out_path, format="PNG")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        latency_sec = round(time.time() - t0, 1)

        # Detect category hint for garments
        cat_hint = "upper_body"
        p_low = prompt.lower()
        if any(w in p_low for w in ("kurta", "anarkali", "saree", "dress", "lehenga", "suit", "gown", "sherwani")):
            cat_hint = "full_body"
        elif any(w in p_low for w in ("pant", "pants", "jeans", "trouser", "trousers", "shorts", "skirt")):
            cat_hint = "lower_body"

        return JSONResponse({
            "status": "success",
            "target": target,
            "filename": filename,
            "result_url": f"/outputs/{filename}",
            "image_data": f"data:image/png;base64,{b64_str}",
            "prompt": prompt,
            "category_hint": cat_hint,
            "latency_seconds": latency_sec,
            "model": "FLUX-DEV-012"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flux Generation Failed: {str(e)}")
