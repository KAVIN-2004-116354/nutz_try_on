import os
import sys
import argparse
from pathlib import Path
from PIL import Image
import gradio as gr

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.inference.engine import CatVTONLoRAEngine
from src.inference.comfy_client import is_comfyui_alive, run_comfyui_tryon, prepare_rgb

# Singleton inference engines
engine_cache = {}

def get_engine(domain: str) -> CatVTONLoRAEngine:
    clean_domain = "indian_ethnic" if domain == "indian_ethnic" else "western"
    if clean_domain not in engine_cache:
        engine_cache[clean_domain] = CatVTONLoRAEngine(domain=clean_domain)
    return engine_cache[clean_domain]

# Verified high-quality sample paths
PERSON_MODI = str(PROJECT_ROOT / "frontend/assets/sample_person_modi.png")
PERSON_FEMALE = str(PROJECT_ROOT / "frontend/assets/sample_person_female.jpg")
PERSON_STUDIO = str(PROJECT_ROOT / "frontend/assets/sample_person_1.jpg")

GARMENT_DENIM = str(PROJECT_ROOT / "frontend/assets/sample_denim_jacket.jpg")
GARMENT_ANARKALI = str(PROJECT_ROOT / "frontend/assets/sample_anarkali_dress.jpg")
GARMENT_EMERALD = str(PROJECT_ROOT / "frontend/assets/sample_emerald_shirt.jpg")
GARMENT_BLAZER = str(PROJECT_ROOT / "frontend/assets/sample_navy_blazer.jpg")
GARMENT_TEE = str(PROJECT_ROOT / "frontend/assets/sample_black_tshirt.jpg")

def run_tryon(person_img, garment_img, domain, seed):
    if person_img is None:
        raise gr.Error("Please provide a Person / Model image.")
    if garment_img is None:
        raise gr.Error("Please provide a Garment reference image.")
        
    person_img = prepare_rgb(person_img)
    garment_img = prepare_rgb(garment_img)

    # Check if ComfyUI is live
    if is_comfyui_alive():
        try:
            cloth_type = "upper" if domain == "western" else "overall"
            comfy_res = run_comfyui_tryon(
                person_img=person_img,
                garment_img=garment_img,
                cloth_type=cloth_type,
                seed=int(seed),
                steps=25,
                cfg=2.5
            )
            telemetry_markdown = f"""
### ⚡ ComfyUI CatVTON Diffusion Telemetry
| Metric | Value |
| :--- | :--- |
| **Backend** | `ComfyUI CatVTON Diffusion (127.0.0.1:8188)` |
| **Workflow** | `DensePose + SCHP AutoMasker + SD1.5 Inpainting` |
| **Mask Type** | `{cloth_type.upper()} (Anatomical AutoMask, No Rectangles)` |
| **Inference Latency** | `⚡ {round(comfy_res['inference_time_ms'] / 1000, 2)} s` |
| **Precision** | `torch.bfloat16 (Zero OOM)` |
| **Status** | `✅ Completed 25 Diffusion Inpainting Steps` |
"""
            mask_out = comfy_res.get("mask_image", comfy_res["tryon_image"])
            return comfy_res["tryon_image"], mask_out, telemetry_markdown
        except Exception as e:
            print(f"[Gradio Notice] ComfyUI error, falling back to GPU engine: {e}")

    engine = get_engine(domain)
    res = engine.infer(
        person_image=person_img,
        garment_image=garment_img,
        domain=domain,
        seed=int(seed)
    )
    
    ckpt_name = os.path.basename(res["lora_checkpoint_used"])
    telemetry_markdown = f"""
### ⚡ GPU & LoRA Telemetry (Fallback Engine)
| Metric | Value |
| :--- | :--- |
| **Active Domain** | `{res['domain'].upper()}` |
| **LoRA Checkpoint** | `{ckpt_name}` |
| **LoRA Adapter Layers** | `{res['num_lora_tensors']} Attention Projections (Rank-16)` |
| **Inference Latency** | `⚡ {res['inference_time_ms']} ms` |
| **Peak GPU VRAM** | `💾 {res['peak_vram_mb']} MB / 8,192 MB (RTX 5050)` |
| **Precision** | `torch.bfloat16 (Zero OOM)` |
| **MediaPipe Pose** | `{'✅ Detected (Anatomical Anchor)' if res['mediapipe_detected'] else '⚠️ Fallback Studio Mask'}` |
| **MLflow Experiment** | `nutz_try_on_lora` |
"""
    return res["tryon_image"], res["masked_preview"], telemetry_markdown

def set_sample(p_path, g_path, dom):
    p_img = Image.open(p_path) if os.path.exists(p_path) else None
    g_img = Image.open(g_path) if os.path.exists(g_path) else None
    return p_img, g_img, dom

