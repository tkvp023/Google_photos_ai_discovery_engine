import sqlite3
import json

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

# Check how failure_point_tags maps to documents and platforms
# Columns in failure_point_tags: id, doc_id, failure_type, sub_category, memory_cue_type, confidence, evidence_quote, search_type
# Columns in documents: doc_id, source, ...

print("=== 1. Check all sub_category counts per platform in db.sqlite ===")
c.execute("""
    SELECT fpt.sub_category, d.source, COUNT(*), AVG(fpt.confidence)
    FROM failure_point_tags fpt
    JOIN documents d ON fpt.doc_id = d.doc_id
    GROUP BY fpt.sub_category, d.source
    ORDER BY fpt.sub_category, d.source
""")
for r in c.fetchall():
    print(f"sub_category: {r[0]} | source: {r[1]} | count: {r[2]} | avg_conf: {r[3]:.3f}")

print("\n=== 2. Check all memory_cue_type counts per platform in db.sqlite ===")
c.execute("""
    SELECT fpt.memory_cue_type, d.source, COUNT(*), AVG(fpt.confidence)
    FROM failure_point_tags fpt
    JOIN documents d ON fpt.doc_id = d.doc_id
    GROUP BY fpt.memory_cue_type, d.source
    ORDER BY fpt.memory_cue_type, d.source
""")
for r in c.fetchall():
    print(f"memory_cue_type: {r[0]} | source: {r[1]} | count: {r[2]} | avg_conf: {r[3]:.3f}")

print("\n=== 3. Check hesitation_tags by reason and platform (for systemic gaps) ===")
c.execute("""
    SELECT ht.reason, d.source, COUNT(*), AVG(ht.confidence)
    FROM hesitation_tags ht
    JOIN documents d ON ht.doc_id = d.doc_id
    GROUP BY ht.reason, d.source
    ORDER BY COUNT(*) DESC
    LIMIT 30
""")
for r in c.fetchall():
    print(f"hesitation_reason: {r[0]} | source: {r[1]} | count: {r[2]} | avg_conf: {r[3]:.3f}")
