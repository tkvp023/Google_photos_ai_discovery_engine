import sqlite3
import html
import re
import json

conn = sqlite3.connect('data/db.sqlite')
c = conn.cursor()

def clean_text(t):
    t = html.unescape(t)
    t = re.sub(r'http\S+', '', t)
    # Remove control characters
    t = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

SOURCE_MAP = {
    'playstore': 'Google Play Store',
    'appstore': 'Apple App Store',
    'reddit': 'Reddit',
    'hackernews': 'Hacker News',
    'youtube': 'YouTube'
}

def get_candidates(sql_query, params=()):
    rows = c.execute(sql_query, params).fetchall()
    results = []
    seen = set()
    for r in rows:
        cleaned = clean_text(r[3])
        prefix = cleaned[:50].lower()
        if prefix in seen or len(cleaned) < 80:
            continue
        seen.add(prefix)
        results.append({
            "doc_id": r[0],
            "source": SOURCE_MAP.get(r[1], r[1]),
            "source_id": r[2],
            "text": cleaned,
            "date": str(r[4] or '')[:10],
            "rating": r[5],
            "tag": r[6] if len(r) > 6 else "photo_discovery"
        })
    return results

# Let's run focused searches for each question:
curated = {}

# Q1: Struggled Photo Types (receipts, bills, licenses, old candid memories, old photos)
curated[1] = get_candidates("""
    SELECT d.doc_id, d.source, d.source_id, d.content, d.timestamp, d.rating, 'struggled_photo_types'
    FROM documents d
    WHERE (
        d.content LIKE '%driving license%' OR
        d.content LIKE '%bills and documents%' OR
        d.content LIKE '%store receipts%' OR
        d.content LIKE '%old photos are missing%' OR
        d.content LIKE '%find old photos%' OR
        d.content LIKE '%vacation with 300 photos%' OR
        d.content LIKE '%document the things I do%'
    )
    AND LOWER(d.content) NOT LIKE '%bitcoin%'
    AND LOWER(d.content) NOT LIKE '%uk banking%'
    ORDER BY LENGTH(d.content) ASC
""")

# Q2: Retained Memory Clues (recalling visual elements, colors, friends, companions, settings)
curated[2] = get_candidates("""
    SELECT d.doc_id, d.source, d.source_id, d.content, d.timestamp, d.rating, 'remembered_visual_clue'
    FROM documents d
    WHERE (d.content LIKE '%photo%' OR d.content LIKE '%photos%')
      AND (
        d.content LIKE '%remember%' OR
        d.content LIKE '%memory%' OR
        d.content LIKE '%memories%'
      )
      AND (
        d.content LIKE '%color%' OR
        d.content LIKE '%wearing%' OR
        d.content LIKE '%friend%' OR
        d.content LIKE '%location%' OR
        d.content LIKE '%sunsets%' OR
        d.content LIKE '%beach%'
      )
      AND LOWER(d.content) NOT LIKE '%bitcoin%'
      AND LOWER(d.content) NOT LIKE '%uk banking%'
    ORDER BY (CASE WHEN d.content LIKE '%search%' THEN 0 ELSE 1 END), LENGTH(d.content) ASC
""")

# Q3: Forgotten Metadata (dates, months, years, timestamps, filenames)
curated[3] = get_candidates("""
    SELECT d.doc_id, d.source, d.source_id, d.content, d.timestamp, d.rating, 'forgot_exact_date'
    FROM documents d
    WHERE (d.content LIKE '%photo%' OR d.content LIKE '%photos%')
      AND (
        d.content LIKE '%date%' OR
        d.content LIKE '%dates%' OR
        d.content LIKE '%year%' OR
        d.content LIKE '%timeline%' OR
        d.content LIKE '%folder%' OR
        d.content LIKE '%organized into different days%'
      )
      AND (
        d.content LIKE '%wrong date%' OR
        d.content LIKE '%cannot find%' OR
        d.content LIKE '%cant find%' OR
        d.content LIKE '%search%' OR
        d.content LIKE '%missing%'
      )
      AND LOWER(d.content) NOT LIKE '%uk banking%'
    ORDER BY LENGTH(d.content) ASC
""")

# Q4: Incomplete Query Formulation (keyword guessing, search prompts, Ask Photos / Gemini query friction)
curated[4] = get_candidates("""
    SELECT d.doc_id, d.source, d.source_id, d.content, d.timestamp, d.rating, 'query_formulation_friction'
    FROM documents d
    WHERE (
        d.content LIKE '%search keywords%' OR
        d.content LIKE '%search term%' OR
        d.content LIKE '%type in search%' OR
        d.content LIKE '%where did the search feature go%' OR
        d.content LIKE '%replacing it with ''ask''%' OR
        d.content LIKE '%search functions now terrible%' OR
        d.content LIKE '%Ask Photos%'
    )
    ORDER BY LENGTH(d.content) ASC
""")

