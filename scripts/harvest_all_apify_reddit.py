import os
import json
import csv
from datetime import datetime, timezone
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

client = ApifyClient(os.getenv("APIFY_API_TOKEN"))
runs = client.runs().list(limit=10)

all_items = []
seen_ids = set()

# Target directory
raw_dir = "data/raw/reddit"
os.makedirs(raw_dir, exist_ok=True)
json_path = os.path.join(raw_dir, "batch_0001.json")
csv_path = os.path.join(raw_dir, "reddit_reviews.csv")

# Load existing if available
if os.path.exists(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
            for item in existing:
                all_items.append(item)
                seen_ids.add(item.get("source_id", ""))
        print(f"Loaded {len(all_items)} existing items from {json_path}")
    except Exception as e:
        print(f"Error loading existing: {e}")

new_count = 0

for r in runs.items:
    ds_id = getattr(r, "default_dataset_id", None) or (r.get("defaultDatasetId") if isinstance(r, dict) else "")
    if not ds_id:
        continue
    
    print(f"Processing dataset {ds_id}...")
    try:
        for item in client.dataset(ds_id).iterate_items():
            # Extract content & title
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
            author = item.get("author") or item.get("username") or "[deleted]"
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

            all_items.append(doc)
            seen_ids.add(source_id)
            new_count += 1

            # Check for comments inside item
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
                    all_items.append(cdoc)
                    seen_ids.add(csource_id)
                    new_count += 1

    except Exception as e:
        print(f"Error processing dataset {ds_id}: {e}")

print(f"\nAdded {new_count} new Reddit documents. Total in raw corpus: {len(all_items)}")

# Save updated JSON
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(all_items, f, indent=2, ensure_ascii=False)
print(f"Saved {len(all_items)} documents to {json_path}")

# Save CSV
if all_items:
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["source_id", "source", "author", "timestamp", "title", "content", "url"])
        writer.writeheader()
        for it in all_items:
            writer.writerow({
                "source_id": it.get("source_id", ""),
                "source": it.get("source", "reddit"),
                "author": it.get("author", ""),
                "timestamp": it.get("timestamp", ""),
                "title": it.get("title") or "",
                "content": it.get("content", ""),
                "url": it.get("url", ""),
            })
    print(f"Saved CSV to {csv_path}")
