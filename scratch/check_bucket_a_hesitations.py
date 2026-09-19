import sqlite3

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

print("=== Hesitation tags filtered to Bucket A docs ===")
c.execute("""
    SELECT ht.reason, d.source, COUNT(*), AVG(ht.confidence)
    FROM hesitation_tags ht
    JOIN documents d ON ht.doc_id = d.doc_id
    JOIN triage_buckets tb ON d.doc_id = tb.doc_id AND tb.bucket = 'A'
    GROUP BY ht.reason, d.source
    ORDER BY ht.reason, COUNT(*) DESC
""")
rows = c.fetchall()
reasons = {}
for r in rows:
    reason = r[0]
    src = r[1]
    cnt = r[2]
    conf = r[3]
    reasons.setdefault(reason, {})[src] = (cnt, conf)

for r, pmap in sorted(reasons.items()):
    tot = sum(v[0] for v in pmap.values())
    print(f"Bucket A | {r}: total={tot} | {pmap}")
