import sqlite3

conn = sqlite3.connect('data/db.sqlite')
c = conn.cursor()

# Check how many documents have content ending in '...'
ending_ellipsis = c.execute("SELECT COUNT(*) FROM documents WHERE content LIKE '%...'").fetchone()[0]
total = c.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
print(f"Docs ending with '...': {ending_ellipsis} / {total}")

# Look at full content of some docs
print("\nSample docs without ending ellipsis:")
samples = c.execute("SELECT source, content FROM documents WHERE content NOT LIKE '%...' AND LENGTH(content) > 100 LIMIT 5").fetchall()
for s, text in samples:
    print(f"[{s}] len={len(text)}:\n{text}\n")
