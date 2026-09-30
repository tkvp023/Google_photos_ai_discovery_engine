"""
Scaled Raw Data Harvester for Search-Only Retrieval Corpus.
Targets high-yield visual search and retrieval discussions across 5 platforms:
Hacker News, Reddit, Play Store, App Store, and YouTube.
Saves outputs directly into data/search_only_corpus/raw/ without touching legacy databases.
"""

import os
import sys
import json
import time
import requests
import html
import re
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

RAW_DIR = PROJECT_ROOT / "data" / "search_only_corpus" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# 1. HACKER NEWS (45 Deep Retrieval Queries, Up to 10 Pages Each)
# ─────────────────────────────────────────────────────────────
def fetch_scaled_hackernews():
    print("\n[1/5] 📡 Fetching Scaled Hacker News discussions via Algolia API...")
    queries = [
        '"google photos" search',
        '"google photos" "find photo"',
        '"google photos" "ask photos"',
        '"google photos" gemini search',
        '"google photos" OCR',
        '"google photos" semantic search',
        '"google photos" search bar',
        '"google photos" search broken',
        '"google photos" visual search',
        '"google photos" CLIP',
        '"google photos" receipt search',
        '"google photos" face search',
        '"google photos" zero results',
        '"google photos" no results',
        '"google photos" search results',
        '"google photos" scroll search',
        '"google photos" search syntax',
        '"google photos" search people',
        '"google photos" locate photo',
        '"google photos" search keywords',
        '"google photos" search by date',
        '"google photos" search by location',
        '"google photos" search album',
        '"google photos" search video',
        '"google photos" natural language search',
        '"google photos" search license plate',
        '"google photos" search dog',
        '"google photos" search document',
        '"google photos" search text in photo',
        '"google photos" image search',
        '"google photos" metadata search',
        '"google photos" search tags',
        '"google photos" search algorithm',
        '"google photos" search feature',
        '"google photos" search sucks',
        '"google photos" search worse',
        '"google photos" search update',
        '"google photos" search prompt',
        '"google photos" query photo',
        '"google photos" filter photos',
        '"google photos" retrieve photo',
        '"google photos" search query',
        '"google photos" search broken update',
        '"google photos" AI search',
        '"google photos" search works',
    ]

    base_url = "https://hn.algolia.com/api/v1/search"
    results = []
    seen_ids = set()

    # Load existing to preserve
    existing_file = RAW_DIR / "hackernews_raw.json"
    if existing_file.exists():
        try:
            with open(existing_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                for d in existing_data:
                    cid = d.get("source_id")
                    if cid:
                        seen_ids.add(str(cid))
                        results.append(d)
            print(f"  🔁 Seeded with {len(results):,} existing HN records.")
        except Exception:
            pass

    for q_idx, q in enumerate(queries, 1):
        new_in_q = 0
        for page in range(8):  # up to 400 comments per query
            try:
                params = {"query": q, "tags": "comment", "hitsPerPage": 50, "page": page}
                resp = requests.get(base_url, params=params, timeout=12)
                if resp.status_code != 200:
                    break
                hits = resp.json().get("hits", [])
                if not hits:
                    break
                for h in hits:
                    cid = str(h.get("objectID"))
                    if cid in seen_ids:
                        continue
                    seen_ids.add(cid)
                    text = h.get("comment_text") or ""
                    clean_text = html.unescape(text)
                    clean_text = re.sub(r"<[^>]+>", " ", clean_text).strip()
                    if len(clean_text) < 30:
                        continue
                    results.append({
                        "doc_id": f"hn_{cid}",
                        "source": "hackernews",
                        "source_id": cid,
                        "author": h.get("author", "anonymous"),
                        "created_at": h.get("created_at", ""),
                        "content": clean_text,
                        "query": q,
                        "url": f"https://news.ycombinator.com/item?id={cid}",
                    })
                    new_in_q += 1
                time.sleep(0.15)
            except Exception as e:
                print(f"    HN error on '{q}' p{page}: {e}")
                break
        print(f"  [{q_idx}/{len(queries)}] '{q}' -> +{new_in_q} new comments (Total: {len(results):,})")

    out_file = RAW_DIR / "hackernews_raw.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Hacker News Harvest Complete: {len(results):,} unique comments saved.")
    return results


