import json

with open('/mnt/c/Users/lenovo/.gemini/antigravity/brain/e3520d9c-dced-4b88-8ad1-6250428a996d/.system_generated/logs/transcript_full.jsonl') as f:
    for line_idx, line in enumerate(f):
        if line_idx == 1277:
            data = json.loads(line)
            tool_calls = data.get('tool_calls', [])
            for tc in tool_calls:
                args = tc.get('args', {})
                if 'Path' in args and 'App.tsx' in args['Path']:
                    content = args.get('Content', '')
                    print("Found App.tsx content! Length:", len(content))
                    with open('/home/lenovo/try_on/scripts/restored_App.tsx', 'w') as out:
                        out.write(content)
                    print("Written to scripts/restored_App.tsx")
