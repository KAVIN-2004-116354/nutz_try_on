import urllib.request
import json
import time
import subprocess

with open("/home/lenovo/try_on/workflow_api.json") as f:
    wf = json.load(f)

# Use 15 steps
wf["3"]["inputs"]["steps"] = 15
wf["1"]["inputs"]["image"] = "person_1.jpg"
wf["2"]["inputs"]["image"] = "garment_1.jpg"

req = urllib.request.Request(
    "http://127.0.0.1:8188/prompt",
    data=json.dumps({"prompt": wf}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        prompt_id = res["prompt_id"]
        print(f"Queued prompt: {prompt_id}")
except Exception as e:
    print(f"Failed to queue: {e}")
    exit(1)

for _ in range(30):
    time.sleep(1)
    with open("/home/lenovo/ComfyUI/comfyui.log") as lf:
        lines = lf.readlines()
        if lines:
            print("LOG TAIL:\n" + "".join(lines[-15:]))
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:8188/history/{prompt_id}") as hr:
            hist = json.loads(hr.read().decode("utf-8"))
            if prompt_id in hist:
                print("HISTORY RESULT:", hist[prompt_id])
                break
    except Exception as e:
        print(f"Error checking history: {e}")
        break

