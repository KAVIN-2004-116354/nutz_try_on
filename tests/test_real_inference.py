import pytest
import urllib.request
import urllib.error
import json
import time
import os
from PIL import Image

COMFYUI_URL = "http://127.0.0.1:8188"
WORKFLOW_PATH = "/home/lenovo/try_on/workflow_api.json"
OUTPUT_DIR = os.path.expanduser("~/ComfyUI/output")

def test_comfyui_catvton_inference():
    # 1. Check ComfyUI server reachability
    try:
        with urllib.request.urlopen(f"{COMFYUI_URL}/system_stats", timeout=2) as resp:
            stats = json.loads(resp.read().decode("utf-8"))
            print("ComfyUI is online.")
            devices = stats.get("devices", [])
            if devices:
                dev = devices[0]
                print(f"Device: {dev.get('name')}")
                print(f"VRAM Free: {dev.get('vram_free', 0) / (1024**2):.1f} MB / {dev.get('vram_total', 0) / (1024**2):.1f} MB")
    except Exception as e:
        pytest.skip(f"ComfyUI is not reachable at {COMFYUI_URL}: {e}")

    print("\n--- [TEST] ComfyUI CatVTON Real Inference ---")

    # 2. Load workflow_api.json
    with open(WORKFLOW_PATH, "r") as f:
        wf = json.load(f)

    # Use 20 steps for fast and thorough validation
    wf["3"]["inputs"]["steps"] = 20
    wf["1"]["inputs"]["image"] = "person_1.jpg"
    wf["2"]["inputs"]["image"] = "garment_1.jpg"

    # 3. Submit workflow to ComfyUI
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=json.dumps({"prompt": wf}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    start_time = time.time()
    try:
        with urllib.request.urlopen(req) as resp:
            prompt_res = json.loads(resp.read().decode("utf-8"))
            prompt_id = prompt_res.get("prompt_id")
            print(f"Prompt successfully queued with ID: {prompt_id}")
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        raise RuntimeError(f"ComfyUI rejected prompt: {err_msg}")

    # 4. Poll for output
    timeout = 180
    result_filename = None
    print("Waiting for CatVTON diffusion execution...")
    
    while time.time() - start_time < timeout:
        time.sleep(2)
        try:
            with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}") as resp:
                history = json.loads(resp.read().decode("utf-8"))
                if prompt_id in history:
                    history_data = history[prompt_id]
                    # Check for execution errors
                    status = history_data.get("status", {})
                    if status.get("status_str") == "error":
                        raise RuntimeError(f"Execution error in ComfyUI: {status.get('messages')}")
                    
                    outputs = history_data.get("outputs", {})
                    for node_id, node_output in outputs.items():
                        if "images" in node_output and len(node_output["images"]) > 0:
                            result_filename = node_output["images"][0]["filename"]
                            break
                    if result_filename:
                        break
        except urllib.error.URLError:
            pass
        print(".", end="", flush=True)

    elapsed = time.time() - start_time
    print(f"\nInference completed in {elapsed:.2f} seconds.")

    assert result_filename is not None, f"Timed out waiting for inference result for prompt {prompt_id}"
    
    # 5. Validate the generated image
    result_path = os.path.join(OUTPUT_DIR, result_filename)
    print(f"Output image path: {result_path}")
    assert os.path.exists(result_path), f"Output file does not exist on disk: {result_path}"
    
    file_size = os.path.getsize(result_path)
    print(f"Output file size: {file_size} bytes")
    assert file_size > 10000, f"Output file is suspiciously small: {file_size} bytes"

    # Decode with PIL
    img = Image.open(result_path)
    print(f"Image format: {img.format}, size: {img.size}, mode: {img.mode}")
    assert img.size[0] > 0 and img.size[1] > 0, "Image has invalid dimensions"
    
    # Verify image is not solid black or white
    extrema = img.getextrema()
    print(f"Image channel extrema: {extrema}")
    for channel_min, channel_max in extrema:
        assert channel_max > channel_min, "Image has zero variance (blank image)"

    # Copy to outputs directory
    os.makedirs("/home/lenovo/try_on/outputs", exist_ok=True)
    local_copy = "/home/lenovo/try_on/outputs/test_catvton_result.png"
    import shutil
    shutil.copyfile(result_path, local_copy)
    print(f"Saved local test artifact to: {local_copy}")
    print("--- [PASS] ComfyUI CatVTON Real Inference Succeeded! ---")

if __name__ == "__main__":
    test_comfyui_catvton_inference()

