import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import json
import csv
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

token = os.getenv("APIFY_API_TOKEN")
if not token:
    print("❌ APIFY_API_TOKEN not found in .env")
    sys.exit(1)

client = ApifyClient(token)

start_urls = [
    {"url": "https://www.reddit.com/r/GooglePixel/search/?q=photos+search&restrict_sr=1"},
    {"url": "https://www.reddit.com/r/GooglePixel/search/?q=ask+photos+gemini&restrict_sr=1"},
    {"url": "https://www.reddit.com/r/GooglePixel/search/?q=face+grouping+fail&restrict_sr=1"},
    {"url": "https://www.reddit.com/r/immich/search/?q=google+photos+search&restrict_sr=1"},
    {"url": "https://www.reddit.com/r/immich/search/?q=facial+recognition&restrict_sr=1"},
    {"url": "https://www.reddit.com/r/selfhosted/search/?q=google+photos+search+replacement&restrict_sr=1"},
    {"url": "https://www.reddit.com/r/googlephotos/search/?q=search+lost+photos&restrict_sr=1"},
    {"url": "https://www.reddit.com/r/googlephotos/search/?q=date+wrong+search&restrict_sr=1"},
]

run_input = {
    "startUrls": start_urls,
    "maxItems": 200,
    "includeComments": True,
    "maxComments": 5,
    "sort": "relevance",
    "time": "all",
}

actor_id = os.getenv("APIFY_REDDIT_ACTOR", "trudax/reddit-scraper-lite")
print(f"🚀 Calling Apify Actor `{actor_id}` for targeted subreddits (r/GooglePixel, r/immich, r/selfhosted, r/googlephotos)...")

try:
    run = client.actor(actor_id).call(run_input=run_input)
except Exception as e:
    print(f"⚠️ Error launching actor: {e}")
    run = None

raw_dir = Path("data/raw/reddit")
raw_dir.mkdir(parents=True, exist_ok=True)
json_path = raw_dir / "batch_0001.json"
csv_path = raw_dir / "reddit_reviews.csv"

# Load existing
existing_items = []
seen_ids = set()
if json_path.exists():
    with open(json_path, "r", encoding="utf-8") as f:
        existing_items = json.load(f)
        for item in existing_items:
            seen_ids.add(item.get("source_id", ""))

new_items = 0

if run:
    ds_id = getattr(run, "default_dataset_id", None) or (run.get("defaultDatasetId") if isinstance(run, dict) else "")
    print(f"📦 Harvesting dataset {ds_id}...")
    if ds_id:
        for item in client.dataset(ds_id).iterate_items():
            content = item.get("body") or item.get("text") or item.get("selftext") or ""
            title = item.get("title") or ""
            full_content = f"{title}\n\n{content}".strip() if (title and content) else (content or title)

            if not full_content or full_content in ("[deleted]", "[removed]"):
                continue

            raw_id = item.get("id") or item.get("postId") or item.get("commentId") or str(hash(full_content))[:12]
            source_id = f"reddit_{raw_id}"

            if source_id in seen_ids:
                continue

            subreddit = item.get("subreddit") or item.get("communityName") or "googlephotos"
            author = item.get("author") or item.get("username") or "reddit_user"
            raw_time = item.get("createdAt") or item.get("parsedTime") or datetime.now(timezone.utc).isoformat()
            url = item.get("url") or item.get("link") or ""

            doc = {
                "source": "reddit",
                "source_type": "primary",
                "source_id": source_id,
                "author": author if author != "[deleted]" else "reddit_user",
                "content": full_content,
                "title": title if title else None,
                "rating": None,
                "timestamp": raw_time,
                "url": url,
                "metadata": {
                    "subreddit": str(subreddit).replace("r/", ""),
                    "upvotes": item.get("upVotes") or item.get("score") or 0,
                    "comment_count": item.get("numberOfComments") or item.get("numComments") or 0,
                    "scraper_engine": "apify",
                }
            }

            existing_items.append(doc)
            seen_ids.add(source_id)
            new_items += 1

            # Check comments
            comments = item.get("comments") or item.get("commentList") or []
            if isinstance(comments, list):
                for comment in comments:
                    cbody = comment.get("body") or comment.get("text") or ""
                    if not cbody.strip() or cbody in ("[deleted]", "[removed]"):
                        continue
                    cid = comment.get("id") or comment.get("commentId") or str(hash(cbody))[:10]
                    csource_id = f"reddit_comment_{cid}"
                    if csource_id in seen_ids:
                        continue

                    cdoc = {
                        "source": "reddit",
                        "source_type": "primary",
                        "source_id": csource_id,
                        "author": "reddit_user",
                        "content": cbody.strip(),
                        "title": None,
                        "rating": None,
                        "timestamp": comment.get("createdAt") or raw_time,
                        "url": comment.get("url") or url,
                        "metadata": {
                            "subreddit": str(subreddit).replace("r/", ""),
                            "upvotes": comment.get("upVotes") or comment.get("score") or 0,
                            "scraper_engine": "apify",
                        }
                    }
                    existing_items.append(cdoc)
                    seen_ids.add(csource_id)
                    new_items += 1

print(f"✅ Added {new_items} new Reddit documents. Total raw Reddit items: {len(existing_items)}")

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(existing_items, f, indent=2, ensure_ascii=False)

if existing_items:
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["source_id", "source", "author", "timestamp", "title", "content", "url"])
        writer.writeheader()
        for it in existing_items:
            writer.writerow({
                "source_id": it.get("source_id", ""),
                "source": it.get("source", "reddit"),
                "author": it.get("author", ""),
                "timestamp": it.get("timestamp", ""),
                "title": it.get("title") or "",
                "content": it.get("content", ""),
                "url": it.get("url", ""),
            })
print(f"💾 Saved updated Reddit raw corpus to {json_path}")
