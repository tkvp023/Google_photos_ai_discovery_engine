import sqlite3

conn = sqlite3.connect('data/db.sqlite')
cur = conn.cursor()

print("=== failure_point_tags by failure_type ===")
for r in cur.execute("SELECT failure_type, count(*), round(count(*) * 100.0 / 1616, 2) FROM failure_point_tags GROUP BY failure_type ORDER BY count(*) DESC").fetchall():
    print(f"  {r[0]}: {r[1]} docs ({r[2]}%)")

print("\n=== failure_point_tags by failure_type and sub_category ===")
for r in cur.execute("SELECT failure_type, sub_category, count(*), round(count(*) * 100.0 / 1616, 2) FROM failure_point_tags GROUP BY failure_type, sub_category ORDER BY count(*) DESC").fetchall():
    print(f"  {r[0]} -> {r[1]}: {r[2]} docs ({r[3]}%)")

print("\n=== failure_point_tags by memory_cue_type ===")
for r in cur.execute("SELECT memory_cue_type, count(*), round(count(*) * 100.0 / 1616, 2) FROM failure_point_tags GROUP BY memory_cue_type ORDER BY count(*) DESC").fetchall():
    print(f"  {r[0]}: {r[1]} docs ({r[2]}%)")

print("\n=== triage_buckets by bucket ===")
for r in cur.execute("SELECT bucket, count(*), round(count(*) * 100.0 / 1616, 2) FROM triage_buckets GROUP BY bucket ORDER BY count(*) DESC").fetchall():
    print(f"  {r[0]}: {r[1]} docs ({r[2]}%)")

print("\n=== triage_buckets by search_type ===")
for r in cur.execute("SELECT search_type, count(*), round(count(*) * 100.0 / 1616, 2) FROM triage_buckets GROUP BY search_type ORDER BY count(*) DESC").fetchall():
    print(f"  {r[0]}: {r[1]} docs ({r[2]}%)")

conn.close()
