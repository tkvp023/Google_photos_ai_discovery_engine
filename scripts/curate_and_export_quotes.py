import sqlite3
import re
import html

conn = sqlite3.connect('data/db.sqlite')
c = conn.cursor()

def clean_text(t):
    t = html.unescape(t)
    t = re.sub(r'http\S+', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def find_best_quotes(include_kws, require_any=None, exclude_kws=None, min_len=80, max_len=1200, limit=6):
    sql = "SELECT doc_id, source, source_id, content, timestamp, rating FROM documents WHERE "
    clauses = ["LENGTH(content) >= ? AND LENGTH(content) <= ?"]
    params = [min_len, max_len]
    
    # Must have at least one from include_kws
    inc_clauses = ["LOWER(content) LIKE ?" for _ in include_kws]
    clauses.append(f"({' OR '.join(inc_clauses)})")
    for k in include_kws:
        params.append(f"%{k.lower()}%")
        
    if require_any:
        req_clauses = ["LOWER(content) LIKE ?" for _ in require_any]
        clauses.append(f"({' OR '.join(req_clauses)})")
        for k in require_any:
            params.append(f"%{k.lower()}%")
            
    if exclude_kws:
        for ex in exclude_kws:
            clauses.append("LOWER(content) NOT LIKE ?")
            params.append(f"%{ex.lower()}%")
            
    sql += " AND ".join(clauses)
    sql += " ORDER BY (CASE WHEN LOWER(content) LIKE '%search%' THEN 0 ELSE 1 END), LENGTH(content) DESC"
    
    rows = c.execute(sql, params).fetchall()
    results = []
    seen = set()
    for r in rows:
        cleaned = clean_text(r[3])
        if len(cleaned) < min_len or cleaned in seen:
            continue
        seen.add(cleaned)
        results.append({
            "doc_id": r[0],
            "source": r[1],
            "source_id": r[2],
            "text": cleaned,
            "timestamp": r[4],
            "rating": r[5]
        })
        if len(results) >= limit:
            break
    return results

# Let's define the exact target concepts for each of the 10 questions:
criteria = {
    1: { # Struggled Photo Types: Candid moments, utility receipts, documents, unposed family events
        "include": ["candid", "receipt", "document", "prescription", "utility", "old photo", "old version photo", "vacation", "trip", "family photo", "dinner", "event"],
        "require": ["search", "find", "retrieve", "photos", "looking for", "missing"],
        "exclude": ["casino", "crypto", "slot", "bitcoin", "bank account", "identity to another country"]
    },
    2: { # Retained Memory Clues: Colors, clothing, companions, feelings, settings, visual anchors
        "include": ["color", "wearing", "clothes", "wardrobe", "companion", "friend", "wife", "husband", "son", "daughter", "kid", "beach", "restaurant", "remembered"],
        "require": ["photo", "photos", "picture", "pictures", "search"],
        "exclude": ["casino", "crypto", "slot"]
    },
    3: { # Forgotten Metadata: Lost dates, unknown years, missing filenames (IMG_...), folder paths, date amnesia
        "include": ["date", "exact date", "year", "month", "filename", "folder", "album", "where it was", "location", "timeline"],
        "require": ["forgot", "don't know", "cannot remember", "cant remember", "lost", "missing", "search", "photos"],
        "exclude": ["casino", "crypto", "slot"]
    },
    4: { # Incomplete Query Formulation: Keyword guessing, literal queries, single nouns, trying to describe
        "include": ["keyword", "query", "searching for", "searched", "typed", "typing", "describe", "prompt", "gemini", "reformulat"],
        "require": ["photos", "search", "results", "find"],
        "exclude": ["casino", "crypto", "slot"]
    },
    5: { # Irrelevant Results & False Misses: Zero results for existing photos, false misses, wrong photos returned
        "include": ["zero results", "no results", "no result", "0 results", "not found", "doesn't find", "cant find", "cannot find", "irrelevant", "wrong photo", "disappeared", "missing"],
        "require": ["search", "photo", "photos", "library"],
        "exclude": ["casino", "crypto", "slot"]
    },
    6: { # Endless Timeline Scrolling: Scroll fatigue, scrolling through thousands of photos, minutes/hours scrolling, infinite grid
        "include": ["scroll", "scrolling", "timeline", "endless", "infinite", "swipe", "swiping", "hours", "minutes scrolling", "grid"],
        "require": ["photo", "photos", "find", "search", "look"],
        "exclude": ["casino", "crypto", "slot"]
    },
    7: { # Screenshot & Junk Clutter: WhatsApp memes, receipts, screenshots, junk polluting memories
        "include": ["screenshot", "screenshots", "meme", "memes", "whatsapp", "clutter", "junk", "receipts", "downloads", "pollut"],
        "require": ["photo", "photos", "gallery", "search", "library"],
        "exclude": ["casino", "crypto", "slot"]
    },
    8: { # Face Recognition Failures: People & pets, wrong face, missing face, baby/toddler tag, untagged
        "include": ["face", "faces", "facial", "people", "pets", "pet", "dog", "cat", "tagged", "tagging", "grouping", "recognize", "misidentif"],
        "require": ["photo", "photos", "search"],
        "exclude": ["casino", "crypto", "slot"]
    },
    9: { # Text & Document Search Failures: OCR, receipts, prescriptions, labels, handwritten text, signs
        "include": ["text", "ocr", "receipt", "receipts", "prescription", "bottle", "document", "documents", "bill", "bills", "label", "words"],
        "require": ["search", "photo", "photos", "find"],
        "exclude": ["casino", "crypto", "slot"]
    },
    10: { # Workarounds & Switching: WhatsApp media search, Apple Photos, Immich, asking friends, switching away
        "include": ["whatsapp", "apple photos", "icloud", "immich", "onedrive", "dropbox", "switch", "leaving", "alternative", "ask my friend", "friends to send"],
        "require": ["photo", "photos", "google photos"],
        "exclude": ["casino", "crypto", "slot"]
    },
}

for qid, c_spec in criteria.items():
    qs = find_best_quotes(c_spec["include"], c_spec.get("require"), c_spec.get("exclude"), limit=4)
    print(f"\n=================== Q{qid} Grounded Quotes ({len(qs)} found) ===================")
    for i, q in enumerate(qs):
        print(f"[{i+1}] ({q['source']} | {q['source_id']} | len={len(q['text'])}):")
        print(f'"{q["text"]}"\n')
