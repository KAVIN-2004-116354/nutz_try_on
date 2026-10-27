from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
import urllib.request
import urllib.parse
import json
import time
import os

app = FastAPI(title="Virtual Try-On API", version="1.2")
COMFYUI_URL = "http://127.0.0.1:8188"

def queue_prompt(prompt):
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
    response = urllib.request.urlopen(req)
    return json.loads(response.read())

def get_history(prompt_id):
    req = urllib.request.Request(f"{COMFYUI_URL}/history/{prompt_id}")
    response = urllib.request.urlopen(req)
    return json.loads(response.read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    req = urllib.request.Request(f"{COMFYUI_URL}/view?{url_values}")
    response = urllib.request.urlopen(req)
    return response.read()

@app.post("/api/v1/try-on")
async def generate_try_on(
    person_image: UploadFile = File(...),
    garment_image: UploadFile = File(...)
):
    # 1. Save uploaded images to ComfyUI input folder
    input_dir = os.path.expanduser("~/ComfyUI/input")
    os.makedirs(input_dir, exist_ok=True)
    
    person_path = os.path.join(input_dir, person_image.filename)
    garment_path = os.path.join(input_dir, garment_image.filename)
    
    with open(person_path, "wb") as f:
        f.write(await person_image.read())
    with open(garment_path, "wb") as f:
        f.write(await garment_image.read())

    # 2. Load and update the blueprint
    with open("workflow_api.json", "r") as f:
        prompt = json.load(f)

    # Note: Node IDs (like "1" and "2") might vary based on your specific JSON. 
    # Check your workflow_api.json if this throws a KeyError!
    for node_id, node in prompt.items():
        if node["class_type"] == "LoadImage":
            if "person" in node["inputs"]["image"].lower() or node_id == "1":
                node["inputs"]["image"] = person_image.filename
            elif "garment" in node["inputs"]["image"].lower() or node_id == "2":
                node["inputs"]["image"] = garment_image.filename

    # 3. Fire the request to ComfyUI
    prompt_response = queue_prompt(prompt)
    prompt_id = prompt_response["prompt_id"]

    # 4. Wait for the GPU to finish (Polling)
    while True:
        history = get_history(prompt_id)
        if prompt_id in history:
            break
        time.sleep(1) # Check every 1 second

    # 5. Extract and return the final image
    history_data = history[prompt_id]
    for node_id in history_data['outputs']:
        node_output = history_data['outputs'][node_id]
        if 'images' in node_output:
            image_info = node_output['images'][0]
            image_bytes = get_image(image_info['filename'], image_info['subfolder'], image_info['type'])
            
            # Return the actual image file to Swagger UI
            return Response(content=image_bytes, media_type="image/png")
            
    return {"error": "Image generation failed or output not found"}
