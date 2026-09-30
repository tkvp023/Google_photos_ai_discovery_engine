import os
import re
import json

ROOT = os.path.abspath(".")
EXCLUDE_DIRS = {'.git', 'node_modules', '.next', '__pycache__', 'scratch'}

patterns = [
    r'(\b\d+(\.\d+)?%\b)',
    r'(\b(expression|interpretation|evaluation|recovery)\b)',
    r'(\b(vague_memory_cue|literal_keyword_match|query_formulation_gap|forced_scroll|zero_recall|scrolling_friction)\b)',
    r'(\b(953|628|867|609|134|779|671|251|1616|1,616)\b)',
    r'(\b(59\.0|58\.9|38\.9|38\.8|53\.7|37\.7|48\.2|41\.5|26\.6|18\.3|6\.8|50\.6)\b)'
]

combined_re = re.compile('|'.join(patterns), re.IGNORECASE)

results = []

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
    for fname in filenames:
        if fname.endswith(('.py', '.json', '.md', '.ts', '.tsx', '.txt', '.yaml', '.yml')):
            fpath = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(fpath, ROOT)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_no, line in enumerate(f, start=1):
                        if combined_re.search(line):
                            results.append({
                                'file': rel_path,
                                'line': line_no,
                                'text': line.strip()
                            })
            except Exception as e:
                pass

print(f"Total matching lines found: {len(results)}")

# Let's filter to lines mentioning failure stages or categories specifically
failure_keywords = ['expression', 'interpretation', 'evaluation', 'recovery',
                    'vague memory', 'literal keyword', 'formulation gap',
                    'forced scroll', 'zero recall', 'scrolling friction',
                    'search misunderstanding', "can't find", "can't spot", "no help",
                    '48.2%', '41.5%', '59.0%', '58.9%', '38.9%', '38.8%', '53.7%', '37.7%']

targeted = []
for r in results:
    lower = r['text'].lower()
    if any(k in lower for k in failure_keywords):
        targeted.append(r)

print(f"Targeted failure-category lines: {len(targeted)}")

with open('scratch/targeted_inventory.json', 'w', encoding='utf-8') as f:
    json.dump(targeted, f, indent=2)

# Print a breakdown by file
file_counts = {}
for r in targeted:
    file_counts[r['file']] = file_counts.get(r['file'], 0) + 1

print("\nFiles containing failure category numbers/references:")
for f, cnt in sorted(file_counts.items(), key=lambda x: -x[1]):
    print(f"  {f}: {cnt} lines")
