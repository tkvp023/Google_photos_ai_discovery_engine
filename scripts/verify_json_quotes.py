import json

for qid in range(1, 11):
    with open(f"dashboard/public/data/q{qid}.json", "r", encoding="utf-8") as f:
        d = json.load(f)
    print(f"\n=== Q{qid}: {d.get('question_short', '')} ({len(d['key_quotes'])} quotes) ===")
    for i, q in enumerate(d['key_quotes']):
        ends_dots = q['text'].endswith('...')
        print(f"  [{i+1}] {q['source']} | len={len(q['text'])} chars | ends_with_dots={ends_dots}")
        print(f"      Preview: \"{q['text'][:100]}...\"")
        print(f"      Ending: \"...{q['text'][-60:]}\"")

with open("dashboard/public/data/systemic_gaps.json", "r", encoding="utf-8") as f:
    sg = json.load(f)
print(f"\n=== Systemic Gaps ({len(sg['key_quotes'])} quotes) ===")
for i, q in enumerate(sg['key_quotes']):
    print(f"  [{i+1}] {q.get('source')} | len={len(q['text'])} chars | Issue: {q.get('issue')}")
    print(f"      Preview: \"{q['text'][:90]}...\"")
