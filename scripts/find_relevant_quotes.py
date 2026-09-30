import sqlite3
import re

conn = sqlite3.connect('data/db.sqlite')
c = conn.cursor()

print("Total documents:", c.execute("SELECT COUNT(*) FROM documents").fetchone()[0])

# Check sources
sources = c.execute("SELECT source, COUNT(*) FROM documents GROUP BY source").fetchall()
print("Sources:", sources)

# Check documents mentioning search, photo, find, scroll, face, clutter, screenshot, etc.
keywords = ['search', 'find', 'photo', 'picture', 'scroll', 'clutter', 'screenshot', 'face', 'pet', 'receipt', 'date', 'remember', 'album', 'whatsapp']
for kw in keywords:
    cnt = c.execute("SELECT COUNT(*) FROM documents WHERE LOWER(content) LIKE ?", (f"%{kw}%",)).fetchone()[0]
    print(f"Docs containing '{kw}': {cnt}")
