import sqlite3
import json

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

print("=== failure_point_tags distinct sub_category and memory_cue_type ===")
c.execute("""
    SELECT failure_type, sub_category, memory_cue_type, COUNT(*), AVG(confidence)
    FROM failure_point_tags
    GROUP BY failure_type, sub_category, memory_cue_type
    ORDER BY failure_type, sub_category
""")
for r in c.fetchall():
    print(r)
