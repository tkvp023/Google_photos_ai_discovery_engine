import sqlite3

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

print("=== ALL failure_point_tags sub_categories ===")
c.execute("""
    SELECT failure_type, sub_category, COUNT(*), AVG(confidence)
    FROM failure_point_tags
    GROUP BY failure_type, sub_category
    ORDER BY failure_type, COUNT(*) DESC
""")
for r in c.fetchall():
    print(f"  {r[0]:15} | {r[1]:30} | {r[2]:3} | {r[3]:.4f}")

print("\n=== ALL failure_point_tags memory_cue_types ===")
c.execute("""
    SELECT memory_cue_type, COUNT(*), AVG(confidence)
    FROM failure_point_tags
    GROUP BY memory_cue_type
    ORDER BY COUNT(*) DESC
""")
for r in c.fetchall():
    print(f"  {r[0]:20} | {r[1]:3} | {r[2]:.4f}")

print("\n=== ALL hesitation_tags reasons in Bucket A ===")
c.execute("""
    SELECT ht.reason, COUNT(*), AVG(ht.confidence)
    FROM hesitation_tags ht
    JOIN triage_buckets tb ON ht.doc_id = tb.doc_id
    WHERE tb.bucket = 'A'
    GROUP BY ht.reason
    ORDER BY COUNT(*) DESC
""")
for r in c.fetchall():
    print(f"  {r[0]:35} | {r[1]:3} | {r[2]:.4f}")

print("\n=== ALL hesitation_tags reasons overall ===")
c.execute("""
    SELECT ht.reason, COUNT(*), AVG(ht.confidence)
    FROM hesitation_tags ht
    GROUP BY ht.reason
    ORDER BY COUNT(*) DESC
""")
for r in c.fetchall():
    print(f"  {r[0]:35} | {r[1]:4} | {r[2]:.4f}")
