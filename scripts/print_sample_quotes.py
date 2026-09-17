import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import json
from pathlib import Path

for qid in range(1, 11):
    path = Path(f"dashboard/public/data/q{qid}.json")
    if not path.exists():
        continue
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    print(f"=== Q{qid}: {d.get('question_short')} ({d.get('total_relevant_docs')} docs) ===")
    for q in d.get("key_quotes", [])[:2]:
        text = q.get("text") or q.get("content", "")
        src = q.get("source", "")
        author = q.get("author", "user")
        print(f"  • [{src}] \"{text[:160]}...\"")
    print()