# Q5: Irrelevant Results & False Misses (zero results, no results for existing photos, wrong photos)
curated[5] = get_candidates("""
    SELECT d.doc_id, d.source, d.source_id, d.content, d.timestamp, d.rating, 'zero_results_existing_photo'
    FROM documents d
    WHERE (
        d.content LIKE '%No results shown%' OR
        d.content LIKE '%returns zero results%' OR
        d.content LIKE '%no results at all when searching%' OR
        d.content LIKE '%cant find your pictures without seeing%' OR
        d.content LIKE '%can''t find a single image in search%' OR
        d.content LIKE '%search feature has turned to trash%' OR
        d.content LIKE '%can''t find any photos%'
    )
    ORDER BY LENGTH(d.content) ASC
""")

# Q6: Endless Timeline Scrolling (scroll fatigue, scrolling through thousands of photos, infinite timeline)
curated[6] = get_candidates("""
    SELECT d.doc_id, d.source, d.source_id, d.content, d.timestamp, d.rating, 'endless_scrolling_fatigue'
    FROM documents d
    WHERE (
        d.content LIKE '%scrolling through thousands of pictures%' OR
        d.content LIKE '%jarring to scroll through searching for a particular photo%' OR
        d.content LIKE '%scroll down my timeline%' OR
        d.content LIKE '%scroll through your photo timeline%' OR
        d.content LIKE '%scroll through thousands%' OR
        (d.content LIKE '%scroll%' AND d.content LIKE '%photos%' AND d.content LIKE '%timeline%')
    )
    ORDER BY LENGTH(d.content) ASC
""")

# Q7: Screenshot & Junk Clutter (screenshots, receipts, memes, junk polluting gallery)
curated[7] = get_candidates("""
    SELECT d.doc_id, d.source, d.source_id, d.content, d.timestamp, d.rating, 'screenshot_and_junk_clutter'
    FROM documents d
    WHERE (
        d.content LIKE '%Screenshots folder%' OR
        d.content LIKE '%All taken screenshots now appear in the Camera folder%' OR
        d.content LIKE '%store receipts (which is super convenient for filing expense reports)%' OR
        d.content LIKE '%screenshots app%' OR
        (d.content LIKE '%screenshot%' AND d.content LIKE '%photo%' AND (d.content LIKE '%clutter%' OR d.content LIKE '%folder%' OR d.content LIKE '%delete%' OR d.content LIKE '%search%'))
    )
    ORDER BY LENGTH(d.content) ASC
""")

# Q8: Face Recognition Failures (People & Pets, wrong faces, pet recognition failures)
curated[8] = get_candidates("""
    SELECT d.doc_id, d.source, d.source_id, d.content, d.timestamp, d.rating, 'face_recognition_misidentification'
    FROM documents d
    WHERE (
        d.content LIKE '%fails to recognise pets%' OR
        d.content LIKE '%People and Pets, photos do not appear%' OR
        d.content LIKE '%face classification%' OR
        d.content LIKE '%search photos by people%' OR
        d.content LIKE '%tracking my face%' OR
        (d.content LIKE '%face%' AND d.content LIKE '%photo%' AND (d.content LIKE '%recogni%' OR d.content LIKE '%tag%' OR d.content LIKE '%people%'))
    )
    ORDER BY LENGTH(d.content) ASC
""")

# Q9: Text & Document Search Failures (OCR, text in photos, receipts, documents, handwriting)
curated[9] = get_candidates("""
    SELECT d.doc_id, d.source, d.source_id, d.content, d.timestamp, d.rating, 'text_ocr_detection_failure'
    FROM documents d
    WHERE (
        d.content LIKE '%search for my driving license%' OR
        d.content LIKE '%search text in images%' OR
        d.content LIKE '%find text of objects in photos%' OR
        d.content LIKE '%quick text based search%' OR
        d.content LIKE '%OCR and image search%' OR
        (d.content LIKE '%text%' AND d.content LIKE '%photo%' AND d.content LIKE '%search%')
    )
    ORDER BY LENGTH(d.content) ASC
""")

# Q10: Workarounds & Switching (leaving Google Photos, Apple Photos, Immich, WhatsApp media, NAS)
curated[10] = get_candidates("""
    SELECT d.doc_id, d.source, d.source_id, d.content, d.timestamp, d.rating, 'workarounds_and_switching'
    FROM documents d
    WHERE (
        d.content LIKE '%Immich is fantastic%' OR
        d.content LIKE '%leaving for competitors%' OR
        d.content LIKE '%suggest finding an alternative to entrust your precious memories%' OR
        d.content LIKE '%Google Photos/Drive because of AI-search. Dropbox because easy integration%' OR
        d.content LIKE '%hosting the originals on my own NAS%' OR
        d.content LIKE '%preventing people from ever leaving Google Photos%' OR
        d.content LIKE '%Time for a new App, goodbye Photos%'
    )
    ORDER BY LENGTH(d.content) ASC
""")

with open('scripts/curated_quotes_output.json', 'w', encoding='utf-8') as f:
    json.dump(curated, f, indent=2, ensure_ascii=False)

print("Curated output written. Counts:")
for qid in range(1, 11):
    print(f"Q{qid}: {len(curated[qid])} quotes found")