# ─────────────────────────────────────────────────────────────
# 2. REDDIT (Multi-Subreddit & Archive Expansion)
# ─────────────────────────────────────────────────────────────
def fetch_scaled_reddit():
    print("\n[2/5] 📡 Fetching Scaled Reddit discussions...")
    results = []
    seen_ids = set()

    existing_file = RAW_DIR / "reddit_raw.json"
    if existing_file.exists():
        try:
            with open(existing_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                for d in existing_data:
                    pid = d.get("source_id")
                    if pid:
                        seen_ids.add(str(pid))
                        results.append(d)
            print(f"  🔁 Seeded with {len(results):,} existing Reddit records.")
        except Exception:
            pass

    # Load archive seeds
    archive_paths = [
        PROJECT_ROOT / "data" / "raw" / "reddit" / "reddit_reviews.csv",
        PROJECT_ROOT / "data" / "raw" / "reddit" / "batch_0001.json",
    ]
    for p in archive_paths:
        if p.exists():
            try:
                if p.suffix == ".csv":
                    import csv
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            pid = row.get("source_id") or row.get("doc_id")
                            if pid and pid not in seen_ids:
                                seen_ids.add(pid)
                                results.append({
                                    "doc_id": f"reddit_{pid}",
                                    "source": "reddit",
                                    "source_id": pid,
                                    "subreddit": row.get("subreddit", "googlephotos"),
                                    "author": row.get("author", "anonymous"),
                                    "created_at": row.get("created_at", ""),
                                    "content": row.get("content", ""),
                                    "query": "archive_seed",
                                    "url": row.get("url", ""),
                                })
                elif p.suffix == ".json":
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for row in data:
                            pid = row.get("source_id") or row.get("doc_id") or row.get("id")
                            if pid and str(pid) not in seen_ids:
                                seen_ids.add(str(pid))
                                results.append({
                                    "doc_id": f"reddit_{pid}",
                                    "source": "reddit",
                                    "source_id": str(pid),
                                    "subreddit": row.get("subreddit", "googlephotos"),
                                    "author": row.get("author", "anonymous"),
                                    "created_at": row.get("created_at", ""),
                                    "content": row.get("content", row.get("text", "")),
                                    "query": "archive_json",
                                    "url": row.get("url", ""),
                                })
            except Exception as e:
                print(f"    Archive read error on {p.name}: {e}")

    # Search subreddits
    subreddits = ["googlephotos", "GooglePixel", "Android", "androidapps", "selfhosted", "immich", "photography", "google"]
    search_terms = [
        "search", "find photo", "ask photos", "gemini search", "search broken",
        "no results", "face search", "receipt search", "scroll search results",
        "search keywords", "cant find", "locate photo", "search bar", "OCR",
        "search algorithm", "search people", "search text", "search date",
        "search location", "search query"
    ]

    headers = {"User-Agent": "PhotosSearchHarvest/3.0"}
    for sub in subreddits:
        for term in search_terms:
            try:
                url = f"https://www.reddit.com/r/{sub}/search.json"
                params = {"q": term, "restrict_sr": "on", "sort": "relevance", "limit": 40}
                resp = requests.get(url, headers=headers, params=params, timeout=10)
                if resp.status_code == 200:
                    data = resp.json().get("data", {}).get("children", [])
                    for post in data:
                        pdata = post.get("data", {})
                        pid = pdata.get("id")
                        if not pid or pid in seen_ids:
                            continue
                        seen_ids.add(pid)
                        title = pdata.get("title", "")
                        selftext = pdata.get("selftext", "")
                        combined = f"{title}\n\n{selftext}".strip()
                        if len(combined) < 35:
                            continue
                        created_utc = pdata.get("created_utc", 0)
                        created_dt = datetime.fromtimestamp(created_utc, timezone.utc).isoformat() if created_utc else ""
                        results.append({
                            "doc_id": f"reddit_{pid}",
                            "source": "reddit",
                            "source_id": pid,
                            "subreddit": sub,
                            "author": pdata.get("author", "anonymous"),
                            "created_at": created_dt,
                            "content": combined,
                            "query": term,
                            "url": f"https://reddit.com{pdata.get('permalink', '')}",
                        })
                time.sleep(0.8)
            except Exception as e:
                pass

    out_file = RAW_DIR / "reddit_raw.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Reddit Harvest Complete: {len(results):,} unique records saved.")
    return results


