import sqlite3
import os

print("Listing tables in corpus.db and any other db files:")
for f in os.listdir("."):
    if f.endswith(".db") or f.endswith(".sqlite"):
        print("DB file:", f)
        try:
            conn = sqlite3.connect(f)
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = c.fetchall()
            print("  Tables:", tables)
            for t in tables:
                c.execute(f"SELECT COUNT(*) FROM {t[0]}")
                print(f"    {t[0]}: {c.fetchone()[0]} rows")
        except Exception as e:
            print("  Error:", e)
