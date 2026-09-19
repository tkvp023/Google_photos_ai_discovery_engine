import sqlite3

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

print("=== Check Subcategories and Memory Cues in failure_point_tags ===")
c.execute("""
    SELECT failure_type, sub_category, count(*), avg(confidence)
    FROM failure_point_tags
    GROUP BY failure_type, sub_category
    ORDER BY failure_type, count(*) DESC
""")
for r in c.fetchall():
    print(f"{r[0]:15} | {r[1]:30} | {r[2]:3} | {r[3]:.3f}")

print("\n=== Check Cognitive Stages (failure_type) ===")
c.execute("""
    SELECT failure_type, count(*), count(distinct doc_id), avg(confidence)
    FROM failure_point_tags
    GROUP BY failure_type
""")
for r in c.fetchall():
    print(f"{r[0]:15} | {r[1]:3} tags | {r[2]:3} docs | conf={r[3]:.3f}")