# ─────────────────────────────────────────────────────────────
# 3. YOUTUBE (Targeted Search & Video Comment Harvest)
# ─────────────────────────────────────────────────────────────
def fetch_scaled_youtube():
    print("\n[3/5] 📡 Fetching Scaled YouTube video comments...")
    api_key = os.getenv("YOUTUBE_API_KEY")
    results = []
    seen_ids = set()

    existing_file = RAW_DIR / "youtube_raw.json"
    if existing_file.exists():
        try:
            with open(existing_file, "r", encoding="utf-8") as f:
                for d in json.load(f):
                    cid = d.get("source_id")
                    if cid:
                        seen_ids.add(str(cid))
                        results.append(d)
            print(f"  🔁 Seeded with {len(results):,} existing YouTube records.")
        except Exception:
            pass

    # Load archive comments
    archive_paths = [
        PROJECT_ROOT / "data" / "raw" / "youtube" / "youtube_reviews.csv",
        PROJECT_ROOT / "data" / "raw" / "youtube" / "batch_0001.json",
    ]
    for p in archive_paths:
        if p.exists():
            try:
                if p.suffix == ".csv":
                    import csv
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        for row in csv.DictReader(f):
                            cid = row.get("source_id") or row.get("doc_id")
                            if cid and cid not in seen_ids:
                                seen_ids.add(cid)
                                results.append({
                                    "doc_id": f"youtube_{cid}",
                                    "source": "youtube",
                                    "source_id": cid,
                                    "author": row.get("author", "anonymous"),
                                    "created_at": row.get("created_at", ""),
                                    "content": row.get("content", ""),
                                    "query": "archive_seed",
                                    "url": row.get("url", ""),
                                })
                elif p.suffix == ".json":
                    with open(p, "r", encoding="utf-8") as f:
                        for row in json.load(f):
                            cid = row.get("source_id") or row.get("doc_id")
                            if cid and str(cid) not in seen_ids:
                                seen_ids.add(str(cid))
                                results.append({
                                    "doc_id": f"youtube_{cid}",
                                    "source": "youtube",
                                    "source_id": str(cid),
                                    "author": row.get("author", "anonymous"),
                                    "created_at": row.get("created_at", ""),
                                    "content": row.get("content", row.get("text", "")),
                                    "query": "archive_json",
                                    "url": row.get("url", ""),
                                })
            except Exception as e:
                pass

    if api_key:
        try:
            from googleapiclient.discovery import build
            youtube = build("youtube", "v3", developerKey=api_key)

            search_queries = [
                "google photos search tips",
                "google photos ask photos gemini",
                "how to search google photos",
                "google photos search problems",
                "google photos find old photos",
                "google photos vs apple photos search",
                "google photos search tricks you didn't know",
                "google photos search feature review",
                "google photos ask photos test",
                "find receipt in google photos",
                "google photos facial recognition search",
                "google photos search by text OCR",
            ]

            video_ids = []
            for sq in search_queries:
                try:
                    req = youtube.search().list(q=sq, part="snippet", type="video", maxResults=20, order="relevance")
                    resp = req.execute()
                    for item in resp.get("items", []):
                        vid = item.get("id", {}).get("videoId")
                        if vid and vid not in video_ids:
                            video_ids.append(vid)
                except Exception as e:
                    print(f"    YouTube query '{sq}' error: {e}")

            print(f"    Targeting {len(video_ids)} search-focused YouTube videos...")
            for vid in video_ids[:40]:
                try:
                    req = youtube.commentThreads().list(videoId=vid, part="snippet", maxResults=50, order="relevance")
                    resp = req.execute()
                    for item in resp.get("items", []):
                        cdata = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                        cid = item.get("id")
                        if not cid or cid in seen_ids:
                            continue
                        seen_ids.add(cid)
                        text = cdata.get("textDisplay", "")
                        clean_text = html.unescape(text)
                        clean_text = re.sub(r"<[^>]+>", " ", clean_text).strip()
                        if len(clean_text) < 25:
                            continue
                        results.append({
                            "doc_id": f"youtube_{cid}",
                            "source": "youtube",
                            "source_id": cid,
                            "author": cdata.get("authorDisplayName", "anonymous"),
                            "created_at": cdata.get("publishedAt", ""),
                            "content": clean_text,
                            "video_id": vid,
                            "query": "video_comment",
                            "url": f"https://www.youtube.com/watch?v={vid}",
                        })
                except Exception:
                    pass
        except Exception as e:
            print(f"    YouTube Data API build error: {e}")

    out_file = RAW_DIR / "youtube_raw.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  ✅ YouTube Harvest Complete: {len(results):,} unique comments saved.")
    return results


