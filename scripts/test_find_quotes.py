import sqlite3
import html
import re
import json

conn = sqlite3.connect('data/db.sqlite')
c = conn.cursor()

def clean_text(t):
    t = html.unescape(t)
    t = re.sub(r'http\S+', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

SOURCE_MAP = {
    'playstore': 'Google Play Store',
    'appstore': 'Apple App Store',
    'reddit': 'Reddit',
    'hackernews': 'Hacker News',
    'youtube': 'YouTube'
}

def search_quotes(must_have, should_have=None, exclude=None, min_len=90, max_len=900, limit=5):
    sql = """
        SELECT d.doc_id, d.source, d.source_id, d.content, d.timestamp, d.rating,
               COALESCE((SELECT reason FROM hesitation_tags WHERE doc_id = d.doc_id LIMIT 1), 'search_friction'),
               COALESCE((SELECT confidence FROM hesitation_tags WHERE doc_id = d.doc_id LIMIT 1), 0.85)
        FROM documents d
        WHERE LENGTH(d.content) >= ? AND LENGTH(d.content) <= ?
    """
    params = [min_len, max_len]
    
    for term in must_have:
        sql += " AND LOWER(d.content) LIKE ?"
        params.append(f"%{term.lower()}%")
        
    if should_have:
        or_clauses = ["LOWER(d.content) LIKE ?" for _ in should_have]
        sql += f" AND ({' OR '.join(or_clauses)})"
        for term in should_have:
            params.append(f"%{term.lower()}%")
            
    if exclude:
        for term in exclude:
            sql += " AND LOWER(d.content) NOT LIKE ?"
            params.append(f"%{term.lower()}%")
            
    sql += " ORDER BY (CASE WHEN LOWER(d.content) LIKE '%search%' AND LOWER(d.content) LIKE '%photo%' THEN 0 ELSE 1 END), LENGTH(d.content) ASC LIMIT 25"
    
    rows = c.execute(sql, params).fetchall()
    results = []
    seen = set()
    for r in rows:
        cl = clean_text(r[3])
        # Avoid duplicate prefixes
        prefix = cl[:60].lower()
        if prefix in seen or len(cl) < min_len:
            continue
        seen.add(prefix)
        results.append({
            "text": cl,
            "source": SOURCE_MAP.get(r[1], r[1]),
            "source_id": r[2],
            "date": str(r[4] or '')[:10],
            "confidence": round(float(r[7] or 0.85), 2),
            "tags": [r[6]],
            "rating": r[5]
        })
        if len(results) >= limit:
            break
    return results

questions_config = {
    1: { # Struggled Photo Types: Old candid shots, receipts, documents, family events
        "title": "Struggled Photo Types",
        "must": ["photo"],
        "should": ["candid", "receipt", "document", "old photo", "vacation", "trip", "family", "moment"],
        "exclude": ["casino", "crypto", "slot", "bitcoin", "banking apps", "iphone vs android", "migrated my entire google identity"]
    },
    2: { # Retained Memory Clues: Colors, clothing, companions, settings, visual elements
        "title": "Retained Memory Clues",
        "must": ["photo", "remember"],
        "should": ["color", "wearing", "red", "blue", "shirt", "friend", "dog", "beach", "lake", "night"],
        "exclude": ["casino", "crypto", "banking apps"]
    },
    3: { # Forgotten Metadata: Dates, years, timestamps, filenames, exact locations
        "title": "Forgotten Metadata",
        "must": ["photo"],
        "should": ["date", "exact date", "year", "month", "filename", "folder", "don't remember when", "forgot when"],
        "exclude": ["casino", "crypto", "banking apps"]
    },
    4: { # Incomplete Query Formulation: Keyword guessing, Ask Photos prompt issues, Gemini search
        "title": "Incomplete Query Formulation",
        "must": ["search"],
        "should": ["keyword", "query", "typed", "gemini", "ask photos", "phrase", "describe"],
        "exclude": ["casino", "crypto", "banking apps"]
    },
    5: { # Irrelevant Results & False Misses: Zero results for existing photos, wrong photos
        "title": "Irrelevant Results & False Misses",
        "must": ["search", "photo"],
        "should": ["no results", "zero results", "can't find", "cannot find", "irrelevant", "wrong photos", "not found", "doesn't find"],
        "exclude": ["casino", "crypto"]
    },
    6: { # Endless Timeline Scrolling: Scroll fatigue, scrolling through thousands of photos
        "title": "Endless Timeline Scrolling",
        "must": ["scroll"],
        "should": ["timeline", "years", "thousands", "swipe", "hours", "minutes", "endless", "grid"],
        "exclude": ["casino", "crypto"]
    },
    7: { # Screenshot & Junk Clutter: Screenshots, receipts, memes, junk polluting personal photos
        "title": "Screenshot & Junk Clutter",
        "must": ["photo"],
        "should": ["screenshot", "screenshots", "clutter", "meme", "memes", "whatsapp", "junk", "receipts"],
        "exclude": ["casino", "crypto"]
    },
    8: { # Face Recognition Failures: People & pets, wrong faces, untagged people
        "title": "Face Recognition Failures",
        "must": ["face"],
        "should": ["people", "pet", "pets", "dog", "cat", "tagged", "tagging", "grouping", "recognize", "wrong person"],
        "exclude": ["casino", "crypto"]
    },
    9: { # Text & Document Search Failures: OCR, receipts, prescriptions, signs, handwritten text
        "title": "Text & Document Search Failures",
        "must": ["photo"],
        "should": ["text", "ocr", "receipt", "document", "prescription", "license", "words", "signs"],
        "exclude": ["casino", "crypto"]
    },
    10: { # Workarounds & Switching: WhatsApp search, Apple Photos, Immich, asking friends, leaving Google Photos
        "title": "Workarounds & Switching",
        "must": ["photos"],
        "should": ["whatsapp", "apple photos", "immich", "onedrive", "switch", "leaving", "alternative", "ask my friend"],
        "exclude": ["casino", "crypto"]
    }
}

for qid, cfg in questions_config.items():
    quotes = search_quotes(cfg["must"], cfg.get("should"), cfg.get("exclude"), limit=4)
    print(f"\n=================== Q{qid}: {cfg['title']} ({len(quotes)} quotes) ===================")
    for i, q in enumerate(quotes):
        print(f"[{i+1}] ({q['source']} | {q['source_id']} | len={len(q['text'])} | date={q['date']}):")
        print(f"\"{q['text']}\"\n")
