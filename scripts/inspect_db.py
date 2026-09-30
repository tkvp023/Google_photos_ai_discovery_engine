import sqlite3

def inspect(path):
    print(f"\n{'='*50}\nInspecting: {path}\n{'='*50}")
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    for t in tables:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = c.fetchone()[0]
        print(f"  • {t:25}: {cnt:,} rows")
    conn.close()

if __name__ == "__main__":
    inspect("data/db.sqlite")
    inspect("data/search_only_corpus/search_only_corpus.sqlite")
