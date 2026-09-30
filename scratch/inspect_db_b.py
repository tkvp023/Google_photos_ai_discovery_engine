import sqlite3

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

print("=== CHECKING DOCS IN BUCKET B WITH 'search' OR 'find' OR 'face' ===")
c.execute("""
    SELECT d.doc_id, d.source, t.bucket_reason, d.content 
    FROM documents d 
    JOIN triage_buckets t ON d.doc_id = t.doc_id 
    WHERE t.bucket = 'B' AND (LOWER(d.content) LIKE '%search%' OR LOWER(d.content) LIKE '%find%')
    LIMIT 6
""")
for row in c.fetchall():
    clean = row[3].replace("\n", " ")[:140]
    reason = (row[2] or "").replace("\n", " ")[:90]
    print(f"[{row[1]}] Reason: {reason}\n  Text: {clean}...\n")
