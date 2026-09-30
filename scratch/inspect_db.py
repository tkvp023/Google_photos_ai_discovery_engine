import sqlite3

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

for b in ["A", "B", "C", "D"]:
    print(f"\n==================== SAMPLES FROM BUCKET {b} ====================")
    c.execute("""
        SELECT d.doc_id, d.source, t.bucket_reason, d.content 
        FROM documents d 
        JOIN triage_buckets t ON d.doc_id = t.doc_id 
        WHERE t.bucket = ? 
        LIMIT 5
    """, (b,))
    for row in c.fetchall():
        clean = row[3].replace("\n", " ")[:150]
        reason = (row[2] or "").replace("\n", " ")[:100]
        print(f"[{row[1]}] Reason: {reason}\n  Text: {clean}...\n")
