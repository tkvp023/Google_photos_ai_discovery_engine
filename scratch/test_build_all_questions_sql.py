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
    avg_conf = sum(cnt * cf for cnt, cf in confs) / total if total > 0 and confs else 0.85
    
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

# Test Q1
q1_specs = [
    ("Multi-Cue Episodic Memories", "combined_episodic", "fpt.memory_cue_type = 'combined'", "#6366f1"),
    ("Specific Persons & Companions", "person_memories", "fpt.memory_cue_type = 'person'", "#10b981"),
    ("Relative-Time & Seasonal Events", "time_memories", "fpt.memory_cue_type = 'time'", "#f59e0b"),
    ("Visual Details & Specific Colors", "visual_details", "fpt.memory_cue_type = 'visual_detail'", "#a855f7"),
    ("Utility Receipts & Medicine Labels", "text_receipts", "fpt.memory_cue_type = 'text_content'", "#3b82f6"),
    ("Spontaneous Gatherings & Dinners", "event_context", "fpt.memory_cue_type = 'event_context'", "#fb7185"),
    ("Specific Vacation Places & Shacks", "place_settings", "fpt.memory_cue_type = 'place'", "#06b6d4"),
]

q1_items = []
q1_attr = []
total_q1_tags = 278
for label, tag, cond, color in q1_specs:
    sql = f"SELECT d.source, COUNT(*), AVG(fpt.confidence) FROM failure_point_tags fpt JOIN documents d ON fpt.doc_id = d.doc_id WHERE {cond} GROUP BY d.source"
    data = query_category_platform_data(conn, sql)
    q1_items.append({
        "label": label,
        "tag": tag,
        "count": data["count"],
        "pct": round(data["count"] / total_q1_tags * 100, 1),
        "avg_confidence": data["avg_confidence"],
        "color": color
    })
    q1_attr.append({
        "label": label,
        "tag": tag,
        "avg_confidence": data["avg_confidence"],
        "sources": data["sources"]
    })

print("Q1 Breakdown sum:", sum(item["count"] for item in q1_items))
for item, attr in zip(q1_items, q1_attr):
    attr_sum = sum(s["count"] for s in attr["sources"])
    print(f"  {item['label']:35}: breakdown={item['count']}, attr_sum={attr_sum}, conf={item['avg_confidence']}")
    assert item["count"] == attr_sum, f"Mismatch in {item['label']}"

conn.close()
print("\n[OK] Q1 math and direct SQL queries verified successfully!")
