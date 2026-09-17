import sqlite3
import json

conn = sqlite3.connect('data/db.sqlite')
c = conn.cursor()

def get_matching_docs(must_contain, should_contain=None, exclude=None, min_len=60, max_len=1200):
    sql = "SELECT doc_id, source, source_id, content, timestamp, rating FROM documents WHERE "
    clauses = []
    
    # must contain at least one of these terms
    or_terms = [f"LOWER(content) LIKE '%{t.lower()}%'" for t in must_contain]
    clauses.append(f"({' OR '.join(or_terms)})")
    
    if should_contain:
        should_clauses = [f"LOWER(content) LIKE '%{t.lower()}%'" for t in should_contain]
        clauses.append(f"({' OR '.join(should_clauses)})")
        
    if exclude:
        for ex in exclude:
            clauses.append(f"LOWER(content) NOT LIKE '%{ex.lower()}%'")
            
    clauses.append(f"LENGTH(content) >= {min_len} AND LENGTH(content) <= {max_len}")
    
    full_sql = sql + " AND ".join(clauses)
    return c.execute(full_sql).fetchall()

queries = {
    1: {"must": ["candid", "receipt", "document", "old photo", "unposed", "vacation", "trip", "find"], "should": ["photo", "picture", "search"]},
    2: {"must": ["remember", "color", "wear", "clothes", "friend", "companion", "wife", "husband", "kid", "dog"], "should": ["photo", "search", "find"]},
    3: {"must": ["date", "year", "filename", "album", "month", "time", "where", "location"], "should": ["forgot", "lost", "remember", "search", "photo", "find"]},
    4: {"must": ["query", "keyword", "search", "trying to find", "type", "describe"], "should": ["photo", "app", "result"]},
    5: {"must": ["no result", "0 result", "zero result", "irrelevant", "wrong photo", "not found", "doesn't find", "cant find", "cannot find", "missing"], "should": ["search", "photo"]},
    6: {"must": ["scroll", "scrolling", "timeline", "swipe", "minutes", "hours", "endless"], "should": ["photo", "find", "search", "grid"]},
    7: {"must": ["screenshot", "meme", "clutter", "whatsapp", "junk", "receipt", "download"], "should": ["photo", "search", "clean", "separate"]},
    8: {"must": ["face", "people", "pet", "dog", "cat", "tag", "recognize", "person", "grouping"], "should": ["photo", "search", "wrong"]},
    9: {"must": ["text", "receipt", "prescription", "document", "ocr", "words", "label", "read"], "should": ["photo", "search", "find"]},
    10: {"must": ["whatsapp", "apple", "iphone", "immich", "onedrive", "switch", "transfer", "alternative", "ask", "friend"], "should": ["photo", "search", "backup", "leave"]},
}

for qid, q in queries.items():
    docs = get_matching_docs(q["must"], q.get("should"), exclude=["casino", "slot", "crypto", "banking app"], min_len=70)
    print(f"\n==================== QUESTION {qid}: Found {len(docs)} matching docs ====================")
    for d in docs[:3]:
        print(f"[{d[1]} | {d[2]}] (len={len(d[3])})")
        print(f"{d[3]}\n")
