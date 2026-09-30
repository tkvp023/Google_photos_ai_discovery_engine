"""
Deep Search Harvester for Hacker News Algolia API.
Queries high-yield unquoted search terms to pull 4,000+ targeted comments.
"""

import sys
import json
import time
import requests
import html
import re
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "search_only_corpus" / "raw"
RAW_FILE = RAW_DIR / "hackernews_raw.json"

QUERIES = [
    "google photos search",
    "google photos find",
    "google photos OCR",
    "google photos face",
    "google photos query",
    "google photos receipt",
    "google photos semantic",
    "google photos CLIP",
    "google photos ask",
    "google photos retrieve",
    "google photos locate",
    "google photos search bar",
    "google photos keywords",
    "google photos recognition",
    "google photos people search",
    "google photos date search",
    "google photos location search",
    "google photos natural language",
    "google photos ask photos",
    "google photos search broken",
]

def main():
    print("=" * 65)
    print("📡 DEEP HACKER NEWS HARVESTER (UNQUOTED HIGH-YIELD QUERIES)")
    print("=" * 65)

    existing_docs = []
    seen_ids = set()
    if RAW_FILE.exists():
        try:
            with open(RAW_FILE, "r", encoding="utf-8") as f:
                existing_docs = json.load(f)
                for d in existing_docs:
                    cid = d.get("source_id")
                    if cid:
                        seen_ids.add(str(cid))
            print(f"🔁 Seeded with {len(existing_docs):,} existing HN comments.")
        except Exception:
            pass

    base_url = "https://hn.algolia.com/api/v1/search"
    added_total = 0

    for q_idx, q in enumerate(QUERIES, 1):
        added_for_q = 0
        # Fetch up to 15 pages (750 hits per query)
        for page in range(15):
            try:
                params = {
                    "query": q,
                    "tags": "comment",
                    "hitsPerPage": 50,
                    "page": page
                }
                resp = requests.get(base_url, params=params, timeout=12)
                if resp.status_code != 200:
                    break
                hits = resp.json().get("hits", [])
                if not hits:
                    break

                for h in hits:
                    cid = str(h.get("objectID"))
                    if not cid or cid in seen_ids:
                        continue
                    seen_ids.add(cid)

                    raw_comment = h.get("comment_text") or ""
                    clean_text = html.unescape(raw_comment)
                    clean_text = re.sub(r"<[^>]+>", " ", clean_text).strip()

                    # Quality filter: must be substantive and mention photos/google
                    lower = clean_text.lower()
                    if len(clean_text) < 35 or "photo" not in lower:
                        continue

                    existing_docs.append({
                        "doc_id": f"hn_{cid}",
                        "source": "hackernews",
                        "source_id": cid,
                        "author": h.get("author", "anonymous"),
                        "created_at": h.get("created_at", ""),
                        "content": clean_text,
                        "query": q,
                        "url": f"https://news.ycombinator.com/item?id={cid}",
                    })
                    added_for_q += 1
                    added_total += 1

                time.sleep(0.12)
            except Exception as e:
                print(f"    Error on '{q}' p{page}: {e}")
                break

        print(f"  [{q_idx}/{len(QUERIES)}] '{q}' -> +{added_for_q} new comments (Total: {len(existing_docs):,})", flush=True)

    with open(RAW_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_docs, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 65)
    print(f"🎉 DEEP HN HARVEST COMPLETE!")
    print(f"  • New comments added:  +{added_total:,}")
    print(f"  • Total HN pool:       {len(existing_docs):,} unique comments")
    print(f"  • Saved to:            {RAW_FILE}")
    print("=" * 65)

if __name__ == "__main__":
    main()
