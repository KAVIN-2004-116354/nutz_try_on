# Current State Audit

**Date**: 2026-10-29  
**Repository Path**: `/home/lenovo/try_on`  
**Git Branch**: `master`  
**Git Head**: `e25b73d` (`feat: complete CatVTON pipeline with ZenML and MLflow integration`)  

---

## 1. Git Status & Uncommitted Changes

```
On branch master
Changes not staged for commit:
  modified:   main.py
  modified:   mlflow.db
  modified:   pipeline.py
  modified:   workflow_api.json

Untracked files:
  README.md
  analyze_modi.py
  build_studio.py
  debug_mask.py
  debug_mask2.py
  frontend/
  result.png
  src/preprocessing/
```

*Note*: No destructive operations (`git reset`, `git clean`) were performed. All existing user work, weights, and images are preserved.

---

## 2. Directory Structure & File Map

* `main.py`: FastAPI server handling `/api/v1/try-on`, `/api/v1/classify-garment`, `/health`, `/api/v1/analytics`, mounting `/studio` and `/outputs`.
* `workflow_api.json`: ComfyUI JSON API workflow definition referencing `LoadImage`, `FashionClothMask`, `CatVTONNode`, and `SaveImage`.
* `pipeline.py`: ZenML pipeline orchestrating virtual try-on with MLflow run tracking and image artifact logging.
* `mlflow.db`: SQLite database storing MLflow experiment runs for `virtual-tryon-production`.
* `data.dvc`, `.dvcignore`: DVC tracking files for dataset versioning.
* `src/`:
  * `src/models/CatVTON/`: Cloned repository of CatVTON implementation.
  * `src/preprocessing/classifier.py`: Rule-based garment category classifier.
  * `src/models/run_mlflow.py`, `run_baseline.py`, `run_reproducible.py`.
* `frontend/`:
  * `index.html`: Dedicated 2D AI Virtual Try-On Studio.
  * `app.js`: Interactive frontend logic (before/after comparison slider, image upload, REST API dispatch).
  * `style.css`: Luxury white/indigo theme styling.
  * `widget.js`, `widget.css`: Embeddable merchant widget SDK.
  * `demo_store.html`: Standalone e-commerce storefront demo.
  * `assets/`: Sample models (Modi, Studio Model) and sample garments (Oxford Shirt, Denim Jacket, Black Tee, Navy Blazer).
* `tests/`: Existing test directory (initially empty).
* `outputs/`: Local inference storage directory.

---

## 3. Runtime Environment Audit

* **OS**: Linux (WSL2 Ubuntu 24.04 on Windows 11 host)
* **Python**: 3.14.4
* **PyTorch**: 2.14.1+cu130
* **CUDA Device**: `cuda:0` - NVIDIA GeForce RTX 5050 Laptop GPU
* **Total VRAM**: 8151 MiB (~8.5 GB)
* **ComfyUI Version**: 0.42.0 (running on `http://127.0.0.1:8188`)
* **ComfyUI Packages**:
  * `comfy-aimdo`: 0.6.0 (installed and active)
  * `comfyui-frontend-package`: 1.57.1
  * `comfyui-workflow-templates`: 0.11.96
* **Custom Nodes**:
  * `/home/lenovo/ComfyUI/custom_nodes/comfyui-try-on` (exposes `CatVTONNode` and `FashionClothMask`)
  * `/home/lenovo/ComfyUI/custom_nodes/websocket_image_save.py`

---

## 4. Initial Test Status

* Prior to this audit, `pytest` was not installed in the virtual environment and `tests/` had no test files.
* Test dependencies (`pytest`, `httpx`) have been provisioned to enable automated regression testing.

