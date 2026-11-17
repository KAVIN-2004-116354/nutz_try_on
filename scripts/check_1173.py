import json

with open('/mnt/c/Users/lenovo/.gemini/antigravity/brain/e3520d9c-dced-4b88-8ad1-6250428a996d/.system_generated/logs/transcript_full.jsonl') as f:
    for line_idx, line in enumerate(f):
        if line_idx == 1173:
            data = json.loads(line)
            for tc in data.get('tool_calls', []):
                print("1173 Target:", tc.get('args', {}).get('Target'))
                print("1173 Replacement:", tc.get('args', {}).get('Replacement'))
