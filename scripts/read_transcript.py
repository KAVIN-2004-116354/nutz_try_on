import json

with open('/mnt/c/Users/lenovo/.gemini/antigravity/brain/e3520d9c-dced-4b88-8ad1-6250428a996d/.system_generated/logs/transcript.jsonl') as f:
    lines = f.readlines()

for line in lines[1285:1305]:
    data = json.loads(line)
    step = data.get('step_index')
    src = data.get('source')
    typ = data.get('type')
    content = str(data.get('content', ''))[:120].replace('\n', ' ')
    print(f"Step {step} | {src} | {typ} | {content}")
