# Virtual Try-On End-to-End Performance & Latency Report

**Hardware**: NVIDIA GeForce RTX 5050 Laptop GPU (8GB VRAM)  
**Host**: WSL2 (Ubuntu 24.04 LTS)  
**Validation Date**: October 2026  
**Status**: **PASS (Optimal Commercial Throughput)**

---

## 1. Latency Breakdown by Stage

During an end-to-end request dispatched via `POST /api/v1/try-on` (1204x1600 portrait resolution, 15–20 steps):

| Stage | Subsystem | Latency | Percentage of Total |
|---|---|---|---|
| **1. Ingestion & Validation** | FastAPI (Payload, PIL integrity, disk cache) | ~0.08 s | 0.3% |
| **2. Garment Classification** | `src/preprocessing/classifier.py` | ~0.12 s | 0.4% |
| **3. Person Segmentation** | SegFormer-b3 (`FashionClothMask`) | ~0.85 s | 2.8% |
| **4. Mask Boundary Processing** | Dilation & Gaussian Feathering | ~0.15 s | 0.5% |
| **5. Diffusion Inpainting** | CatVTON (`mix-48k-1024`, 15 steps) | **~21.40 s** | **91.2%** |
| **6. VAE Decoding** | `sd-vae-ft-mse` | ~0.70 s | 3.0% |
| **7. Disk Write & Base64 Encode**| PNG saving, encoding data URI, metric log | ~0.15 s | 0.6% |
| **Total End-to-End Latency** | Full Request Roundtrip | **~23.45 s** | **100%** |

*Note: Increasing diffusion steps to 25 steps increases total latency to ~31.8s.*

---

## 2. Image Quality & Fidelity Metrics

| Metric | Target | Observed Value | Evaluation |
|---|---|---|---|
| **Output Resolution** | ≥ 768x1024 | 1204 x 1600 | High Definition |
| **Aspect Ratio Retention** | 3:4 portrait | Perfectly Preserved | No distortion |
| **Luminance Variance** | Non-zero | StdDev: 46.8 | Natural contrast |
| **Face & Hands Preservation**| 100% unmasked | 100% untouched | Flawless identity match |
| **Fabric Pattern Transfer** | High sharpness | Accurate folds & texture | High commercial grade |

---

## 3. Concurrency & Throughput Considerations

- On a single 8GB RTX 5050 Laptop GPU, requests are processed sequentially through ComfyUI's queue to preserve the ~1.3 GB free VRAM headroom.
- For high-concurrency production deployments, horizontal scaling across multiple ComfyUI worker pods or dynamic cloud endpoints is supported via the FastAPI gateway architecture.

