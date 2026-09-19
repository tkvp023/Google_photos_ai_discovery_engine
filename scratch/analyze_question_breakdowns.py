import sqlite3
import json

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

print("=== Check subcategories in failure_point_tags ===")
c.execute("""
    SELECT failure_type, sub_category, COUNT(*), AVG(confidence)
    FROM failure_point_tags
    GROUP BY failure_type, sub_category
    ORDER BY failure_type, COUNT(*) DESC
""")
for r in c.fetchall():
    print(f"{r[0]} | {r[1]}: count={r[2]}, avg_conf={r[3]:.4f}")

print("\n=== Check memory_cue_type in failure_point_tags ===")
c.execute("""
    SELECT memory_cue_type, COUNT(*), AVG(confidence)
    FROM failure_point_tags
    GROUP BY memory_cue_type
    ORDER BY COUNT(*) DESC
""")
for r in c.fetchall():
    print(f"memory_cue: {r[0]}: count={r[1]}, avg_conf={r[2]:.4f}")

print("\n=== Check hesitation_tags counts ===")
c.execute("""
    SELECT reason, COUNT(*), AVG(confidence)
    FROM hesitation_tags
    GROUP BY reason
    ORDER BY COUNT(*) DESC
""")
for r in c.fetchall():
    print(f"hesitation: {r[0]}: count={r[1]}, avg_conf={r[2]:.4f}")
