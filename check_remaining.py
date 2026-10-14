import os

# Check for any remaining Viki/Viki references
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith(('.py', '.md', '.toml', '.txt', '.pyi', '.rs', '.ts', '.tsx', '.html', '.css', '.json', '.yml', '.yaml', '.sh', '.ps1')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()
            except:
                continue
            
            if 'viki' in content.lower() or ' viki ' in content.lower():
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'viki' in line.lower() or ' viki ' in line.lower():
                        # Skip if it's a variable name like 'viki_count'
                        if 'viki' in line.lower().split() or 'viki' in line.lower():
                            print(f'Found in: {os.path.join(root, f)}')
                            print('  Line {}: {}'.format(i+1, line.strip()[:120].encode('ascii', 'replace').decode()))
                        break