import sqlite3

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

# Let's check how Q3 (forgotten metadata), Q5 (irrelevant results), Q7 (clutter), Q9 (documents), Q10 (workarounds) map to tags
print("=== Q3 tags in hesitation_tags or failure_point_tags ===")
# In hesitation_tags:
for tag in ['forgot_exact_date', 'forgot_filename_or_album', 'forgot_exact_location']:
    c.execute("""
        SELECT d.source, COUNT(*), AVG(ht.confidence)
        FROM hesitation_tags ht
        JOIN documents d ON ht.doc_id = d.doc_id
        WHERE ht.reason = ?
        GROUP BY d.source
    """, (tag,))
    counts = {r[0]: r[1] for r in c.fetchall()}
    print(f"Hesitation '{tag}': Total={sum(counts.values())} | Counts={counts}")

print("\n=== Q7 clutter tags in failure_point_tags and hesitation_tags ===")
c.execute("""
    SELECT d.source, COUNT(*)
    FROM failure_point_tags fpt
    JOIN documents d ON fpt.doc_id = d.doc_id
    WHERE fpt.sub_category = 'clutter_pollutes_results'
    GROUP BY d.source
""")
print("failure_point_tags clutter_pollutes_results:", c.fetchall())

print("\n=== Q9 text / document tags ===")
for cue in ['text_content']:
    c.execute("""
        SELECT d.source, COUNT(*), AVG(fpt.confidence)
        FROM failure_point_tags fpt
        JOIN documents d ON fpt.doc_id = d.doc_id
        WHERE fpt.memory_cue_type = ?
        GROUP BY d.source
    """, (cue,))
    counts = {r[0]: r[1] for r in c.fetchall()}
    print(f"Cue '{cue}': Total={sum(counts.values())} | Counts={counts}")

print("\n=== Check how Q7, Q8, Q9, Q10 were constructed in question_mapper.py ===")
