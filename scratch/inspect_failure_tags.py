import sqlite3

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

print("=== Count of failure_point_tags by failure_type ===")
c.execute("SELECT failure_type, COUNT(*) FROM failure_point_tags GROUP BY failure_type")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

print("\n=== Count of failure_point_tags by sub_category ===")
c.execute("SELECT failure_type, sub_category, COUNT(*), AVG(confidence) FROM failure_point_tags GROUP BY failure_type, sub_category ORDER BY failure_type, COUNT(*) DESC")
for r in c.fetchall():
    print(f"  {r[0]} | {r[1]}: {r[2]} (avg conf {r[3]:.3f})")

print("\n=== Sample failure_point_tags with evidence_quote ===")
c.execute("SELECT id, doc_id, failure_type, sub_category, confidence, evidence_quote FROM failure_point_tags LIMIT 10")
for r in c.fetchall():
    print(f"ID {r[0]} | Doc {r[1]} | {r[2]}/{r[3]} | Conf: {r[4]} | Quote: {r[5][:80]}...")
