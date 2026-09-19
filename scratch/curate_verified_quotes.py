import sqlite3
import json

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

source_map = {
    'playstore': 'Play Store',
    'appstore': 'App Store',
    'reddit': 'Reddit',
    'hackernews': 'Hacker News',
    'youtube': 'YouTube'
}

used_quotes = set()

def fetch_curated_quotes(where_clause, limit=5):
    c.execute(f"""
        SELECT fpt.evidence_quote, fpt.confidence, d.source, fpt.sub_category, fpt.memory_cue_type, d.doc_id
        FROM failure_point_tags fpt
        JOIN documents d ON fpt.doc_id = d.doc_id
        WHERE ({where_clause}) AND INSTR(d.content, fpt.evidence_quote) > 0
        ORDER BY fpt.confidence DESC, LENGTH(fpt.evidence_quote) DESC
    """)
    quotes = []
    for r in c.fetchall():
        q_text = r[0].strip()
        # Clean quotes
        if q_text in used_quotes or len(q_text) < 25:
            continue
        used_quotes.add(q_text)
        quotes.append({
            "text": q_text,
            "confidence": round(float(r[1]), 3),
            "source": source_map.get(r[2], r[2].capitalize()),
            "tags": [r[3].replace('_', ' '), r[4].replace('_', ' ')]
        })
        if len(quotes) >= limit:
            break
    return quotes

print("=== Testing Curated Quotes for All Questions ===")

# Q1: Memory Cues
q1_quotes = fetch_curated_quotes("fpt.memory_cue_type IN ('combined', 'person', 'time', 'visual_detail', 'text_content')")
print(f"Q1 quotes: {len(q1_quotes)}")
for q in q1_quotes[:2]:
    print("  ", q["source"], q["confidence"], q["tags"], q["text"][:100])

# Q2: Retained Memory Clues (visual, companion, time, setting)
q2_quotes = fetch_curated_quotes("fpt.memory_cue_type IN ('visual_detail', 'person', 'time', 'event_context', 'place') AND fpt.sub_category NOT IN ('wrong_face_match')")
print(f"Q2 quotes: {len(q2_quotes)}")
for q in q2_quotes[:2]:
    print("  ", q["source"], q["confidence"], q["tags"], q["text"][:100])

# Q3: Forgotten Metadata (dates, filenames, albums)
q3_quotes = fetch_curated_quotes("fpt.sub_category IN ('temporal_mismatch', 'temporal_vagueness') OR LOWER(fpt.evidence_quote) LIKE '%date%' OR LOWER(fpt.evidence_quote) LIKE '%year%' OR LOWER(fpt.evidence_quote) LIKE '%month%' OR LOWER(fpt.evidence_quote) LIKE '%album%'")
print(f"Q3 quotes: {len(q3_quotes)}")
for q in q3_quotes[:2]:
    print("  ", q["source"], q["confidence"], q["tags"], q["text"][:100])

# Q4: Incomplete Query Formulation (keyword matching, natural language misinterprets, dead ends)
q4_quotes = fetch_curated_quotes("fpt.sub_category IN ('literal_keyword_match', 'gemini_misinterprets', 'compositional_query_fail', 'gemini_conversation_dead_end')")
print(f"Q4 quotes: {len(q4_quotes)}")
for q in q4_quotes[:2]:
    print("  ", q["source"], q["confidence"], q["tags"], q["text"][:100])

# Q5: Irrelevant Results & False Misses (zero results, irrelevant photos, entity not recognized)
q5_quotes = fetch_curated_quotes("fpt.sub_category IN ('entity_not_recognized', 'no_context_in_results', 'literal_keyword_match', 'other_interpretation') OR LOWER(fpt.evidence_quote) LIKE '%zero%' OR LOWER(fpt.evidence_quote) LIKE '%nothing%' OR LOWER(fpt.evidence_quote) LIKE '%no result%'")
print(f"Q5 quotes: {len(q5_quotes)}")
for q in q5_quotes[:2]:
    print("  ", q["source"], q["confidence"], q["tags"], q["text"][:100])

# Q6: Endless Timeline Scrolling (scrolling, no refinement)
q6_quotes = fetch_curated_quotes("fpt.sub_category IN ('fallback_to_scroll', 'no_refinement_support')")
print(f"Q6 quotes: {len(q6_quotes)}")
for q in q6_quotes[:2]:
    print("  ", q["source"], q["confidence"], q["tags"], q["text"][:100])

# Q7: Clutter & Screenshots
q7_quotes = fetch_curated_quotes("fpt.sub_category = 'clutter_pollutes_results' OR LOWER(fpt.evidence_quote) LIKE '%screenshot%' OR LOWER(fpt.evidence_quote) LIKE '%clutter%' OR LOWER(fpt.evidence_quote) LIKE '%receipt%'")
print(f"Q7 quotes: {len(q7_quotes)}")
for q in q7_quotes[:2]:
    print("  ", q["source"], q["confidence"], q["tags"], q["text"][:100])

# Q8: Face Recognition Failures (wrong face match)
q8_quotes = fetch_curated_quotes("fpt.sub_category = 'wrong_face_match' OR (fpt.memory_cue_type = 'person' AND fpt.sub_category = 'entity_not_recognized')")
print(f"Q8 quotes: {len(q8_quotes)}")
for q in q8_quotes[:2]:
    print("  ", q["source"], q["confidence"], q["tags"], q["text"][:100])

# Q9: Text & Document Search Failures (text_content)
q9_quotes = fetch_curated_quotes("fpt.memory_cue_type = 'text_content' OR LOWER(fpt.evidence_quote) LIKE '%license%' OR LOWER(fpt.evidence_quote) LIKE '%text%' OR LOWER(fpt.evidence_quote) LIKE '%sign%' OR LOWER(fpt.evidence_quote) LIKE '%document%'")
print(f"Q9 quotes: {len(q9_quotes)}")
for q in q9_quotes[:2]:
    print("  ", q["source"], q["confidence"], q["tags"], q["text"][:100])

# Q10: Workarounds & Switching
q10_quotes = fetch_curated_quotes("fpt.sub_category IN ('other_recovery', 'cold_restart_each_try') OR LOWER(fpt.evidence_quote) LIKE '%whatsapp%' OR LOWER(fpt.evidence_quote) LIKE '%apple%' OR LOWER(fpt.evidence_quote) LIKE '%scroll%' OR LOWER(fpt.evidence_quote) LIKE '%immich%'")
print(f"Q10 quotes: {len(q10_quotes)}")
for q in q10_quotes[:2]:
    print("  ", q["source"], q["confidence"], q["tags"], q["text"][:100])

print(f"\nTotal unique quotes used: {len(used_quotes)}")
