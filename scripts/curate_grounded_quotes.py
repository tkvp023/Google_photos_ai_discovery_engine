import sqlite3
import json

conn = sqlite3.connect('data/db.sqlite')
c = conn.cursor()

def search_quotes(terms, exclude_terms=None, limit=5, min_len=40, max_len=1200):
    query_parts = []
    for term in terms:
        query_parts.append(f"LOWER(content) LIKE '%{term.lower()}%'")
    sql = f"SELECT doc_id, source, source_id, content, timestamp, rating FROM documents WHERE ({' OR '.join(query_parts)})"
    if exclude_terms:
        for ex in exclude_terms:
            sql += f" AND LOWER(content) NOT LIKE '%{ex.lower()}%'"
    sql += f" AND LENGTH(content) >= {min_len} AND LENGTH(content) <= {max_len}"
    
    rows = c.execute(sql).fetchall()
    return rows

print("Testing quote search for Q1 (Struggled photo types: candid, document, receipt, unposed, old photos)...")
q1_candidates = search_quotes(['receipt', 'document', 'candid', 'old photo', 'prescription', 'find photo', 'retrieve'], limit=10)
print(f"Found {len(q1_candidates)} candidates for Q1")
for r in q1_candidates[:3]:
    print(f"[{r[1]} | {r[2]}] {r[3]}\n")
