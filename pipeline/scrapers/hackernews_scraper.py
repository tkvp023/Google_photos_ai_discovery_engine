"""
Hacker News Scraper for Google Photos technical critiques & architectural discussions.
Uses Algolia HN Search API (free, open, high rate limit).
"""

import sys
import os
import re
import html
import requests
from typing import List, Optional
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, ".")
from pipeline.scrapers.base_scraper import BaseScraper, ScrapedDocument, anonymize_username


class HackerNewsScraper(BaseScraper):

    def __init__(self, config: dict = None, data_dir=None):
        super().__init__(config or {}, data_dir=data_dir)

    @property
    def source_name(self) -> str:
        return "hackernews"

    def scrape(self, limit: Optional[int] = None) -> List[ScrapedDocument]:
        queries = [
            '"google photos" search',
            '"google photos" find photo',
            '"google photos" face recognition',
            '"google photos" "ask photos"',
            '"google photos" clutter',
            '"google photos" immich',
            '"google photos" backup duplicate',
            '"google photos" search broken',
            '"google photos" timeline scroll',
        ]

        documents = []
        seen_ids = set(self.get_existing_source_ids())
        target_limit = limit or 500

        print(f"\n  📡 Scraping Hacker News via Algolia API across {len(queries)} queries...")

        base_url = "https://hn.algolia.com/api/v1/search"

        for q in queries:
            if len(documents) >= target_limit:
                break

            for page in range(3):
                try:
                    params = {
                        "query": q,
                        "tags": "comment",
                        "hitsPerPage": 50,
                        "page": page,
                    }
                    resp = requests.get(base_url, params=params, timeout=15)
                    if resp.status_code != 200:
                        break

                    hits = resp.json().get("hits", [])
                    if not hits:
                        break

                    for h in hits:
                        object_id = str(h.get("objectID") or "")
                        if not object_id or object_id in seen_ids:
                            continue

                        raw_html = h.get("comment_text", "")
                        if not raw_html:
                            continue

                        # Clean HTML
                        text = re.sub(r"<[^>]+>", " ", raw_html)
                        text = html.unescape(text)
                        text = re.sub(r"\s+", " ", text).strip()

                        # Must have meaningful length and mention google photos or photos
                        if len(text) < 40:
                            continue
                        if "photo" not in text.lower():
                            continue

                        author = h.get("author") or "anonymous"
                        created_at = h.get("created_at") or datetime.now(timezone.utc).isoformat()
                        story_title = h.get("story_title") or "Google Photos Discussion"
                        story_url = h.get("story_url") or f"https://news.ycombinator.com/item?id={object_id}"

                        doc = ScrapedDocument(
                            source="hackernews",
                            source_type="primary",
                            source_id=f"hn_{object_id}",
                            author=anonymize_username(author),
                            content=text,
                            title=story_title,
                            rating=None,
                            timestamp=created_at,
                            url=f"https://news.ycombinator.com/item?id={object_id}",
                            metadata={
                                "story_title": story_title,
                                "story_id": h.get("story_id"),
                                "points": h.get("points", 0),
                            }
                        )

                        documents.append(doc)
                        seen_ids.add(object_id)

                        if len(documents) >= target_limit:
                            break

                    self.rate_limit_sleep(0.3)

                except Exception as e:
                    print(f"    ⚠️ HN Query '{q}' page {page} error: {e}")
                    break

        print(f"  ✅ Extracted {len(documents)} Hacker News discussions.")
        return documents


if __name__ == "__main__":
    scraper = HackerNewsScraper()
    scraper.run(limit=250)
