import json

with open('/mnt/c/Users/lenovo/.gemini/antigravity/brain/e3520d9c-dced-4b88-8ad1-6250428a996d/.system_generated/logs/transcript_full.jsonl') as f:
    for line_idx, line in enumerate(f):
        if line_idx == 63:
            data = json.loads(line)
            content = data.get('content', '')
            print("Line 63 content length:", len(content))
            with open('/home/lenovo/try_on/scripts/presets_original.ts', 'w') as out:
                out.write(content)
            print("Saved presets_original.ts")