def build_app():
    with gr.Blocks(title="Nutz Virtual Try-On Studio 2.0") as demo:
        gr.Markdown(
            """
            # 👗 Nutz Virtual Fitting Studio 2.0
            ### Photorealistic 2D Diffusion Try-On with ComfyUI CatVTON & Anatomical DensePose/SCHP Masking
            **Hardware Engine**: NVIDIA GeForce RTX 5050 Laptop GPU (8GB VRAM) • Mixed Precision: `bfloat16` • Backend: `ComfyUI CatVTON`
            """
        )
        
        with gr.Row():
            # LEFT COLUMN: Fitting Room Inputs
            with gr.Column(scale=5):
                gr.Markdown("## 👤 1. Model & Garment Selection")
                
                with gr.Row():
                    person_input = gr.Image(
                        value=PERSON_MODI if os.path.exists(PERSON_MODI) else None,
                        type="pil",
                        label="Target Model / Person (Standing Pose)",
                        height=380
                    )
                    garment_input = gr.Image(
                        value=GARMENT_DENIM if os.path.exists(GARMENT_DENIM) else None,
                        type="pil",
                        label="Garment Reference (Flat-lay or Product)",
                        height=380
                    )
                
                gr.Markdown("#### ⚡ Quick Presets")
                with gr.Row():
                    btn_preset_modi = gr.Button("🇮🇳 Modi + Denim Jacket", size="sm")
                    btn_preset_female_dress = gr.Button("🥻 Model + Green Anarkali", size="sm")
                    btn_preset_blazer = gr.Button("👔 Studio + Navy Blazer", size="sm")
                    btn_preset_emerald = gr.Button("👕 Modi + Oxford Shirt", size="sm")

                gr.Markdown("## 🎛️ 2. Domain & Try-On Configuration")
                domain_choice = gr.Radio(
                    choices=[
                        ("👔 Western (Upper-body / Waist-bounded / Pants Protected)", "western"),
                        ("🇮🇳 Indian Ethnic (Full-body Kurtas, Sarees & Anarkalis)", "indian_ethnic")
                    ],
                    value="western",
                    label="Garment Category / Coverage",
                    info="Western: waist-bounded mask protecting legs | Indian Ethnic: full drape"
                )
                
                with gr.Row():
                    seed_input = gr.Slider(minimum=1, maximum=9999, value=42, step=1, label="Random Seed")
                
                generate_btn = gr.Button("✨ Generate Virtual Try-On", variant="primary", size="lg")

            # RIGHT COLUMN: Mirror & Telemetry
            with gr.Column(scale=6):
                gr.Markdown("## 🪞 3. Virtual Fitting Mirror")
                
                with gr.Tabs():
                    with gr.TabItem("✨ Try-On Result"):
                        tryon_output = gr.Image(
                            type="pil",
                            label="Virtual Try-On Photorealistic Render (ComfyUI CatVTON)",
                            height=520,
                            interactive=False
                        )
                    with gr.TabItem("🎯 DensePose / SCHP Anatomical Mask"):
                        mask_output = gr.Image(
                            type="pil",
                            label="Anatomical Agnostic Mask (Protects Head, Hands & Lower Body)",
                            height=520,
                            interactive=False
                        )
                    with gr.TabItem("📊 GPU Telemetry & MLOps"):
                        telemetry_output = gr.Markdown("Click **Generate Virtual Try-On** to view live GPU telemetry.")

        # Preset Button Click Handlers
        btn_preset_modi.click(
            fn=lambda: set_sample(PERSON_MODI, GARMENT_DENIM, "western"),
            outputs=[person_input, garment_input, domain_choice]
        )
        btn_preset_female_dress.click(
            fn=lambda: set_sample(PERSON_FEMALE, GARMENT_ANARKALI, "indian_ethnic"),
            outputs=[person_input, garment_input, domain_choice]
        )
        btn_preset_blazer.click(
            fn=lambda: set_sample(PERSON_STUDIO, GARMENT_BLAZER, "western"),
            outputs=[person_input, garment_input, domain_choice]
        )
        btn_preset_emerald.click(
            fn=lambda: set_sample(PERSON_MODI, GARMENT_EMERALD, "western"),
            outputs=[person_input, garment_input, domain_choice]
        )

        # Generate Action
        generate_btn.click(
            fn=run_tryon,
            inputs=[person_input, garment_input, domain_choice, seed_input],
            outputs=[tryon_output, mask_output, telemetry_output]
        )
        
    return demo

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-port", type=int, default=7860, help="Server port (default: 7860)")
    parser.add_argument("--server-name", type=str, default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    args = parser.parse_args()
    
    app = build_app()
    print(f"Launching Nutz Try-On Fitting Studio at http://{args.server_name}:{args.server_port} ...", flush=True)
    app.launch(server_name=args.server_name, server_port=args.server_port, share=False)
