import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = "dashboard"
EXCLUDE = {'.next', 'node_modules', 'package-lock.json'}
patterns = [
    r'interpretation_failure',
    r'recovery_breakdown',
    r'#1 Blocker',
    r'#2 Blocker',
    r'59\.0%',
    r'38\.9%',
    r'53\.7%',
    r'37\.7%',
    r'48\.2%',
    r'41\.5%',
    r'36\.7%',
    r'\b593\b',
    r'\b628\b',
    r'\b953\b',
    r'\b867\b',
    r'\b609\b',
    r'\b107\b',
]

combined = re.compile('|'.join(patterns), re.IGNORECASE)

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in EXCLUDE]
    for f in filenames:
        if f in EXCLUDE:
            continue
        if f.endswith(('.ts', '.tsx', '.json', '.css', '.md')):
            path = os.path.join(dirpath, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                for idx, line in enumerate(fp, start=1):
                    if combined.search(line):
                        print(f"{path}:{idx}: {line.strip()[:140]}")
