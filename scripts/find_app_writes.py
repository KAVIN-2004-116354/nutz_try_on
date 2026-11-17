import json

with open('/mnt/c/Users/lenovo/.gemini/antigravity/brain/e3520d9c-dced-4b88-8ad1-6250428a996d/.system_generated/logs/transcript_full.jsonl') as f:
    for line_idx, line in enumerate(f):
        if 'app.tsx' in line.lower():
            data = json.loads(line)
            tool_calls = data.get('tool_calls', [])
            for tc in tool_calls:
                args = tc.get('args', {})
                p = args.get('Path', '')
                if 'app.tsx' in p.lower():
                    print(f"Line {line_idx}: {tc.get('name')} -> {p}")
                    if tc.get('name') == 'write_file':
                        print("  length:", len(args.get('Content', '')))
                        with open(f'/home/lenovo/try_on/scripts/app_backup_{line_idx}.tsx', 'w') as out:
                            out.write(args.get('Content', ''))
