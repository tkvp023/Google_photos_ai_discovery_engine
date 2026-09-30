import sqlite3

for db_path in ['data/search_only_corpus/search_only_corpus.sqlite', 'data/db.sqlite']:
    print(f'=== DB: {db_path} ===')
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print('  Tables:', tables)
        for t in tables:
            count = cur.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
            print(f"    {t}: {count} rows")
            cols = [c[1] for c in cur.execute(f"PRAGMA table_info({t})").fetchall()]
            print(f"      columns: {cols[:8]}... (total {len(cols)})")
        conn.close()
    except Exception as e:
        print('  Error:', e)
