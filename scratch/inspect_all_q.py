import json
from pathlib import Path

for i in range(1, 11):
    p = Path(f"dashboard/public/data/q{i}.json")
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    print(f"Q{i}: {d['question_short']} | Total: {d['total_relevant_docs']} | Conf: {d['avg_confidence']}")
    for b in d.get("breakdown", []):
        print(f"   {b['tag']}: {b['label']} -> {b['count']} ({b['pct']}%) [conf: {b.get('avg_confidence')}]")
