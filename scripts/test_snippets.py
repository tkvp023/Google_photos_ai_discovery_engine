import sqlite3
import html
import re
import json

conn = sqlite3.connect('data/db.sqlite')
c = conn.cursor()

def clean(t):
    t = html.unescape(t)
    t = re.sub(r'http\S+', '', t)
    t = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def find_doc(doc_id_or_snippet):
    row = c.execute("""
        SELECT doc_id, source, source_id, content, timestamp, rating 
        FROM documents 
        WHERE doc_id = ? OR content LIKE ?
        LIMIT 1
    """, (doc_id_or_snippet, f"%{doc_id_or_snippet}%")).fetchone()
    if not row:
        return None
    return {
        "doc_id": row[0],
        "source": row[1],
        "source_id": row[2],
        "text": clean(row[3]),
        "date": str(row[4] or '')[:10],
        "rating": row[5]
    }

# Let's search candidates for all 10 questions
q_queries = {
    1: [
        "driving license",
        "bills and documents",
        "store receipts (which is super convenient",
        "MY PHOTOS ARE MISSING!! My old photos",
        "vacation with 300 photos",
    ],
    2: [
        "easily I can find old photos and memories by date, location, or people",
        "find text of objects in photos and the map",
        "search for pictures of dogs, sunsets, trees",
        "I just searched on Google Photos by her name and it found a bunch because of the face classification",
    ],
    3: [
        "aren't organized into different days anymore and everything is just bunched up",
        "newer videos appear on wrong dates",
        "cannot find a single image in search because they took away this basic function",
        "searching in the Photos app on my Android phone returns zero results",
    ],
    4: [
        "the app has been so poor recently with the search keywords",
        "where did the search feature go? I have to \"ask\" now",
        "Search no longer works. Photos just hangs when I type in a search term",
        "replacing it with 'ask' is the worst feature",
        "integrating Gemini into so many apps so fast seems to",
    ],
    5: [
        "returns zero results for any search term",
        "cant find your pictures without seeing \"no results\"",
        "no results at all when searching on the Android equivalent app",
        "I can't find a single image in search because they took away this basic function",
        "The search feature has turned to trash. Stop making your apps worse",
    ],
    6: [
        "scrolling through thousands of pictures",
        "makes it really jarring to scroll through searching for a particular photo",
        "as I scroll down my timeline, newer videos appear on wrong dates",
        "Scroll through your photo timeline. Anything with a cloud",
    ],
    7: [
        "All taken screenshots now appear in the Camera folder instead",
        "screenshots app. Maybe it works on other Android devices",
        "like blurry photos, screenshots and large videos",
        "even pictures of store receipts (which is super convenient for filing expense reports)",
    ],
    8: [
        "fails to recognise pets in a lot of photos",
        "Google arranges photos by face recognition",
        "face classification. That's some good",
        "search photos by people\" feature. I find this creepy",
    ],
    9: [
        "search for my driving license just by searching 'license'",
        "search text in images",
        "find text of objects in photos and the map+time search",
        "quick text based search, like me with clock tower",
    ],
    10: [
        "leaving for competitors.. 2023 Edit: Latest update ruined",
        "I would suggest finding an alternative to entrust your precious memories with",
        "Immich is fantastic",
        "hosting the originals on my own NAS and upload a copy in Google Photos",
        "Time for a new App, goodbye Photos. Update: Google Dark Patterns",
    ]
}

print("Testing quote retrieval for all questions...")
for qid, snippets in q_queries.items():
    print(f"\n--- Q{qid} ---")
    for s in snippets:
        res = find_doc(s)
        if res:
            print(f"  FOUND [{res['source']} | len={len(res['text'])}]: {res['text'][:100]}...")
        else:
            print(f"  NOT FOUND: {s}")
