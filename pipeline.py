import time
import os
import json
import urllib.request
import urllib.error
import shutil
import mlflow
from zenml import pipeline, step

COMFYUI_URL = "http://127.0.0.1:8188"

def queue_comfyui_prompt(prompt_workflow: dict):
    url = f"{COMFYUI_URL}/prompt"
    data = json.dumps({"prompt": prompt_workflow}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("prompt_id")
    except urllib.error.HTTPError as e:
        print(f"ComfyUI API rejected the request: {e}")
        try:
            print(f"Error Details: {e.read().decode('utf-8')}")
        except Exception:
            pass
        return None
    except Exception as e:
        print(f"Failed to connect to ComfyUI API: {e}")
        return None

def wait_for_comfyui_completion(prompt_id: str, timeout_seconds: int = 180):
    url = f"{COMFYUI_URL}/history/{prompt_id}"
    start_wait = time.time()
    print(f"Polling ComfyUI for prompt {prompt_id} completion...")
    
    while time.time() - start_wait < timeout_seconds:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                history = json.loads(response.read().decode("utf-8"))
                if prompt_id in history:
                    history_data = history[prompt_id]
                    outputs = history_data.get("outputs", {})
                    for node_id, node_output in outputs.items():
                        if "images" in node_output and len(node_output["images"]) > 0:
                            image_info = node_output["images"][0]
                            return image_info["filename"]
        except Exception:
            pass
        time.sleep(2)
        print(".", end="", flush=True)
    
    print(f"\nTimed out waiting for prompt {prompt_id}")
    return None

@step
def virtual_tryon_step(person_image_filename: str, garment_image_filename: str) -> str:
    start_time = time.time()
    
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not tracking_uri:
        try:
            urllib.request.urlopen("http://127.0.0.1:5001", timeout=1)
            tracking_uri = "http://127.0.0.1:5001"
        except Exception:
            db_file = os.path.abspath("mlflow.db")
            tracking_uri = f"sqlite:///{db_file}"
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("virtual-tryon-production")
    
    with mlflow.start_run(run_name="zenml_catvton_comfyapi"):
        mlflow.log_param("model_architecture", "CatUTON (ComfyUI API Backend)")
        mlflow.log_param("person_image", person_image_filename)
        mlflow.log_param("garment_image", garment_image_filename)
        
        workflow_path = "workflow_api.json"
        if not os.path.exists(workflow_path):
            raise FileNotFoundError(f"Missing {workflow_path} in ~/try_on directory!")
            
        with open(workflow_path, "r") as f:
            comfy_workflow = json.load(f)
        
        person_node_id = "1" 
        garment_node_id = "2"
        
        comfy_workflow[person_node_id]["inputs"]["image"] = person_image_filename
        comfy_workflow[garment_node_id]["inputs"]["image"] = garment_image_filename
        
        print("Dispatching workflow to ComfyUI API on port 8188...")
        prompt_id = queue_comfyui_prompt(comfy_workflow)
        output_filename = None
        output_path = None
        
        if prompt_id:
            print(f"Successfully queued ComfyUI prompt ID: {prompt_id}")
            output_filename = wait_for_comfyui_completion(prompt_id)
            if output_filename:
                output_path = os.path.join(os.path.expanduser("~/ComfyUI/output"), output_filename)
                print(f"\nGeneration complete! Output image: {output_path}")
                
                os.makedirs("outputs", exist_ok=True)
                local_output = os.path.join("outputs", f"tryon_{output_filename}")
                shutil.copyfile(output_path, local_output)
                
                if os.path.exists(output_path):
                    mlflow.log_artifact(output_path, artifact_path="outputs")
        else:
            print("API request failed.")
            
        latency = time.time() - start_time
        mlflow.log_metric("inference_latency_seconds", latency)
        mlflow.log_metric("pipeline_success", 1 if output_filename else 0)
            
        return output_path or ""

@pipeline
def virtual_tryon_pipeline(person_img: str, garment_img: str):
    virtual_tryon_step(person_image_filename=person_img, garment_image_filename=garment_img)

if __name__ == "__main__":
    virtual_tryon_pipeline.with_options(enable_cache=False)(
        person_img="person_1.jpg", 
        garment_img="garment_1.jpg"
    )
