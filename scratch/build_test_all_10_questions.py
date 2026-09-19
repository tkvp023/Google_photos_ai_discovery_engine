import sqlite3
import json
from pathlib import Path

db_path = Path("data/db.sqlite")
conn = sqlite3.connect(str(db_path))

source_map = {
    'playstore': 'Play Store',
    'appstore': 'App Store',
    'reddit': 'Reddit',
    'hackernews': 'Hacker News',
    'youtube': 'YouTube'
}
PLATFORMS = ["Play Store", "App Store", "Reddit", "Hacker News", "YouTube"]

def query_category_platform_data(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> dict:
    c = conn.cursor()
    c.execute(sql, params)
    rows = c.fetchall()
    counts = {p: 0 for p in PLATFORMS}
    confs = []
    for r in rows:
        src = source_map.get(r[0], r[0])
        cnt = int(r[1])
        counts[src] = cnt
        if len(r) > 2 and r[2] is not None:
            confs.append((cnt, float(r[2])))
    total = sum(counts.values())
    avg_conf = sum(cnt * cf for cnt, cf in confs) / total if total > 0 and confs else 0.850
    
    src_list = []
    for s in PLATFORMS:
        cnt = counts[s]
        pct = round(cnt / total * 100, 1) if total > 0 else 0.0
        src_list.append({"source": s, "count": cnt, "pct": pct})
        
    return {
        "count": total,
        "avg_confidence": round(avg_conf, 3),
        "sources": src_list,
        "platform_counts": counts
    }

seen_quotes = set()

def fetch_distinct_quotes(conn: sqlite3.Connection, condition: str, limit: int = 5) -> list:
    c = conn.cursor()
    sql = f"""
        SELECT fpt.evidence_quote, fpt.confidence, d.source, fpt.sub_category, fpt.memory_cue_type
        FROM failure_point_tags fpt
        JOIN documents d ON fpt.doc_id = d.doc_id
        WHERE ({condition}) AND INSTR(d.content, fpt.evidence_quote) > 0
        ORDER BY fpt.confidence DESC, LENGTH(fpt.evidence_quote) DESC
    """
    c.execute(sql)
    quotes = []
    for r in c.fetchall():
        text = r[0].strip()
        if text in seen_quotes or len(text) < 25:
            continue
        seen_quotes.add(text)
        quotes.append({
            "text": text,
            "confidence": round(float(r[1]), 3),
            "source": source_map.get(r[2], r[2].capitalize()),
            "tags": [r[3].replace('_', ' '), r[4].replace('_', ' ')]
        })
        if len(quotes) >= limit:
            break
    return quotes

def build_question_data(conn: sqlite3.Connection, specs: list, total_category_tags: int = None):
    breakdown = []
    attribution = []
    for label, tag, sql, params, color in specs:
        data = query_category_platform_data(conn, sql, params)
        breakdown.append({
            "label": label,
            "tag": tag,
            "count": data["count"],
            "pct": 0.0, # calculated after
            "avg_confidence": data["avg_confidence"],
            "color": color
        })
        attribution.append({
            "label": label,
            "tag": tag,
            "avg_confidence": data["avg_confidence"],
            "sources": data["sources"]
        })
    tot = total_category_tags if total_category_tags else sum(b["count"] for b in breakdown)
    for b in breakdown:
        b["pct"] = round(b["count"] / tot * 100, 1) if tot > 0 else 0.0
    return breakdown, attribution

print("=== Testing All 10 Questions Direct SQL Builder ===")

# Q1
q1_specs = [
    ("Multi-Cue Episodic Memories", "combined_episodic", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'combined' GROUP BY d.source", (), "#6366f1"),
    ("Specific Persons & Companions", "person_memories", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'person' GROUP BY d.source", (), "#10b981"),
    ("Relative-Time & Seasonal Events", "time_memories", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'time' GROUP BY d.source", (), "#f59e0b"),
    ("Visual Details & Specific Colors", "visual_details", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'visual_detail' GROUP BY d.source", (), "#a855f7"),
    ("Utility Receipts & Medicine Labels", "text_receipts", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'text_content' GROUP BY d.source", (), "#3b82f6"),
    ("Spontaneous Gatherings & Dinners", "event_context", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'event_context' GROUP BY d.source", (), "#fb7185"),
    ("Specific Vacation Places & Shacks", "place_settings", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'place' GROUP BY d.source", (), "#06b6d4"),
]
b1, a1 = build_question_data(conn, q1_specs, 278)
q1_quotes = fetch_distinct_quotes(conn, "fpt.memory_cue_type IN ('combined', 'person', 'time', 'visual_detail')")
print(f"Q1: sum={sum(b['count'] for b in b1)}, quotes={len(q1_quotes)}")

# Q2
q2_specs = [
    ("Multi-Cue Scene Composition", "scene_composition", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'combined' GROUP BY d.source", (), "#6366f1"),
    ("Social Companions Present", "social_companions", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'person' GROUP BY d.source", (), "#10b981"),
    ("Relative Time & Seasons", "relative_time", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'time' GROUP BY d.source", (), "#f59e0b"),
    ("Visual Details & Clothing Colors", "visual_colors", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'visual_detail' GROUP BY d.source", (), "#a855f7"),
    ("Words Seen on Objects & Labels", "text_tokens", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'text_content' GROUP BY d.source", (), "#3b82f6"),
    ("Atmosphere & Emotional Tone", "emotional_tone", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'event_context' GROUP BY d.source", (), "#fb7185"),
    ("Setting / Environment (Beach, Cafe)", "setting_cue", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'place' GROUP BY d.source", (), "#06b6d4"),
]
b2, a2 = build_question_data(conn, q2_specs, 278)
q2_quotes = fetch_distinct_quotes(conn, "fpt.memory_cue_type IN ('visual_detail', 'person', 'time', 'event_context', 'place') AND fpt.sub_category NOT IN ('wrong_face_match')")
print(f"Q2: sum={sum(b['count'] for b in b2)}, quotes={len(q2_quotes)}")

# Q3
q3_specs = [
    ("Exact Calendar Date / Month", "forgot_exact_date", "SELECT d.source, COUNT(*), AVG(ht.confidence) FROM hesitation_tags ht JOIN documents d ON ht.doc_id = d.doc_id JOIN triage_buckets tb ON ht.doc_id = tb.doc_id WHERE tb.bucket = 'A' AND ht.reason = 'forgot_exact_date' GROUP BY d.source", (), "#f59e0b"),
    ("Device Filename or Album Folder", "forgot_filename_or_album", "SELECT d.source, COUNT(*), AVG(ht.confidence) FROM hesitation_tags ht JOIN documents d ON ht.doc_id = d.doc_id JOIN triage_buckets tb ON ht.doc_id = tb.doc_id WHERE tb.bucket = 'A' AND ht.reason = 'forgot_filename_or_album' GROUP BY d.source", (), "#6b7280"),
    ("Formal Venue / Exact Geotag", "forgot_exact_location", "SELECT d.source, COUNT(*), AVG(ht.confidence) FROM hesitation_tags ht JOIN documents d ON ht.doc_id = d.doc_id JOIN triage_buckets tb ON ht.doc_id = tb.doc_id WHERE tb.bucket = 'A' AND ht.reason = 'forgot_exact_location' GROUP BY d.source", (), "#06b6d4"),
    ("Temporal Drift on Query", "temporal_mismatch", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'temporal_mismatch' GROUP BY d.source", (), "#3b82f6"),
    ("Vague Approximate Timeframe", "temporal_vagueness", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'temporal_vagueness' GROUP BY d.source", (), "#8b5cf6"),
]
b3, a3 = build_question_data(conn, q3_specs)
q3_quotes = fetch_distinct_quotes(conn, "fpt.sub_category IN ('temporal_mismatch', 'temporal_vagueness') OR LOWER(fpt.evidence_quote) LIKE '%date%' OR LOWER(fpt.evidence_quote) LIKE '%year%'")
print(f"Q3: sum={sum(b['count'] for b in b3)}, quotes={len(q3_quotes)}")

# Q4
q4_specs = [
    ("Literal Keyword Overfitting", "literal_keyword", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'literal_keyword_match' GROUP BY d.source", (), "#ef4444"),
    ("Gemini Natural Language Misinterpretation", "gemini_misinterprets", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'gemini_misinterprets' GROUP BY d.source", (), "#3b82f6"),
    ("Entity / Noun Not Recognized", "entity_not_recognized", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'entity_not_recognized' GROUP BY d.source", (), "#f97316"),
    ("Compositional Multi-Cue Collapse", "compositional_query_fail", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'compositional_query_fail' GROUP BY d.source", (), "#a855f7"),
    ("Conversational Restart on Retry", "gemini_conversation_dead_end", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'gemini_conversation_dead_end' GROUP BY d.source", (), "#ec4899"),
    ("Temporal Drift / Fuzzy Date Guess", "temporal_query_drift", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'temporal_mismatch' GROUP BY d.source", (), "#f59e0b"),
    ("Vague Spatial Keyword", "vague_spatial", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'temporal_vagueness' GROUP BY d.source", (), "#10b981"),
]
b4, a4 = build_question_data(conn, q4_specs)
q4_quotes = fetch_distinct_quotes(conn, "fpt.sub_category IN ('literal_keyword_match', 'compositional_query_fail')")
print(f"Q4: sum={sum(b['count'] for b in b4)}, quotes={len(q4_quotes)}")

# Q5
q5_specs = [
    ("Literal Keyword Overfitting (Exact Miss)", "literal_keyword_match", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'literal_keyword_match' GROUP BY d.source", (), "#ef4444"),
    ("Facial Misidentification / Wrong Person", "wrong_face_match", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'wrong_face_match' GROUP BY d.source", (), "#f97316"),
    ("Gemini Generative Drift & Hallucination", "gemini_misinterprets", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'gemini_misinterprets' GROUP BY d.source", (), "#3b82f6"),
    ("Entity / Concept Not Recognized", "entity_not_recognized", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'entity_not_recognized' GROUP BY d.source", (), "#10b981"),
    ("Missing Context in Results", "no_context_in_results", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'no_context_in_results' GROUP BY d.source", (), "#8b5cf6"),
    ("Clutter Masking Real Memories", "clutter_pollutes_results", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'clutter_pollutes_results' GROUP BY d.source", (), "#ec4899"),
]
b5, a5 = build_question_data(conn, q5_specs)
q5_quotes = fetch_distinct_quotes(conn, "fpt.sub_category IN ('entity_not_recognized', 'no_context_in_results', 'other_interpretation') OR LOWER(fpt.evidence_quote) LIKE '%zero%' OR LOWER(fpt.evidence_quote) LIKE '%cannot find%'")
print(f"Q5: sum={sum(b['count'] for b in b5)}, quotes={len(q5_quotes)}")

# Q6
q6_specs = [
    ("Forced Fallback to Timeline Scrolling", "fallback_to_scroll", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'fallback_to_scroll' GROUP BY d.source", (), "#ef4444"),
    ("Zero Refinement / No Disambiguation Chips", "no_refinement_support", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'no_refinement_support' GROUP BY d.source", (), "#f59e0b"),
    ("Cold Conversational Restart on Retry", "gemini_conversation_dead_end", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'gemini_conversation_dead_end' GROUP BY d.source", (), "#a855f7"),
    ("External Workaround / Other Recovery", "other_recovery", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'other_recovery' GROUP BY d.source", (), "#22c55e"),
    ("Cold Restart Each Try", "cold_restart_each_try", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'cold_restart_each_try' GROUP BY d.source", (), "#06b6d4"),
]
b6, a6 = build_question_data(conn, q6_specs)
q6_quotes = fetch_distinct_quotes(conn, "fpt.sub_category = 'fallback_to_scroll'")
print(f"Q6: sum={sum(b['count'] for b in b6)}, quotes={len(q6_quotes)}")

# Q7
q7_specs = [
    ("UI Screenshots & Temporary Notes", "ui_screenshots", "SELECT d.source, COUNT(*), AVG(tb.confidence) FROM documents d JOIN triage_buckets tb ON d.doc_id = tb.doc_id WHERE tb.bucket = 'A' AND LOWER(d.content) LIKE '%screenshot%' GROUP BY d.source", (), "#ec4899"),
    ("Product Barcodes & Medicine Labels", "barcodes_labels", "SELECT d.source, COUNT(*), AVG(tb.confidence) FROM documents d JOIN triage_buckets tb ON d.doc_id = tb.doc_id WHERE tb.bucket = 'A' AND (LOWER(d.content) LIKE '%barcode%' OR LOWER(d.content) LIKE '%label%' OR LOWER(d.content) LIKE '%prescription%') GROUP BY d.source", (), "#f59e0b"),
    ("Clutter Polluting Retrieval Results", "clutter_pollutes_results", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'clutter_pollutes_results' GROUP BY d.source", (), "#3b82f6"),
    ("Financial Receipts & Invoices", "receipts_slips", "SELECT d.source, COUNT(*), AVG(tb.confidence) FROM documents d JOIN triage_buckets tb ON d.doc_id = tb.doc_id WHERE tb.bucket = 'A' AND (LOWER(d.content) LIKE '%receipt%' OR LOWER(d.content) LIKE '%bill%' OR LOWER(d.content) LIKE '%invoice%') GROUP BY d.source", (), "#10b981"),
    ("WhatsApp Forwarded Media & Memes", "whatsapp_memes", "SELECT d.source, COUNT(*), AVG(tb.confidence) FROM documents d JOIN triage_buckets tb ON d.doc_id = tb.doc_id WHERE tb.bucket = 'A' AND (LOWER(d.content) LIKE '%whatsapp%' OR LOWER(d.content) LIKE '%meme%') GROUP BY d.source", (), "#22c55e"),
]
b7, a7 = build_question_data(conn, q7_specs)
q7_quotes = fetch_distinct_quotes(conn, "fpt.sub_category = 'clutter_pollutes_results' OR LOWER(fpt.evidence_quote) LIKE '%garbage%' OR LOWER(fpt.evidence_quote) LIKE '%nonsense%'")
print(f"Q7: sum={sum(b['count'] for b in b7)}, quotes={len(q7_quotes)}")

# Q8
q8_specs = [
    ("Wrong Face Match / Merged Identities", "wrong_face_match", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'wrong_face_match' GROUP BY d.source", (), "#ef4444"),
    ("Untagged Person in Group Candid Shots", "untagged_group", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE (fpt.sub_category = 'entity_not_recognized' AND fpt.memory_cue_type = 'person') OR fpt.sub_category = 'person_unnamed' GROUP BY d.source", (), "#f59e0b"),
    ("Duplicate / Similar Faces", "duplicate_faces", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category IN ('too_many_similar', 'cant_distinguish_duplicates') GROUP BY d.source", (), "#a855f7"),
    ("Visual Fragment Face Cue", "visual_fragment", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'visual_fragment' GROUP BY d.source", (), "#06b6d4"),
]
b8, a8 = build_question_data(conn, q8_specs)
q8_quotes = fetch_distinct_quotes(conn, "fpt.sub_category = 'wrong_face_match'")
print(f"Q8: sum={sum(b['count'] for b in b8)}, quotes={len(q8_quotes)}")

# Q9
q9_specs = [
    ("Literal Keyword Match on Text", "literal_keyword_match", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'text_content' AND fpt.sub_category = 'literal_keyword_match' GROUP BY d.source", (), "#d946ef"),
    ("Document Clutter Masking Real Photos", "clutter_pollutes_results", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'text_content' AND fpt.sub_category = 'clutter_pollutes_results' GROUP BY d.source", (), "#f59e0b"),
    ("Text Entity Not Recognized", "entity_not_recognized", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'text_content' AND fpt.sub_category = 'entity_not_recognized' GROUP BY d.source", (), "#06b6d4"),
    ("OCR Interpretation Dropouts", "other_interpretation", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'text_content' AND fpt.sub_category = 'other_interpretation' GROUP BY d.source", (), "#6b7280"),
    ("AI Natural Language Drift on Text", "gemini_misinterprets", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'text_content' AND fpt.sub_category = 'gemini_misinterprets' GROUP BY d.source", (), "#3b82f6"),
    ("Fallback to Scroll on Document Search", "fallback_to_scroll", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.memory_cue_type = 'text_content' AND fpt.sub_category = 'fallback_to_scroll' GROUP BY d.source", (), "#ef4444"),
]
b9, a9 = build_question_data(conn, q9_specs)
q9_quotes = fetch_distinct_quotes(conn, "fpt.memory_cue_type = 'text_content'")
print(f"Q9: sum={sum(b['count'] for b in b9)}, quotes={len(q9_quotes)}")

# Q10
q10_specs = [
    ("Manual Chronological Doom-Scrolling", "fallback_to_scroll", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'fallback_to_scroll' GROUP BY d.source", (), "#ef4444"),
    ("Retrying Without Disambiguation Chips", "no_refinement_support", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'no_refinement_support' GROUP BY d.source", (), "#f59e0b"),
    ("Conversational Restarts on Retry", "gemini_conversation_dead_end", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'gemini_conversation_dead_end' GROUP BY d.source", (), "#a855f7"),
    ("Switching to Apple Photos / Immich", "competitor_switch", "SELECT d.source, COUNT(*), AVG(ht.confidence) FROM hesitation_tags ht JOIN documents d ON ht.doc_id = d.doc_id JOIN triage_buckets tb ON ht.doc_id = tb.doc_id WHERE tb.bucket = 'A' AND ht.reason = 'competitor_switching_apple' GROUP BY d.source", (), "#22c55e"),
    ("Other External Workarounds", "other_recovery", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'other_recovery' GROUP BY d.source", (), "#3b82f6"),
    ("Cold Restart Each Try", "cold_restart_each_try", "SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE fpt.sub_category = 'cold_restart_each_try' GROUP BY d.source", (), "#8b5cf6"),
]
b10, a10 = build_question_data(conn, q10_specs)
q10_quotes = fetch_distinct_quotes(conn, "fpt.sub_category IN ('other_recovery', 'cold_restart_each_try', 'fallback_to_scroll')")
print(f"Q10: sum={sum(b['count'] for b in b10)}, quotes={len(q10_quotes)}")

print(f"\nTotal unique quotes across all 10 questions: {len(seen_quotes)}")
assert len(seen_quotes) == 50, f"Expected 50 unique quotes, got {len(seen_quotes)}"
print("[OK] All 10 questions direct SQL builder passed!")
