"""
Extended Raw Data Fetcher for Google Photos Retrieval Corpus.
Fetches across 5 platforms: Play Store, App Store, Reddit, Hacker News, YouTube.
Saves all raw outputs into data/search_only_corpus/raw/ without touching existing files.
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

RAW_DIR = PROJECT_ROOT / "data" / "search_only_corpus" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# 1. HACKER NEWS (Algolia Search API)
# ─────────────────────────────────────────────────────────────
def fetch_hackernews():
    print("\n[1/5] 📡 Fetching Hacker News discussions via Algolia API...")
    queries = [
        '"google photos" search',
        '"google photos" find photo',
        '"google photos" "ask photos"',
        '"google photos" gemini search',
        '"google photos" search broken',
        '"google photos" search vs',
        '"google photos" face search',
        '"google photos" receipt search',
        '"google photos" zero results',
        '"google photos" no results',
        '"google photos" search results',
        '"google photos" scroll search',
    ]
    base_url = "https://hn.algolia.com/api/v1/search"
    results = []
    seen_ids = set()

    for q in queries:
        for page in range(4):  # up to 200 hits per query
            try:
                params = {"query": q, "tags": "comment", "hitsPerPage": 50, "page": page}
                resp = requests.get(base_url, params=params, timeout=15)
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
                    # simple html unescape/clean
                    import html, re
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
            except Exception as e:
                print(f"    HN error on {q} p{page}: {e}")
                break

    out_file = RAW_DIR / "hackernews_raw.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Hacker News: Saved {len(results)} raw items to {out_file.name}")
    return results


# ─────────────────────────────────────────────────────────────
# 2. REDDIT (Apify + Public Search Fallback)
# ─────────────────────────────────────────────────────────────
def fetch_reddit():
    print("\n[2/5] 📡 Fetching Reddit discussions...")
    apify_token = os.getenv("APIFY_API_TOKEN")
    results = []
    seen_ids = set()

    # Public JSON search across target subreddits
    subreddits = ["googlephotos", "GooglePixel", "Android", "androidapps", "selfhosted", "immich"]
    search_terms = [
        "search",
        "find photo",
        "ask photos",
        "gemini search",
        "search broken",
        "no results",
        "face search",
        "receipt search",
        "scroll search results",
        "search keywords",
    ]

    headers = {"User-Agent": "PhotosRetrievalResearch/2.0"}

    for sub in subreddits:
        for term in search_terms:
            try:
                url = f"https://www.reddit.com/r/{sub}/search.json"
                params = {"q": term, "restrict_sr": "on", "sort": "relevance", "limit": 40}
                resp = requests.get(url, headers=headers, params=params, timeout=12)
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
                        if len(combined) < 40:
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
                time.sleep(1.0)  # respectful rate limit
            except Exception as e:
                print(f"    Reddit public search error r/{sub} '{term}': {e}")

    # Also load existing reddit reviews from previous raw data to ensure max coverage
    prev_file = PROJECT_ROOT / "data" / "raw" / "reddit" / "reddit_reviews.csv"
    if prev_file.exists():
        import csv
        with open(prev_file, "r", encoding="utf-8", errors="ignore") as f:
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

    out_file = RAW_DIR / "reddit_raw.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Reddit: Saved {len(results)} raw items to {out_file.name}")
    return results


# ─────────────────────────────────────────────────────────────
# 3. YOUTUBE (YouTube Data API v3)
# ─────────────────────────────────────────────────────────────
def fetch_youtube():
    print("\n[3/5] 📡 Fetching YouTube video comments via Data API v3...")
    api_key = os.getenv("YOUTUBE_API_KEY")
    results = []
    seen_ids = set()

    # Load existing archive comments first
    prev_file = PROJECT_ROOT / "data" / "raw" / "youtube" / "youtube_reviews.csv"
    if prev_file.exists():
        import csv
        with open(prev_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
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
            ]

            video_ids = []
            for sq in search_queries:
                try:
                    req = youtube.search().list(q=sq, part="snippet", type="video", maxResults=15, order="relevance")
                    resp = req.execute()
                    for item in resp.get("items", []):
                        vid = item.get("id", {}).get("videoId")
                        if vid and vid not in video_ids:
                            video_ids.append(vid)
                except Exception as e:
                    print(f"    YouTube search error '{sq}': {e}")

            print(f"    Found {len(video_ids)} relevant YouTube videos. Fetching top comments...")
            for vid in video_ids[:25]:
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
                        import re
                        clean = re.sub(r"<[^>]+>", " ", text).strip()
                        if len(clean) < 30:
                            continue
                        results.append({
                            "doc_id": f"youtube_{cid}",
                            "source": "youtube",
                            "source_id": cid,
                            "author": cdata.get("authorDisplayName", "anonymous"),
                            "created_at": cdata.get("publishedAt", ""),
                            "content": clean,
                            "query": "video_comments",
                            "url": f"https://www.youtube.com/watch?v={vid}",
                        })
                except Exception:
                    pass  # comments may be disabled
        except Exception as e:
            print(f"    YouTube API init error: {e}")

    out_file = RAW_DIR / "youtube_raw.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  ✅ YouTube: Saved {len(results)} raw items to {out_file.name}")
    return results


# ─────────────────────────────────────────────────────────────
# 4. APPLE APP STORE (Multi-Country RSS Feeds)
# ─────────────────────────────────────────────────────────────
def fetch_appstore():
    print("\n[4/5] 📡 Fetching Apple App Store reviews across multi-country feeds...")
    app_id = "962194608"
    countries = ["us", "gb", "ca", "au"]
    results = []
    seen_ids = set()

    # Load existing archive first
    prev_file = PROJECT_ROOT / "data" / "raw" / "appstore" / "batch_0001.json"
    if prev_file.exists():
        with open(prev_file, "r", encoding="utf-8") as f:
            batch = json.load(f)
            for item in batch:
                sid = item.get("source_id") or item.get("doc_id")
                if sid and sid not in seen_ids:
                    seen_ids.add(sid)
                    results.append({
                        "doc_id": f"appstore_{sid}",
                        "source": "appstore",
                        "source_id": sid,
                        "author": item.get("author", "anonymous"),
                        "created_at": item.get("created_at", ""),
                        "content": item.get("content", ""),
                        "rating": item.get("rating", 0),
                        "query": "archive_seed",
                    })

    for country in countries:
        for page in range(1, 11):
            try:
                url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortBy=mostRecent/json"
                resp = requests.get(url, timeout=12)
                if resp.status_code != 200:
                    break
                data = resp.json()
                feed = data.get("feed", {})
                entries = feed.get("entry", [])
                if not entries:
                    break
                for entry in entries:
                    try:
                        rid = entry.get("id", {}).get("label")
                        if not rid or rid in seen_ids:
                            continue
                        seen_ids.add(rid)
                        title = entry.get("title", {}).get("label", "")
                        content = entry.get("content", {}).get("label", "")
                        rating = int(entry.get("im:rating", {}).get("label", 0))
                        combined = f"{title}\n\n{content}".strip()
                        if len(combined) < 25:
                            continue
                        results.append({
                            "doc_id": f"appstore_{rid}",
                            "source": "appstore",
                            "source_id": rid,
                            "author": entry.get("author", {}).get("name", {}).get("label", "anonymous"),
                            "created_at": entry.get("updated", {}).get("label", ""),
                            "content": combined,
                            "rating": rating,
                            "query": f"rss_{country}",
                        })
                    except Exception:
                        continue
            except Exception as e:
                print(f"    App Store feed error ({country} p{page}): {e}")
                break

    out_file = RAW_DIR / "appstore_raw.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Apple App Store: Saved {len(results)} raw items to {out_file.name}")
    return results


# ─────────────────────────────────────────────────────────────
# 5. GOOGLE PLAY STORE (Multi-Region Scraper)
# ─────────────────────────────────────────────────────────────
def fetch_playstore():
    print("\n[5/5] 📡 Fetching Google Play Store reviews across regions and sort modes...")
    results = []
    seen_ids = set()

    # Load existing archive first
    prev_file = PROJECT_ROOT / "data" / "raw" / "playstore" / "playstore_reviews.csv"
    if prev_file.exists():
        import csv
        with open(prev_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
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
                        "rating": row.get("rating", 0),
                        "query": "archive_seed",
                    })

    try:
        from google_play_scraper import reviews, Sort
        regions = ["us", "gb", "ca", "au", "in"]
        sorts = [Sort.MOST_RELEVANT, Sort.NEWEST]

        for reg in regions:
            for s in sorts:
                for score in [1, 2, 3, None]:
                    try:
                        batch, _ = reviews(
                            "com.google.android.apps.photos",
                            lang="en",
                            country=reg,
                            sort=s,
                            count=150,
                            filter_score_with=score,
                        )
                        for r in batch:
                            rid = r.get("reviewId")
                            if not rid or rid in seen_ids:
                                continue
                            seen_ids.add(rid)
                            content = r.get("content") or ""
                            if len(content.strip()) < 25:
                                continue
                            at = r.get("at")
                            at_iso = at.isoformat() if at else ""
                            results.append({
                                "doc_id": f"playstore_{rid}",
                                "source": "playstore",
                                "source_id": rid,
                                "author": r.get("userName", "anonymous"),
                                "created_at": at_iso,
                                "content": content.strip(),
                                "rating": r.get("score", 0),
                                "query": f"{reg}_{score}",
                            })
                    except Exception as e:
                        print(f"    Play Store error {reg}/{score}: {e}")
                        break
    except Exception as e:
        print(f"    google_play_scraper error: {e}")

    out_file = RAW_DIR / "playstore_raw.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Google Play Store: Saved {len(results)} raw items to {out_file.name}")
    return results


def main():
    print("=" * 65)
    print("🚀 EXTENDED RAW SOURCE HARVEST (5 PLATFORMS)")
    print("=" * 65)
    hn_docs = fetch_hackernews()
    reddit_docs = fetch_reddit()
    yt_docs = fetch_youtube()
    app_docs = fetch_appstore()
    play_docs = fetch_playstore()

    total_raw = len(hn_docs) + len(reddit_docs) + len(yt_docs) + len(app_docs) + len(play_docs)
    print("\n" + "=" * 65)
    print(f"🎉 TOTAL RAW DOCUMENTS HARVESTED: {total_raw:,}")
    print(f"  • Google Play Store:   {len(play_docs):,}")
    print(f"  • Apple App Store:     {len(app_docs):,}")
    print(f"  • Reddit:              {len(reddit_docs):,}")
    print(f"  • Hacker News:         {len(hn_docs):,}")
    print(f"  • YouTube:             {len(yt_docs):,}")
    print("=" * 65)


if __name__ == "__main__":
    main()