# ─────────────────────────────────────────────────────────────
# 4. GOOGLE PLAY STORE (Scaled Multi-Region & Archive Harvest)
# ─────────────────────────────────────────────────────────────
def fetch_scaled_playstore():
    print("\n[4/5] 📡 Fetching Scaled Play Store reviews...")
    results = []
    seen_ids = set()

    existing_file = RAW_DIR / "playstore_raw.json"
    if existing_file.exists():
        try:
            with open(existing_file, "r", encoding="utf-8") as f:
                for d in json.load(f):
                    pid = d.get("source_id")
                    if pid:
                        seen_ids.add(str(pid))
                        results.append(d)
            print(f"  🔁 Seeded with {len(results):,} existing Play Store records.")
        except Exception:
            pass

    # Load all archive CSV and JSON batches
    archive_dir = PROJECT_ROOT / "data" / "raw" / "playstore"
    if archive_dir.exists():
        for p in sorted(archive_dir.glob("*")):
            try:
                if p.suffix == ".csv":
                    import csv
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        for row in csv.DictReader(f):
                            pid = row.get("source_id") or row.get("doc_id")
                            if pid and pid not in seen_ids:
                                seen_ids.add(pid)
                                results.append({
                                    "doc_id": f"playstore_{pid}",
                                    "source": "playstore",
                                    "source_id": pid,
                                    "author": row.get("author", "anonymous"),
                                    "created_at": row.get("created_at", ""),
                                    "content": row.get("content", ""),
                                    "rating": row.get("score", row.get("rating", "")),
                                    "url": "https://play.google.com/store/apps/details?id=com.google.android.apps.photos",
                                })
                elif p.suffix == ".json":
                    with open(p, "r", encoding="utf-8") as f:
                        for row in json.load(f):
                            pid = row.get("source_id") or row.get("doc_id") or row.get("reviewId")
                            if pid and str(pid) not in seen_ids:
                                seen_ids.add(str(pid))
                                results.append({
                                    "doc_id": f"playstore_{pid}",
                                    "source": "playstore",
                                    "source_id": str(pid),
                                    "author": row.get("author", row.get("userName", "anonymous")),
                                    "created_at": row.get("created_at", str(row.get("at", ""))),
                                    "content": row.get("content", ""),
                                    "rating": row.get("score", row.get("rating", "")),
                                    "url": "https://play.google.com/store/apps/details?id=com.google.android.apps.photos",
                                })
            except Exception:
                pass

    # Deep scrape via google-play-scraper across regions
    try:
        from google_play_scraper import reviews, Sort
        regions = ["us", "gb", "ca", "au", "in"]
        for r_idx, reg in enumerate(regions, 1):
            for sort_mode in [Sort.MOST_RELEVANT, Sort.NEWEST]:
                try:
                    rvs, _ = reviews(
                        "com.google.android.apps.photos",
                        lang="en",
                        country=reg,
                        sort=sort_mode,
                        count=500
                    )
                    for r in rvs:
                        rid = r.get("reviewId")
                        if not rid or rid in seen_ids:
                            continue
                        seen_ids.add(rid)
                        content = r.get("content", "").strip()
                        if len(content) < 25:
                            continue
                        at = r.get("at")
                        results.append({
                            "doc_id": f"playstore_{rid}",
                            "source": "playstore",
                            "source_id": rid,
                            "author": r.get("userName", "anonymous"),
                            "created_at": at.isoformat() if hasattr(at, "isoformat") else str(at),
                            "content": content,
                            "rating": r.get("score"),
                            "url": "https://play.google.com/store/apps/details?id=com.google.android.apps.photos",
                        })
                except Exception as e:
                    print(f"    Play Store {reg} error: {e}")
                time.sleep(0.5)
            print(f"  [{r_idx}/{len(regions)}] Region '{reg}' scraped -> Total: {len(results):,}")
    except Exception as e:
        print(f"    google-play-scraper error: {e}")

    out_file = RAW_DIR / "playstore_raw.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Play Store Harvest Complete: {len(results):,} unique records saved.")
    return results


