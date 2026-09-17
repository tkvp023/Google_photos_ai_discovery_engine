"""
Google Play Store scraper for Google Photos reviews.
Uses google-play-scraper library (unofficial, no auth required).
Iterates across multiple regions, sort modes (Most Relevant + Newest), and friction scores (1, 2, 3 stars)
for maximum depth of authentic user retrieval pain points.
"""

from typing import List, Optional

from pipeline.scrapers.base_scraper import BaseScraper, ScrapedDocument, anonymize_username, with_retry
from pipeline.scrapers.config import PLAYSTORE_CONFIG


class PlayStoreScraper(BaseScraper):

    @property
    def source_name(self) -> str:
        return "playstore"

    @with_retry
    def _fetch_reviews_batch(self, country: str, sort, filter_score=None, continuation_token=None, count=200):
        """Fetch a single batch of reviews from Google Play Store."""
        from google_play_scraper import reviews

        kwargs = {
            "app_id": self.config.get("app_id", "com.google.android.apps.photos"),
            "lang": "en",
            "country": country,
            "sort": sort,
            "count": count,
            "continuation_token": continuation_token,
        }
        if filter_score is not None:
            kwargs["filter_score_with"] = filter_score

        result, token = reviews(**kwargs)
        return result, token

    def scrape(self, limit: Optional[int] = None) -> List[ScrapedDocument]:
        from google_play_scraper import Sort
        from tqdm import tqdm

        target = limit or self.config.get("count", 5000)
        app_id = self.config.get("app_id", "com.google.android.apps.photos")

        # Load existing source IDs to avoid re-scraping
        existing_ids = self.get_existing_source_ids()
        print(f"  📦 Found {len(existing_ids)} existing docs on disk")

        documents: List[ScrapedDocument] = []
        
        # High-signal English-speaking markets for Google Photos
        regions = ["us", "gb", "ca", "au", "in"]
        # Both Most Relevant (deepest friction essays) and Newest (recent updates/bugs)
        sort_modes = [Sort.MOST_RELEVANT, Sort.NEWEST]
        # Target friction star ratings first (1, 2, 3 stars), then all (None)
        score_filters = [1, 2, 3, None]

        pbar = tqdm(total=target, desc="  Play Store", unit="reviews")
        pbar.update(min(len(existing_ids), target))

        for score in score_filters:
            if len(documents) + len(existing_ids) >= target:
                break

            for sort in sort_modes:
                if len(documents) + len(existing_ids) >= target:
                    break

                for country in regions:
                    if len(documents) + len(existing_ids) >= target:
                        break

                    continuation_token = None
                    empty_streak = 0
                    max_batches = 8  # up to 1,600 reviews per cell

                    for batch_idx in range(max_batches):
                        if len(documents) + len(existing_ids) >= target:
                            break

                        try:
                            batch_count = min(200, target - (len(documents) + len(existing_ids)))
                            if batch_count <= 0:
                                break

                            result, continuation_token = self._fetch_reviews_batch(
                                country=country,
                                sort=sort,
                                filter_score=score,
                                continuation_token=continuation_token,
                                count=batch_count,
                            )

                            if not result:
                                empty_streak += 1
                                if empty_streak >= 2:
                                    break
                                continue

                            empty_streak = 0
                            added_in_batch = 0

                            for review in result:
                                review_id = review.get("reviewId", "")
                                if not review_id or review_id in existing_ids:
                                    continue

                                doc = ScrapedDocument(
                                    source="playstore",
                                    source_type="primary",
                                    source_id=review_id,
                                    author=anonymize_username(review.get("userName", "")),
                                    content=review.get("content", ""),
                                    title=None,
                                    rating=review.get("score"),
                                    timestamp=review.get("at", "").isoformat() if review.get("at") else None,
                                    url=f"https://play.google.com/store/apps/details?id={app_id}&reviewId={review_id}",
                                    metadata={
                                        "app_version": review.get("appVersion"),
                                        "thumbs_up": review.get("thumbsUpCount", 0),
                                        "country": country,
                                        "sort": sort.name,
                                        "filter_score": score,
                                        "reply_content": review.get("replyContent"),
                                        "replied_at": review.get("repliedAt", "").isoformat() if review.get("repliedAt") else None,
                                    },
                                )
                                documents.append(doc)
                                existing_ids.add(review_id)
                                added_in_batch += 1

                            pbar.update(added_in_batch)

                            if continuation_token is None or added_in_batch == 0:
                                break

                            self.rate_limit_sleep(0.2)

                        except Exception as e:
                            print(f"  ⚠️ Error in {country}/{sort.name}/score={score}: {e}")
                            break

        pbar.close()
        return documents
