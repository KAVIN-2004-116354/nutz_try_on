# 👗 Virtual Try-On — MLOps Pipeline

> An end-to-end MLOps system for AI-powered virtual clothing try-on, built on **CatVTON** (Concatenation-based Virtual Try-On), orchestrated with **ZenML**, tracked with **MLflow**, versioned with **DVC**, and served via **FastAPI + ComfyUI**.

---

## 📌 Table of Contents

1. [Project Overview](#-project-overview)
2. [Architecture](#-architecture)
3. [Technology Stack](#-technology-stack)
4. [Repository Structure](#-repository-structure)
5. [Core Model — CatVTON](#-core-model--catvton)
6. [ComfyUI Workflow](#-comfyui-workflow)
7. [MLOps Layers](#-mlops-layers)
8. [API — FastAPI Server](#-api--fastapi-server)
9. [Setup & Installation](#-setup--installation)
10. [Running the Project](#-running-the-project)
11. [Key Design Decisions](#-key-design-decisions)
12. [Roadmap & Next Steps](#-roadmap--next-steps)

---

## 🧭 Project Overview

This project wraps the **CatVTON** diffusion-based virtual try-on model into a **production-grade MLOps pipeline**. Given a photo of a person and a garment image, the system generates a photorealistic image of the person wearing that garment.

**Core problem solved:** Bridging the gap between a research-grade AI model (CatVTON) and a reproducible, trackable, API-ready production system.

| Capability | Tool Used |
|---|---|
| AI Inference | CatVTON (Stable Diffusion inpainting) |
| Pipeline Orchestration | ZenML |
| Experiment Tracking | MLflow |
| Data Versioning | DVC |
| Node-based Workflow | ComfyUI |
| REST API | FastAPI |

---

## 🏗️ Architecture

\\\
┌──────────────────────────────────────────────────────────────┐
│                        CLIENT / USER                         │
│          (Swagger UI / curl / Frontend App)                  │
└─────────────────────────┬────────────────────────────────────┘
                          │  POST /api/v1/try-on
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Server (main.py)                   │
│  • Accepts person_image + garment_image (multipart upload)   │
│  • Saves images to ~/ComfyUI/input/                          │
│  • Loads & patches workflow_api.json                         │
│  • Dispatches job to ComfyUI REST API (:8188)                │
│  • Polls /history until generation completes                 │
│  • Returns generated PNG directly in response                │
└─────────────────────────┬────────────────────────────────────┘
                          │  HTTP POST /prompt
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                   ComfyUI Backend (:8188)                    │
│                                                              │
│  Node 1: LoadImage (person_image)                            │
│  Node 2: LoadImage (garment_image)                           │
│  Node 5: FashionClothMask  ◄──── Node 1                     │
│          (SCHP + DensePose body parsing)                     │
│  Node 3: CatVTONNode  ◄──── Node 1 + Node 2 + Node 5        │
│          (UNet2D inpainting diffusion, 40 steps, cfg=2.5)    │
│  Node 4: SaveImage  ◄──── Node 3                            │
│          (saves to ~/ComfyUI/output/)                        │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              ZenML Orchestrated Pipeline (pipeline.py)       │
│  @pipeline: virtual_tryon_pipeline                           │
│       └── @step: virtual_tryon_step                          │
│               • Sets up MLflow run                           │
│               • Loads & dispatches workflow_api.json          │
│               • Logs params, latency & artifacts to MLflow   │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              MLflow Tracking Server (:5001)                  │
│  • SQLite backend: mlflow.db                                 │
│  • Experiments: virtual-tryon-production / CatVTON_Baseline  │
│  • Tracks: params, latency, success, output artifacts        │
└──────────────────────────────────────────────────────────────┘
\\\

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Core AI Model** | CatVTON | Concatenation-based virtual try-on via Stable Diffusion inpainting |
| **Diffusion Framework** | Hugging Face Diffusers | UNet, VAE, DDIM scheduler |
| **Body Parsing** | SCHP + DensePose | Automatic cloth mask generation |
| **Node Workflow** | ComfyUI | Visual node graph for inference pipeline |
| **Pipeline Orchestration** | ZenML | Step tracking, artifact lineage, stack management |
| **Experiment Tracking** | MLflow | Params, metrics, artifact logging |
| **Data Versioning** | DVC | Dataset versioning (tracked: data/) |
| **REST API** | FastAPI + Uvicorn | Image upload endpoint, Swagger UI |
| **Deep Learning** | PyTorch + xFormers | GPU inference, memory-efficient attention |
| **Compute** | CUDA 12.1 | GPU acceleration |

---

## 📁 Repository Structure

\\\
try_on/
│
├── pipeline.py              # ZenML @pipeline + @step definition (production entrypoint)
├── main.py                  # FastAPI server with /api/v1/try-on endpoint
├── workflow_api.json        # ComfyUI API workflow blueprint (5-node graph)
├── requirements.txt         # Python dependencies (CUDA 12.1)
│
├── src/
│   └── models/
│       ├── CatVTON/         # Full CatVTON model source
│       │   ├── model/
│       │   │   ├── pipeline.py       # CatVTONPipeline class
│       │   │   ├── attn_processor.py # SkipAttnProcessor (cross-attn bypass)
│       │   │   ├── cloth_masker.py   # AutoMasker (SCHP + DensePose)
│       │   │   ├── SCHP/             # Self-Correction Human Parsing model
│       │   │   └── DensePose/        # Body part dense mapping
│       │   ├── inference.py          # Batch inference (VITON-HD / DressCode)
│       │   ├── app.py                # Gradio demo app
│       │   └── utils.py              # DREAM latent diffusion helpers
│       │
│       ├── run_baseline.py    # Raw CatVTON inference benchmark (no MLflow)
│       ├── run_reproducible.py # Deterministic run (seed=42, no TF32)
│       └── run_mlflow.py      # MLflow-tracked baseline run
│
├── data/
│   └── benchmark/           # DVC-tracked benchmark images
│       ├── person/
│       └── garment/
│
├── data.dvc                 # DVC pointer for data/ directory
├── configs/                 # Configuration files
├── pipelines/               # Additional ZenML pipeline definitions
├── manifests/               # Deployment manifests
├── frontend/                # Frontend app assets
├── inputs/                  # Runtime input staging area
├── outputs/                 # Generated result storage
├── artifacts/               # ZenML / MLflow artifact store
├── mlartifacts/             # MLflow artifact root
├── mlflow.db                # MLflow SQLite tracking DB (production)
├── mlruns.db                # MLflow SQLite tracking DB (baseline runs)
└── .zen/                    # ZenML project config (stack + project IDs)
\\\

---

## 🧠 Core Model — CatVTON

**CatVTON** (*Concatenation-based Virtual Try-On*) reformulates virtual try-on as an **image inpainting problem**.

### How It Works

1. **Input**: Person image (768×1024) + Garment reference image (768×1024) + Binary mask of the clothing region
2. **Masking**: Auto-generated by the \AutoMasker\ using:
   - **SCHP** (Self-Correction Human Parsing) — semantic body part segmentation
   - **DensePose** — dense 3D body surface mapping
3. **Diffusion Backbone**: Fine-tuned \UNet2DConditionModel\ based on \stable-diffusion-inpainting\
4. **Key Innovation**: Concatenates garment image latents directly as visual conditioning via a custom \SkipAttnProcessor\ that bypasses cross-attention (no text prompts needed)
5. **Attention Checkpoint**: \zhengchong/CatVTON\ — \mix-48k-1024\ variant
6. **Output**: Inpainted image with the garment realistically transferred onto the person

### Model Parameters

| Parameter | Value |
|---|---|
| Base checkpoint | \
unwayml/stable-diffusion-inpainting\ |
| Attention checkpoint | \zhengchong/CatVTON\ (mix-48k-1024) |
| VAE | \stabilityai/sd-vae-ft-mse\ |
| Inference steps | 40 (DDIM) |
| Guidance scale | 2.5 |
| Resolution | 768 × 1024 |
| Precision | \float16\ (production) / \p16\ (ComfyUI) |

---

## 🔗 ComfyUI Workflow

The \workflow_api.json\ defines the inference graph:

\\\
Node 1 (LoadImage: person)  →  Node 5 (FashionClothMask)
                                        │
Node 2 (LoadImage: garment) →  Node 3 (CatVTONNode) ←──────┘
                                        │
                               Node 4 (SaveImage)
\\\

- \FashionClothMask\ supports granular category targeting (shirt, top, sweater, pants, dress, etc.)
- \mask_grow=25\ expands mask boundary for cleaner inpainting seams
- \CatVTONNode\: seed=0, steps=40, cfg=2.5, fp16, attn_ckpt=mix

---

## 📊 MLOps Layers

### ZenML Pipeline

\pipeline.py\ defines two ZenML constructs:

- **\@step\ — \irtual_tryon_step\**: Atomic unit with artifact tracking, parameter capture, and caching support
- **\@pipeline\ — \irtual_tryon_pipeline\**: DAG connecting steps, with \enable_cache=False\ for fresh inference per run

**Stack ID**: \52f573c3-f954-4f1b-b19a-6064a42c5b50\

### MLflow Experiment Tracking

| Experiment | Script | Logged Items |
|---|---|---|
| \irtual-tryon-production\ | \pipeline.py\ | model_architecture, person_image, garment_image, inference_latency_seconds, pipeline_success, output artifact |
| \CatVTON_Baseline\ | \
un_mlflow.py\ | seed, inference_steps, guidance_scale, model, generated image artifact |

Launch the MLflow UI:
\\\ash
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001
\\\

### DVC Data Versioning

\\\yaml
# data.dvc
outs:
- md5: e92734da664ac4fa75af2c03758f4bc2.dir
  size: 223694
  nfiles: 2
  path: data
\\\

Git history:
- \e25b73d\ — Complete CatVTON pipeline with ZenML and MLflow integration
- \79c979\ — Initialize DVC and track raw dataset v1

---

## 🌐 API — FastAPI Server

**Swagger UI**: \http://127.0.0.1:8000/docs\

### \POST /api/v1/try-on\

| Field | Type | Description |
|---|---|---|
| \person_image\ | File | Photo of the person (JPG/PNG) |
| \garment_image\ | File | Photo of the garment (JPG/PNG) |

**Response**: \image/png\ — the generated try-on result

**Internal Flow**:
1. Saves uploaded files to \~/ComfyUI/input/\
2. Loads \workflow_api.json\ and patches \LoadImage\ nodes
3. POSTs to \ComfyUI /prompt\ API
4. Polls \/history/{prompt_id}\ until complete
5. Fetches image bytes via \/view\ API and returns them directly

---

## ⚙️ Setup & Installation

### Prerequisites

| Requirement | Version |
|---|---|
| OS | Ubuntu (WSL2 supported) |
| Python | 3.10+ |
| CUDA | 12.1 |
| GPU VRAM | 8 GB+ (16 GB recommended) |
| ComfyUI | Running on port 8188 |

### Steps

\\\ash
# 1. Clone
git clone <your-repo-url> ~/try_on && cd ~/try_on

# 2. Virtual environment
python -m venv venv && source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. ZenML setup
pip install zenml && zenml init

# 5. Pull DVC data
dvc pull

# 6. Place benchmark images
# data/benchmark/person/person_1.jpg
# data/benchmark/garment/garment_1.jpg
\\\

---

## 🚀 Running the Project

### Option A — FastAPI Production Server

\\\ash
# Terminal 1: ComfyUI
cd ~/ComfyUI && python main.py

# Terminal 2: MLflow tracking
mlflow server --backend-store-uri sqlite:///mlflow.db \
              --default-artifact-root ./mlartifacts --port 5001

# Terminal 3: FastAPI
cd ~/try_on && source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
\\\

Open \http://localhost:8000/docs\ and use Swagger UI.

### Option B — ZenML Orchestrated Pipeline

\\\ash
python pipeline.py
\\\

### Option C — Standalone Baseline Runs

\\\ash
python src/models/run_baseline.py          # Raw inference
python src/models/run_reproducible.py      # Deterministic (seed=42)
python src/models/run_mlflow.py            # MLflow-tracked
\\\

---

## 🔑 Key Design Decisions

| Decision | Rationale |
|---|---|
| ComfyUI as inference backend | Battle-tested GPU server with job queue; avoids GPU memory management in FastAPI |
| ZenML for orchestration | Future-proofs migration to cloud orchestrators (Kubeflow, Vertex AI) with zero code changes |
| Synthetic mask in baseline scripts | Eliminates Detectron2 complexity for reproducibility; real masking runs inside ComfyUI |
| MLflow with SQLite backend | Zero-infrastructure tracking for single-machine; swappable for PostgreSQL + S3 |
| DVC for data | Keeps binary assets out of git with versioned, reproducible snapshots |
| \float16\ precision | Best stability/speed trade-off on Ampere GPUs; avoids fp16 NaN issues in inpainting |
| \enable_cache=False\ | Inference is non-deterministic per run; caching would return stale results |

---

## 🗺️ Roadmap & Next Steps

- [ ] **Evaluation module** — SSIM, FID, LPIPS metrics via \src/evaluation/\
- [ ] **Frontend UI** — React or Gradio web interface in \rontend/\
- [ ] **Batch inference** — VITON-HD / DressCode dataset loaders from \inference.py\
- [ ] **Cloud deployment** — Docker + Kubernetes manifests in \manifests/\
- [ ] **Automated masking** — Replace synthetic rectangle mask with full SCHP + DensePose AutoMasker in baselines
- [ ] **Model registry** — Register production model versions in MLflow Model Registry
- [ ] **CI/CD pipeline** — GitHub Actions for lint, test, and docker build
- [ ] **Multi-garment support** — Lower body, dresses, and accessories in workflow

---

## 📄 License

The CatVTON model weights and code are subject to the [CatVTON license](src/models/CatVTON/LICENSE). This project wrapper is MIT licensed.

---

## 🙏 Acknowledgements

- [CatVTON](https://github.com/Zheng-Chong/CatVTON) — Zhengchong et al. for the core try-on model
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) — for the modular inference backend
- [ZenML](https://zenml.io) — for the MLOps orchestration framework
- [MLflow](https://mlflow.org) — for experiment tracking


---

## 👗 Interactive 2D Virtual Try-On Studio (Nutz Try On)

A high-performance, interactive **2D Image-Based Virtual Fitting Studio** powered by CatVTON diffusion inpainting and SegFormer human parsing:

* **URL**: [http://localhost:8000/studio](http://localhost:8000/studio)
* **Features**:
  * **2D Virtual Fitting Stage**: Side-by-side input stage with animated transfer guides.
  * **Interactive Before / After Comparison Slider**: Smooth draggable split view comparing the original photo against the AI try-on result.
  * **Dual & HD Result Views**: Easily toggle between Comparison Slider, Side-by-Side Dual View, and High-Resolution Result views.
  * **Sample Wardrobe & Custom Uploads**: Test curated garments (Oxford Shirt, Denim Jacket, Crewneck Tee, Tailored Blazer) or drag & drop custom photos.
  * **Inference Speed Controls**: Tune step counts (Fast 20 steps, Balanced 25 steps, High-Q 35 steps).
  * **Session History**: Track, inspect, and download generated outfits throughout your session.

---

## 💼 Commercial Product Architecture (Nutz Try On Enterprise v2.0)

Nutz Try On provides a turnkey 2D virtual try-on commercial engine with both a **B2B Embeddable E-Commerce Widget** and a **High-Performance API Gateway**:

### 1. Embeddable Merchant Widget (Shopify / WooCommerce)
Merchants embed virtual try-on on any product page with a single script tag:
```html
<link rel="stylesheet" href="http://localhost:8000/studio/widget.css">
<script src="http://localhost:8000/studio/widget.js"></script>

<!-- Add this button to any product page -->
<button class="nutz-tryon-btn" 
        data-nutz-tryon
        data-garment-url="https://store.com/products/shirt.jpg" 
        data-garment-name="Sage Oxford Shirt">
    ✨ Try On Live
</button>
```

* **Live Demo Storefront**: [http://localhost:8000/demo](http://localhost:8000/demo) (Simulates a luxury fashion brand with embedded try-on)
* **2D Fitting Studio**: [http://localhost:8000/studio](http://localhost:8000/studio)

### 2. Commercial API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | `GET` | Health check & ComfyUI GPU backend connectivity |
| `/api/v1/analytics` | `GET` | Real-time usage metrics, success rate, and average latency |
| `/api/v1/classify-garment` | `POST` | Auto-detects `upper_body`, `lower_body`, or `full_body` mask flags |
| `/api/v1/try-on` | `POST` | Synchronous high-definition try-on with automated category masking |