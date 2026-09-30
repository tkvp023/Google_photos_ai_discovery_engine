import sqlite3
import json
from pathlib import Path

db_path = Path("data/search_only_corpus/search_only_corpus.sqlite")
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM search_only_documents")
total_docs = c.fetchone()[0]

c.execute("SELECT classification, COUNT(*) FROM search_only_documents GROUP BY classification")
cls_counts = dict(c.fetchall())

c.execute("SELECT COUNT(*) FROM search_only_documents WHERE classification = 'in_scope' AND is_quote_verified = 1")
verified_in_scope = c.fetchone()[0]

c.execute("SELECT stage, COUNT(*) FROM flow_stages_evidenced GROUP BY stage ORDER BY COUNT(*) DESC")
stages = c.fetchall()

c.execute("SELECT source, COUNT(*) FROM search_only_documents WHERE classification = 'in_scope' GROUP BY source ORDER BY COUNT(*) DESC")
sources = c.fetchall()

conn.close()

print(f"Total DB records: {total_docs:,}")
print(f"Classification counts: {cls_counts}")
print(f"Verified In-Scope: {verified_in_scope} / {cls_counts.get('in_scope', 0)} ({verified_in_scope / max(1, cls_counts.get('in_scope', 0)) * 100:.1f}%)")
print("\nFlow Stages Breakdown:")
for st, cnt in stages:
    print(f"  • {st:20}: {cnt:4} ({cnt / verified_in_scope * 100:.1f}%)")
print("\nPlatform Breakdown:")
for src, cnt in sources:
    print(f"  • {src:15}: {cnt:4} ({cnt / verified_in_scope * 100:.1f}%)")
