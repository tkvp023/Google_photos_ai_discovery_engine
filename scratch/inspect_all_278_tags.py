import sqlite3
import json

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

c.execute("""
    SELECT fpt.id, fpt.failure_type, fpt.sub_category, fpt.memory_cue_type, 
           fpt.confidence, d.source, fpt.evidence_quote, d.doc_id
    FROM failure_point_tags fpt
    JOIN documents d ON fpt.doc_id = d.doc_id
    ORDER BY fpt.failure_type, fpt.sub_category, fpt.confidence DESC
""")
rows = c.fetchall()
print(f"Total failure_point_tags: {len(rows)}")

# Group quotes by sub_category
by_sub = {}
by_cue = {}
for r in rows:
    sub = r[2]
    cue = r[3]
    by_sub.setdefault(sub, []).append(r)
    by_cue.setdefault(cue, []).append(r)

print("\nSubcategories and quote counts:")
for s, qlist in sorted(by_sub.items()):
    print(f"  {s}: {len(qlist)} quotes")

print("\nMemory cues and quote counts:")
for m, qlist in sorted(by_cue.items()):
    print(f"  {m}: {len(qlist)} quotes")
