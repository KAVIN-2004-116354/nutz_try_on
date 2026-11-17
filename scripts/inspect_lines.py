import json

with open('/mnt/c/Users/lenovo/.gemini/antigravity/brain/e3520d9c-dced-4b88-8ad1-6250428a996d/.system_generated/logs/transcript_full.jsonl') as f:
    for line_idx, line in enumerate(f):
        if line_idx in [831, 1020, 1277]:
            data = json.loads(line)
            tool_calls = data.get('tool_calls', [])
            print(f"Index {line_idx}: {len(tool_calls)} calls")
            for tc in tool_calls:
                name = tc.get('name')
                args = tc.get('args', {})
                path = args.get('Path', '')
                print(f"  {name} -> {path}")
