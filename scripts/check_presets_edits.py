import json

with open('/mnt/c/Users/lenovo/.gemini/antigravity/brain/e3520d9c-dced-4b88-8ad1-6250428a996d/.system_generated/logs/transcript_full.jsonl') as f:
    for line_idx, line in enumerate(f):
        if line_idx in [262, 381]:
            data = json.loads(line)
            tool_calls = data.get('tool_calls', [])
            for tc in tool_calls:
                print(f"Line {line_idx} Target:", tc.get('args', {}).get('Target'))
                print(f"Line {line_idx} Replacement:", tc.get('args', {}).get('Replacement'))
