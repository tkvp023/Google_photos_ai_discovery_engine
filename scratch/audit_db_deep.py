import sqlite3
import json

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

print("=== 1. Sources in documents table ===")
c.execute("SELECT source, COUNT(*) FROM documents GROUP BY source")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

print("\n=== 2. Triage buckets count by source ===")
c.execute("""
    SELECT tb.bucket, d.source, COUNT(*)
    FROM triage_buckets tb
    JOIN documents d ON tb.doc_id = d.doc_id
    GROUP BY tb.bucket, d.source
    ORDER BY tb.bucket, d.source
""")
for r in c.fetchall():
    print(f"  Bucket {r[0]} | {r[1]}: {r[2]}")

print("\n=== 3. Failure Point Tags by failure_type, sub_category, and source ===")
c.execute("""
    SELECT fpt.failure_type, fpt.sub_category, d.source, COUNT(*), AVG(fpt.confidence)
    FROM failure_point_tags fpt
    JOIN documents d ON fpt.doc_id = d.doc_id
    GROUP BY fpt.failure_type, fpt.sub_category, d.source
    ORDER BY fpt.failure_type, fpt.sub_category, d.source
""")
rows = c.fetchall()
print(f"Total grouped rows: {len(rows)}")
for r in rows[:25]:
    print(f"  {r[0]} | {r[1]} | {r[2]}: {r[3]} tags (avg conf {r[4]:.3f})")

print("\n=== 4. Check memory_cue_type in failure_point_tags ===")
c.execute("""
    SELECT memory_cue_type, d.source, COUNT(*), AVG(fpt.confidence)
    FROM failure_point_tags fpt
    JOIN documents d ON fpt.doc_id = d.doc_id
    WHERE memory_cue_type IS NOT NULL AND memory_cue_type != ''
    GROUP BY memory_cue_type, d.source
    ORDER BY COUNT(*) DESC
""")
for r in c.fetchall():
    print(f"  Cue: {r[0]} | {r[1]}: {r[2]} (avg conf {r[3]:.3f})")
