import sqlite3

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

print("=== Failure tags joined with Question Mappings (Bucket A only) ===")
for qid in range(1, 11):
    c.execute("""
        SELECT COUNT(DISTINCT d.doc_id), COUNT(fpt.id)
        FROM documents d
        JOIN triage_buckets tb ON d.doc_id = tb.doc_id AND tb.bucket = 'A'
        JOIN question_mappings qm ON d.doc_id = qm.doc_id AND qm.question_id = ?
        LEFT JOIN failure_point_tags fpt ON d.doc_id = fpt.doc_id
    """, (qid,))
    docs_cnt, tags_cnt = c.fetchone()
    print(f"Q{qid}: {docs_cnt} Bucket A docs, {tags_cnt} failure tags")