# ─────────────────────────────────────────────────────────────
# 5. APPLE APP STORE (Preserve & Scale)
# ─────────────────────────────────────────────────────────────
def fetch_scaled_appstore():
    print("\n[5/5] 📡 Loading Scaled App Store reviews...")
    results = []
    seen_ids = set()

    existing_file = RAW_DIR / "appstore_raw.json"
    if existing_file.exists():
        try:
            with open(existing_file, "r", encoding="utf-8") as f:
                for d in json.load(f):
                    aid = d.get("source_id")
                    if aid:
                        seen_ids.add(str(aid))
                        results.append(d)
            print(f"  🔁 Seeded with {len(results):,} existing App Store records.")
        except Exception:
            pass

    # Load archive batch
    archive_dir = PROJECT_ROOT / "data" / "raw" / "appstore"
    if archive_dir.exists():
        for p in archive_dir.glob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for row in json.load(f):
                        aid = row.get("source_id") or row.get("doc_id") or row.get("id")
                        if aid and str(aid) not in seen_ids:
                            seen_ids.add(str(aid))
                            results.append({
                                "doc_id": f"appstore_{aid}",
                                "source": "appstore",
                                "source_id": str(aid),
                                "author": row.get("author", "anonymous"),
                                "created_at": row.get("created_at", ""),
                                "content": row.get("content", ""),
                                "rating": row.get("score", row.get("rating", "")),
                                "url": "https://apps.apple.com/app/id962194608",
                            })
            except Exception:
                pass

    out_file = RAW_DIR / "appstore_raw.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  ✅ App Store Complete: {len(results):,} unique records saved.")
    return results


def main():
    print("=" * 65)
    print("🚀 SCALED RAW DATA HARVESTER (TARGET: 1,500+ SEARCH IN-SCOPE)")
    print("=" * 65)

    hn = fetch_scaled_hackernews()
    rd = fetch_scaled_reddit()
    yt = fetch_scaled_youtube()
    ps = fetch_scaled_playstore()
    ap = fetch_scaled_appstore()

    total_docs = len(hn) + len(rd) + len(yt) + len(ps) + len(ap)
    print("\n" + "=" * 65)
    print("🎉 HARVEST COMPLETE ACROSS ALL 5 PLATFORMS!")
    print(f"  • Hacker News:    {len(hn):,} raw documents")
    print(f"  • Reddit:         {len(rd):,} raw documents")
    print(f"  • YouTube:        {len(yt):,} raw documents")
    print(f"  • Play Store:     {len(ps):,} raw documents")
    print(f"  • App Store:      {len(ap):,} raw documents")
    print(f"  • TOTAL RAW POOL: {total_docs:,} raw documents")
    print("=" * 65)

if __name__ == "__main__":
    main()
