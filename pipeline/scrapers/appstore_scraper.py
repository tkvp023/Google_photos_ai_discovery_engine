"""
Apple App Store Scraper for Google Photos (iOS).
Extracts user reviews via the official iTunes customer reviews RSS/JSON API.
No heavy dependencies, no fragile packages — pure robust standard library + requests.
"""

import json
import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
import time
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

GOOGLE_PHOTOS_APP_ID = "962194608"

COUNTRIES = ["us", "gb", "ca", "au", "in"]
MAX_PAGES_PER_COUNTRY = 10  # Apple limits RSS customer reviews to max 10 pages (50 per page = 500 reviews)


def fetch_appstore_reviews(app_id: str = GOOGLE_PHOTOS_APP_ID, countries=None, max_pages: int = 10):
    if countries is None:
        countries = COUNTRIES

    raw_dir = Path("data/raw/appstore")
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_file = raw_dir / "batch_0001.json"

    existing_docs = []
    seen_ids = set()
    if out_file.exists():
        try:
            with open(out_file, "r", encoding="utf-8") as f:
                existing_docs = json.load(f)
                for doc in existing_docs:
                    seen_ids.add(doc.get("source_id"))
        except Exception:
            existing_docs = []

    print(f"🍎 Starting Apple App Store Scraper for Google Photos (App ID: {app_id})")
    print(f"🌍 Querying {len(countries)} storefronts: {', '.join(countries).upper()} (up to {max_pages} pages each)...")

    new_count = 0

    for country in countries:
        country_new = 0
        for page in range(1, max_pages + 1):
            url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortBy=mostRecent/json"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            try:
                with urllib.request.urlopen(req, timeout=15) as res:
                    data = json.loads(res.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code == 400 or e.code == 404:
                    # Reached end of available pages for this country
                    break
                print(f"  ⚠️ HTTP {e.code} on {country} page {page}: {e.reason}")
                break
            except Exception as e:
                print(f"  ⚠️ Error fetching {country} page {page}: {e}")
                break

            feed = data.get("feed", {})
            entries = feed.get("entry", [])
            if not entries or len(entries) <= 1:
                # Page 1 contains app metadata in entry 0; if length <= 1, no reviews
                break

            # Entry 0 is usually app info, entries 1+ are reviews
            review_entries = entries[1:] if len(entries) > 1 else []
            for entry in review_entries:
                try:
                    entry_id = entry.get("id", {}).get("label", "")
                    if not entry_id:
                        continue
                    source_id = f"appstore_{entry_id}"
                    if source_id in seen_ids:
                        continue

                    author = entry.get("author", {}).get("name", {}).get("label", "App Store User")
                    title = entry.get("title", {}).get("label", "").strip()
                    content = entry.get("content", {}).get("label", "").strip()
                    rating_val = entry.get("im:rating", {}).get("label")
                    rating = int(rating_val) if rating_val and rating_val.isdigit() else None
                    version = entry.get("im:version", {}).get("label", "")
                    updated = entry.get("updated", {}).get("label", datetime.now(timezone.utc).isoformat())
                    link = entry.get("link", {}).get("attributes", {}).get("href", "")

                    full_content = f"{title}\n\n{content}".strip() if (title and content) else (content or title)
                    if not full_content:
                        continue

                    doc = {
                        "source": "appstore",
                        "source_type": "primary",
                        "source_id": source_id,
                        "author": author,
                        "content": full_content,
                        "title": title if title else None,
                        "rating": rating,
                        "timestamp": updated,
                        "url": link,
                        "metadata": {
                            "app_version": version,
                            "country": country.upper(),
                            "rating": rating,
                            "scraper_engine": "itunes_rss",
                        }
                    }

                    existing_docs.append(doc)
                    seen_ids.add(source_id)
                    new_count += 1
                    country_new += 1
                except Exception as e:
                    continue

            time.sleep(0.3)  # Polite pause between pages

        print(f"  ✅ {country.upper()}: scraped {country_new} new reviews")

    print(f"\n🎉 Total new Apple App Store reviews collected: {new_count}")
    print(f"📦 Total corpus in {out_file}: {len(existing_docs)} documents")

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(existing_docs, f, indent=2, ensure_ascii=False)

    return existing_docs


if __name__ == "__main__":
    fetch_appstore_reviews()
