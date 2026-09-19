import sqlite3
import json

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

print("=== Schema of data/db.sqlite ===")
c.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
for row in c.fetchall():
    print(f"\nTable: {row[0]}")
    print(row[1])

print("\n=== Sample document columns ===")
c.execute("PRAGMA table_info(documents)")
print([col[1] for col in c.fetchall()])

print("\n=== Sample triage_buckets columns ===")
c.execute("PRAGMA table_info(triage_buckets)")
print([col[1] for col in c.fetchall()])

print("\n=== Sample failure_point_tags columns ===")
c.execute("PRAGMA table_info(failure_point_tags)")
print([col[1] for col in c.fetchall()])

print("\n=== Sample question_mappings columns ===")
c.execute("PRAGMA table_info(question_mappings)")
print([col[1] for col in c.fetchall()])
