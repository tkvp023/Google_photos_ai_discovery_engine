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

data_dir = Path("dashboard/public/data")

print("=" * 80)
print("📊 GOOGLE PHOTOS AI DISCOVERY QUESTIONS — EMPIRICAL DATA AUDIT")
print("=" * 80)

for qid in range(1, 11):
    q_file = data_dir / f"q{qid}.json"
    if not q_file.exists():
        print(f"❌ Q{qid}: File not found!")
        continue

    with open(q_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    q_text = data.get("question_text")
    q_short = data.get("question_short")
    total_docs = data.get("total_relevant_docs", 0)
    avg_conf = data.get("avg_confidence", 0)
    breakdown = data.get("breakdown", [])
    quotes = data.get("key_quotes", [])

    print(f"\n[Q{qid}] {q_short.upper()}: \"{q_text}\"")
    print(f"   ├─ Relevant Documents: {total_docs:,} docs (Avg Confidence: {avg_conf:.1%})")
    
    # Top tags
    top_tags_str = ", ".join([f"{item.get('tag')} ({item.get('count')})" for item in breakdown[:3]]) if breakdown else "None"
    print(f"   ├─ Top Friction Drivers: {top_tags_str}")
    
    # Sample Quote
    if quotes:
        sample_q = quotes[0]
        quote_text = sample_q.get("quote") or sample_q.get("content", "")
        author = sample_q.get("author", "anonymous")
        src = sample_q.get("source", "user")
        print(f"   └─ Key Verbatim Evidence: \"{quote_text[:120]}...\" — [{src}]")
    else:
        print(f"   └─ Key Verbatim Evidence: (None)")

print("\n" + "=" * 80)
