import sqlite3

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

print("=== Check documents in Bucket A with metadata words ===")
c.execute("""
    SELECT COUNT(*) FROM documents d
    JOIN triage_buckets tb ON d.doc_id = tb.doc_id AND tb.bucket = 'A'
    WHERE d.content LIKE '%date%' OR d.content LIKE '%year%' OR d.content LIKE '%month%'
""")
print("Docs mentioning date/year/month in Bucket A:", c.fetchone()[0])

c.execute("""
    SELECT d.source, COUNT(*) FROM documents d
    JOIN triage_buckets tb ON d.doc_id = tb.doc_id AND tb.bucket = 'A'
    WHERE d.content LIKE '%date%' OR d.content LIKE '%year%' OR d.content LIKE '%month%'
    GROUP BY d.source
""")
print("By platform:", c.fetchall())

print("\n=== Check docs mentioning filename/IMG/DSC in Bucket A ===")
c.execute("""
    SELECT d.source, COUNT(*) FROM documents d
    JOIN triage_buckets tb ON d.doc_id = tb.doc_id AND tb.bucket = 'A'
    WHERE d.content LIKE '%file%' OR d.content LIKE '%name%' OR d.content LIKE '%IMG%'
    GROUP BY d.source
""")
print("By platform:", c.fetchall())
