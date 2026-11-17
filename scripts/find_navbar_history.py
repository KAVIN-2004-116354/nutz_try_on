import json

with open('/mnt/c/Users/lenovo/.gemini/antigravity/brain/e3520d9c-dced-4b88-8ad1-6250428a996d/.system_generated/logs/transcript_full.jsonl') as f:
    for line_idx, line in enumerate(f):
        if 'navbar.tsx' in line.lower() or 'generationhistory.tsx' in line.lower():
            data = json.loads(line)
            for tc in data.get('tool_calls', []):
                p = tc.get('args', {}).get('Path', '')
                if 'navbar.tsx' in p.lower() or 'generationhistory.tsx' in p.lower():
                    print(f"Line {line_idx}: {tc.get('name')} -> {p}")
                    if tc.get('name') == 'write_file':
                        name = 'navbar' if 'navbar' in p.lower() else 'history'
                        with open(f'/home/lenovo/try_on/scripts/backup_{name}_{line_idx}.tsx', 'w') as out:
                            out.write(tc.get('args', {}).get('Content', ''))
