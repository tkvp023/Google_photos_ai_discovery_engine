import sqlite3
import json

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

def get_platform_counts(where_clause, params=()):
    c.execute(f"""
        SELECT d.source, COUNT(*), AVG(fpt.confidence)
        FROM failure_point_tags fpt
        JOIN documents d ON fpt.doc_id = d.doc_id
        WHERE {where_clause}
        GROUP BY d.source
    """, params)
    counts = {"Play Store": 0, "App Store": 0, "Reddit": 0, "Hacker News": 0, "YouTube": 0}
    confs = []
    source_map = {
        'playstore': 'Play Store',
        'appstore': 'App Store',
        'reddit': 'Reddit',
        'hackernews': 'Hacker News',
        'youtube': 'YouTube'
    }
    for src, cnt, avg_conf in c.fetchall():
        s_name = source_map.get(src, src)
        counts[s_name] = cnt
        if avg_conf:
            confs.append((cnt, avg_conf))
    total = sum(counts.values())
    overall_conf = sum(cnt * cf for cnt, cf in confs) / total if total > 0 else 0.85
    return counts, total, round(overall_conf, 3)

print("=== Q1 & Q2: memory_cue_type platform counts ===")
for cue in ['combined', 'person', 'time', 'visual_detail', 'text_content', 'event_context', 'place']:
    counts, total, conf = get_platform_counts("fpt.memory_cue_type = ?", (cue,))
    print(f"Cue '{cue}': Total={total} | Counts={counts} | Conf={conf}")

print("\n=== Q4: Query Formulation sub_category platform counts ===")
for sub in ['literal_keyword_match', 'gemini_misinterprets', 'entity_not_recognized', 'compositional_query_fail', 'gemini_conversation_dead_end']:
    counts, total, conf = get_platform_counts("fpt.sub_category = ?", (sub,))
    print(f"Sub '{sub}': Total={total} | Counts={counts} | Conf={conf}")

print("\n=== Q6 & Q10: Recovery sub_category platform counts ===")
for sub in ['fallback_to_scroll', 'no_refinement_support', 'gemini_conversation_dead_end', 'other_recovery', 'cold_restart_each_try']:
    counts, total, conf = get_platform_counts("fpt.sub_category = ?", (sub,))
    print(f"Sub '{sub}': Total={total} | Counts={counts} | Conf={conf}")

print("\n=== Q8: Face Recognition sub_category platform counts ===")
counts, total, conf = get_platform_counts("fpt.sub_category = 'wrong_face_match'")
print(f"Sub 'wrong_face_match': Total={total} | Counts={counts} | Conf={conf}")
