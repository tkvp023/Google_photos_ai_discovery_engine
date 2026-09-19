import sqlite3
import json

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

def run_query(sql, params=()):
    c.execute(sql, params)
    rows = c.fetchall()
    counts = {"Play Store": 0, "App Store": 0, "Reddit": 0, "Hacker News": 0, "YouTube": 0}
    source_map = {
        'playstore': 'Play Store',
        'appstore': 'App Store',
        'reddit': 'Reddit',
        'hackernews': 'Hacker News',
        'youtube': 'YouTube'
    }
    confs = []
    for r in rows:
        src = source_map.get(r[0], r[0])
        cnt = r[1]
        counts[src] = cnt
        if len(r) > 2 and r[2] is not None:
            confs.append((cnt, r[2]))
    tot = sum(counts.values())
    avg_c = sum(cnt * cf for cnt, cf in confs) / tot if tot > 0 and confs else 0.85
    return counts, tot, round(avg_c, 3)

print("--- Q3: Hesitation tags in Bucket A vs overall ---")
for r in ['forgot_exact_date', 'forgot_filename_or_album', 'forgot_exact_location']:
    sql_a = """
        SELECT d.source, COUNT(*), AVG(ht.confidence)
        FROM hesitation_tags ht
        JOIN documents d ON ht.doc_id = d.doc_id
        JOIN triage_buckets tb ON ht.doc_id = tb.doc_id
        WHERE tb.bucket = 'A' AND ht.reason = ?
        GROUP BY d.source
    """
    counts_a, tot_a, conf_a = run_query(sql_a, (r,))
    print(f"Bucket A {r:25}: tot={tot_a:3}, conf={conf_a:.3f}, counts={counts_a}")

    sql_all = """
        SELECT d.source, COUNT(*), AVG(ht.confidence)
        FROM hesitation_tags ht
        JOIN documents d ON ht.doc_id = d.doc_id
        WHERE ht.reason = ?
        GROUP BY d.source
    """
    counts_all, tot_all, conf_all = run_query(sql_all, (r,))
    print(f"All docs {r:25}: tot={tot_all:3}, conf={conf_all:.3f}, counts={counts_all}")

print("\n--- Q7: Clutter in Bucket A ---")
clutter_categories = [
    ("UI Screenshots & Temporary Notes", "LOWER(d.content) LIKE '%screenshot%'"),
    ("WhatsApp Forwarded Media & Memes", "LOWER(d.content) LIKE '%whatsapp%' OR LOWER(d.content) LIKE '%meme%'"),
    ("Financial Receipts & Invoices", "LOWER(d.content) LIKE '%receipt%' OR LOWER(d.content) LIKE '%bill%' OR LOWER(d.content) LIKE '%invoice%'"),
    ("Product Barcodes & Medicine Labels", "LOWER(d.content) LIKE '%barcode%' OR LOWER(d.content) LIKE '%label%' OR LOWER(d.content) LIKE '%prescription%'"),
]
for label, cond in clutter_categories:
    sql = f"""
        SELECT d.source, COUNT(*), AVG(tb.confidence)
        FROM documents d
        JOIN triage_buckets tb ON d.doc_id = tb.doc_id
        WHERE tb.bucket = 'A' AND ({cond})
        GROUP BY d.source
    """
    counts, tot, conf = run_query(sql)
    print(f"{label:35}: tot={tot:3}, conf={conf:.3f}, counts={counts}")

print("\n--- Q8: Face Recognition Breakdown in failure_point_tags ---")
# 1. Wrong Face Match / Merged Identities: wrong_face_match (29)
sql = "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'wrong_face_match' GROUP BY d.source"
print("Wrong Face Match:", run_query(sql))

# 2. Untagged Person in Group Candid Shots: entity_not_recognized with person (10) + person_unnamed (1) = 11
sql = "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE (fpt.sub_category = 'entity_not_recognized' AND fpt.memory_cue_type = 'person') OR fpt.sub_category = 'person_unnamed' GROUP BY d.source"
print("Untagged Person:", run_query(sql))

# 3. Pet / Animal Misidentification: too_many_similar / visual_fragment (5) or wrong_face_match with pet keywords
sql = """
    SELECT d.source, COUNT(*), AVG(fpt.confidence)
    FROM failure_point_tags fpt
    JOIN documents d ON fpt.doc_id = d.doc_id
    WHERE fpt.sub_category IN ('too_many_similar', 'cant_distinguish_duplicates')
    GROUP BY d.source
"""
print("Duplicate / Similar Faces:", run_query(sql))

# 4. Contextual Disambiguation Drop: no_context_in_results with person (0) or other_evaluation with person (0)
# Let's check all face-related tags:
sql = """
    SELECT d.source, COUNT(*), AVG(fpt.confidence)
    FROM failure_point_tags fpt
    JOIN documents d ON fpt.doc_id = d.doc_id
    WHERE fpt.memory_cue_type = 'person'
    GROUP BY d.source
"""
print("All Person Memory Cues:", run_query(sql))

print("\n--- Q9: Text & Document Search in failure_point_tags & Bucket A ---")
sql = "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'text_content' GROUP BY d.source"
print("text_content cue:", run_query(sql))

# Breakdown of text_content:
for sub in ['literal_keyword_match', 'clutter_pollutes_results', 'entity_not_recognized', 'gemini_misinterprets', 'other_interpretation', 'fallback_to_scroll']:
    sql = f"SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'text_content' AND fpt.sub_category = '{sub}' GROUP BY d.source"
    c_res, t_res, cf_res = run_query(sql)
    if t_res > 0:
        print(f"  text_content + {sub:25}: tot={t_res:2}, conf={cf_res:.3f}, counts={c_res}")

print("\n--- Q10: Workarounds & Recovery in failure_point_tags & Bucket A ---")
for sub in ['fallback_to_scroll', 'no_refinement_support', 'gemini_conversation_dead_end', 'other_recovery', 'cold_restart_each_try']:
    sql = f"SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = '{sub}' GROUP BY d.source"
    c_res, t_res, cf_res = run_query(sql)
    print(f"  recovery: {sub:28}: tot={t_res:2}, conf={cf_res:.3f}, counts={c_res}")

# In hesitation_tags:
for h in ['timeline_navigation_clunky', 'endless_scrolling_fatigue', 'competitor_switching_apple']:
    sql = f"""
        SELECT d.source, COUNT(*), AVG(ht.confidence)
        FROM hesitation_tags ht
        JOIN documents d ON ht.doc_id = d.doc_id
        JOIN triage_buckets tb ON ht.doc_id = tb.doc_id
        WHERE tb.bucket = 'A' AND ht.reason = '{h}'
        GROUP BY d.source
    """
    c_res, t_res, cf_res = run_query(sql)
    print(f"  hesitation (Bucket A) {h:28}: tot={t_res:2}, conf={cf_res:.3f}, counts={c_res}")

