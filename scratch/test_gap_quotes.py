import sqlite3

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

def get_gap_quote(condition):
    c.execute(f"""
        SELECT d.content, fpt.evidence_quote, fpt.confidence, d.source, d.source_id, d.timestamp, fpt.sub_category
        FROM failure_point_tags fpt
        JOIN documents d ON fpt.doc_id = d.doc_id
        WHERE ({condition}) AND INSTR(d.content, fpt.evidence_quote) > 0
        ORDER BY fpt.confidence DESC
        LIMIT 1
    """)
    r = c.fetchone()
    if r:
        source_map = {'playstore': 'Play Store', 'appstore': 'App Store', 'reddit': 'Reddit', 'hackernews': 'Hacker News', 'youtube': 'YouTube'}
        return {
            "text": r[1],
            "source": source_map.get(r[3], r[3].capitalize()),
            "source_id": r[4],
            "date": str(r[5] or "")[:10],
            "confidence": round(float(r[2]), 3),
            "tags": [r[6].replace('_', ' ')],
            "segment": "unknown"
        }
    return None

gap_quotes = [
    get_gap_quote("fpt.sub_category = 'clutter_pollutes_results'"),
    get_gap_quote("fpt.sub_category = 'entity_not_recognized'"),
    get_gap_quote("fpt.sub_category = 'wrong_face_match'"),
    get_gap_quote("fpt.memory_cue_type = 'text_content'"),
    get_gap_quote("fpt.sub_category = 'fallback_to_scroll'"),
    get_gap_quote("fpt.sub_category IN ('other_recovery', 'cold_restart_each_try') OR LOWER(d.content) LIKE '%apple%' OR LOWER(d.content) LIKE '%immich%'"),
]

for i, gq in enumerate(gap_quotes, 1):
    print(f"{i}. [{gq['source']}] (conf: {gq['confidence']}) {gq['tags']}: {gq['text']}")

