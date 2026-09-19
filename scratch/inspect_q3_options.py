import sqlite3

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

print("=== Q3 Options ===")
# Option 1: Bucket A hesitation tags
c.execute("""
    SELECT ht.reason, d.source, count(*), avg(ht.confidence)
    FROM hesitation_tags ht
    JOIN documents d ON ht.doc_id = d.doc_id
    JOIN triage_buckets tb ON ht.doc_id = tb.doc_id
    WHERE tb.bucket = 'A' AND ht.reason LIKE 'forgot_%'
    GROUP BY ht.reason, d.source
""")
for r in c.fetchall():
    print("Option 1 (Bucket A):", r)

# Option 2: Full corpus hesitation tags
c.execute("""
    SELECT ht.reason, d.source, count(*), avg(ht.confidence)
    FROM hesitation_tags ht
    JOIN documents d ON ht.doc_id = d.doc_id
    WHERE ht.reason LIKE 'forgot_%'
    GROUP BY ht.reason, d.source
""")
for r in c.fetchall():
    print("Option 2 (Full corpus):", r)

# Option 3: What if we split forgot_filename_or_album by whether content mentions filename vs album?
c.execute("""
    SELECT 
        CASE 
            WHEN LOWER(d.content) LIKE '%filename%' OR LOWER(d.content) LIKE '%img_%' OR LOWER(d.content) LIKE '%dsc_%' OR LOWER(d.content) LIKE '%.jpg%' THEN 'forgot_filename'
            ELSE 'forgot_album'
        END as split_type,
        d.source, count(*), avg(ht.confidence)
    FROM hesitation_tags ht
    JOIN documents d ON ht.doc_id = d.doc_id
    WHERE ht.reason = 'forgot_filename_or_album'
    GROUP BY split_type, d.source
""")
for r in c.fetchall():
    print("Option 3 (Filename vs Album):", r)
