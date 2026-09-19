import sqlite3
import json

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

def query_fpt(where_clause, params=()):
    c.execute(f"""
        SELECT d.source, COUNT(*), AVG(fpt.confidence)
        FROM failure_point_tags fpt
        JOIN documents d ON fpt.doc_id = d.doc_id
        WHERE {where_clause}
        GROUP BY d.source
    """, params)
    source_map = {
        'playstore': 'Play Store',
        'appstore': 'App Store',
        'reddit': 'Reddit',
        'hackernews': 'Hacker News',
        'youtube': 'YouTube'
    }
    counts = {"Play Store": 0, "App Store": 0, "Reddit": 0, "Hacker News": 0, "YouTube": 0}
    confs = []
    for src, cnt, avg_c in c.fetchall():
        s = source_map.get(src, src)
        counts[s] = cnt
        confs.append((cnt, avg_c))
    tot = sum(counts.values())
    avg_conf = sum(cnt * cf for cnt, cf in confs) / tot if tot > 0 else 0.85
    return counts, tot, round(avg_conf, 3)

print("--- Testing Real DB Attribution for All Failure Point Categories ---")

# Let's check how each question maps to failure_point_tags:
# Q1: Memory Cues (Photos People Struggle to Find)
print("\n=== Q1: Memory Cues ===")
for cue in ['combined', 'person', 'time', 'visual_detail', 'text_content', 'event_context', 'place']:
    counts, tot, conf = query_fpt("fpt.memory_cue_type = ?", (cue,))
    print(f"Q1 {cue}: tot={tot}, conf={conf}, counts={counts}")

# Q2: Retained Memory Clues
print("\n=== Q2: Retained Clues ===")
for cue in ['combined', 'person', 'time', 'visual_detail', 'text_content', 'event_context', 'place']:
    counts, tot, conf = query_fpt("fpt.memory_cue_type = ?", (cue,))
    print(f"Q2 {cue}: tot={tot}, conf={conf}, counts={counts}")

# Q4: Incomplete Query Formulation
print("\n=== Q4: Query Formulation ===")
for sub in ['literal_keyword_match', 'gemini_misinterprets', 'entity_not_recognized', 'compositional_query_fail', 'gemini_conversation_dead_end']:
    counts, tot, conf = query_fpt("fpt.sub_category = ?", (sub,))
    print(f"Q4 {sub}: tot={tot}, conf={conf}, counts={counts}")

# Q6: Endless Timeline Scrolling
print("\n=== Q6: Scrolling / Recovery ===")
for sub in ['fallback_to_scroll', 'no_refinement_support', 'gemini_conversation_dead_end', 'other_recovery', 'cold_restart_each_try']:
    counts, tot, conf = query_fpt("fpt.sub_category = ?", (sub,))
    print(f"Q6 {sub}: tot={tot}, conf={conf}, counts={counts}")

# Q8: Face Recognition
print("\n=== Q8: Face Recognition ===")
counts, tot, conf = query_fpt("fpt.sub_category = 'wrong_face_match'")
print(f"Q8 wrong_face_match: tot={tot}, conf={conf}, counts={counts}")
counts, tot, conf = query_fpt("fpt.sub_category = 'entity_not_recognized' AND fpt.memory_cue_type = 'person'")
print(f"Q8 untagged person in group: tot={tot}, conf={conf}, counts={counts}")
