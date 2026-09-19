import os
import sqlite3
import csv

print("=== Checking data/all_scraped_reviews.csv ===")
if os.path.exists("data/all_scraped_reviews.csv"):
    with open("data/all_scraped_reviews.csv", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print("CSV rows count:", len(rows))
        if rows:
            print("Columns:", list(rows[0].keys()))
            sources = {}
            for r in rows:
                s = r.get("source", "unknown")
                sources[s] = sources.get(s, 0) + 1
            print("Source distribution:", sources)

for db_path in ["data/db.sqlite", "data/discovery_engine.db", "pipeline/db/corpus.db"]:
    if os.path.exists(db_path):
        print(f"\n=== Checking {db_path} ===")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        for t in tables:
            tname = t[0]
            try:
                c.execute(f"SELECT COUNT(*) FROM {tname}")
                cnt = c.fetchone()[0]
                print(f"  Table {tname}: {cnt} rows")
            except Exception as e:
                print(f"  Table {tname} error: {e}")
