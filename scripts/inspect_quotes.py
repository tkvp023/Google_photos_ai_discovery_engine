import sqlite3

conn = sqlite3.connect('data/db.sqlite')
c = conn.cursor()
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables:", tables)

for t in tables:
    count = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    cols = [d[0] for d in c.execute(f"SELECT * FROM {t} LIMIT 1").description]
    print(f"Table: {t} ({count} rows) -> Columns: {cols}")
