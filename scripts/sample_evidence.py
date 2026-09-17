import sqlite3

conn = sqlite3.connect('data/db.sqlite')
c = conn.cursor()

sample_tags = c.execute("""
    SELECT h.reason, h.evidence_quote, d.content, d.source, d.source_id
    FROM hesitation_tags h
    JOIN documents d ON h.doc_id = d.doc_id
    WHERE h.evidence_quote IS NOT NULL AND LENGTH(h.evidence_quote) > 20
    LIMIT 10
""").fetchall()

for r in sample_tags:
    print(f"Reason: {r[0]}")
    print(f"Evidence quote: {r[1]}")
    print(f"Full doc content (len={len(r[2])}): {r[2][:150]}...")
    print(f"Source: {r[3]}, ID: {r[4]}")
    print("-" * 50)
