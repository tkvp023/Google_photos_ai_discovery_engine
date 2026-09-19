import sqlite3

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

def get_gap_quotes():
    categories = [
        ("clutter_pollutes_results", "Screenshot & Clutter Overflow", "fpt.sub_category = 'clutter_pollutes_results'"),
        ("zero_results_for_existing_photo", "Zero Recall on Existing Photos", "fpt.sub_category = 'entity_not_recognized' AND LOWER(d.content) LIKE '%search%'"),
        ("wrong_face_match", "Facial Clustering Errors", "fpt.sub_category = 'wrong_face_match'"),
        ("text_ocr_detection_failure", "OCR & Document Indexing Gap", "fpt.memory_cue_type = 'text_content'"),
        ("endless_scrolling_fatigue", "Endless Timeline Scrolling", "fpt.sub_category = 'fallback_to_scroll'"),
        ("competitor_switching_apple", "Ecosystem Switching", "fpt.sub_category IN ('other_recovery', 'cold_restart_each_try') OR LOWER(d.content) LIKE '%apple%' OR LOWER(d.content) LIKE '%immich%'"),
    ]
    source_map = {
        'playstore': 'Play Store',
        'appstore': 'App Store',
        'reddit': 'Reddit',
        'hackernews': 'Hacker News',
        'youtube': 'YouTube'
    }
    quotes = []
    seen = set()
    for tag, label, cond in categories:
        sql = f"""
            SELECT fpt.evidence_quote, fpt.confidence, d.source, d.source_id, d.timestamp, fpt.sub_category
            FROM failure_point_tags fpt
            JOIN documents d ON fpt.doc_id = d.doc_id
            WHERE ({cond}) AND INSTR(d.content, fpt.evidence_quote) > 0
            ORDER BY fpt.confidence DESC, LENGTH(fpt.evidence_quote) DESC
        """
        c.execute(sql)
        for r in c.fetchall():
            text = r[0].strip()
            if text not in seen and len(text) > 25:
                seen.add(text)
                quotes.append({
                    "text": text[:300] + ("..." if len(text) > 300 else ""),
                    "source": source_map.get(r[2], r[2].capitalize()),
                    "source_id": str(r[3] or ""),
                    "date": str(r[4] or "")[:10],
                    "confidence": round(float(r[1]), 3),
                    "tags": [tag],
                    "segment": "unknown"
                })
                break
    return quotes

quotes = get_gap_quotes()
print(f"Got {len(quotes)} quotes:")
for q in quotes:
    print(f"[{q['source']}] (conf: {q['confidence']}) {q['tags']}: {q['text']}")
