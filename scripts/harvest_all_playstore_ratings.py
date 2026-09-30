"""
High-Yield Play Store Review Harvester for Search-Based Retrieval.
Iterates across all 5 star ratings (1, 2, 3, 4, 5), sort modes, and English-speaking countries.
Extracts authentic user search and visual retrieval friction.
Appends directly to data/search_only_corpus/raw/playstore_raw.json without duplicates.
"""

import os
import sys
import json
import time
from pathlib import Path
from google_play_scraper import reviews, Sort

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = PROJECT_ROOT / "data" / "search_only_corpus" / "raw" / "playstore_raw.json"

def main():
    print("=" * 65)
    print("📲 SCALED PLAY STORE STAR-RATING HARVESTER")
    print("=" * 65)

    existing_docs = []
    seen_ids = set()
    if RAW_PATH.exists():
        with open(RAW_PATH, "r", encoding="utf-8") as f:
            existing_docs = json.load(f)
            for d in existing_docs:
                sid = d.get("source_id")
                if sid:
                    seen_ids.add(str(sid))
    print(f"📦 Existing Play Store records on disk: {len(existing_docs):,}")

    countries = ["us", "in", "gb", "ca", "au", "ie", "nz", "ph", "sg", "za"]
    scores = [1, 2, 3, 4, 5]
    sort_modes = [Sort.NEWEST, Sort.MOST_RELEVANT]

    new_docs = []
    start_time = time.time()
    target_new = 15000  # collect up to 15,000 brand new reviews

    for score in scores:
        if len(new_docs) >= target_new:
            break
        for country in countries:
            if len(new_docs) >= target_new:
                break
            for sort_mode in sort_modes:
                if len(new_docs) >= target_new:
                    break

                sort_name = "NEWEST" if sort_mode == Sort.NEWEST else "MOST_RELEVANT"
                print(f"🌟 Score={score}⭐ | Country='{country.upper()}' | Sort={sort_name}...")
                continuation_token = None
                consecutive_empty = 0
                consecutive_zero_new = 0

                for page in range(10):  # up to 10 pages per cell (~2,000 reviews)
                    try:
                        res, continuation_token = reviews(
                            "com.google.android.apps.photos",
                            lang="en",
                            country=country,
                            sort=sort_mode,
                            filter_score_with=score,
                            count=199,
                            continuation_token=continuation_token
                        )
                    except Exception as e:
                        print(f"  ⚠️ Error on {country} score={score} page {page + 1}: {e}")
                        break

                    if not res:
                        consecutive_empty += 1
                        if consecutive_empty >= 2:
                            break
                        continue
                    consecutive_empty = 0

                    page_new = 0
                    for r in res:
                        rid = r.get("reviewId")
                        if not rid or rid in seen_ids:
                            continue
                        seen_ids.add(rid)

                        content = (r.get("content") or "").strip()
                        if not content or len(content) < 8:
                            continue

                        dt = r.get("at")
                        dt_str = dt.isoformat() if hasattr(dt, "isoformat") else str(dt or "")

                        doc = {
                            "doc_id": f"playstore_{rid}",
                            "source": "playstore",
                            "source_type": "primary",
                            "source_id": rid,
                            "author": r.get("userName") or "PlayStoreUser",
                            "content": content,
                            "title": None,
                            "rating": r.get("score"),
                            "created_at": dt_str,
                            "url": f"https://play.google.com/store/apps/details?id=com.google.android.apps.photos&reviewId={rid}",
                            "metadata": {
                                "thumbsUpCount": r.get("thumbsUpCount", 0),
                                "country": country,
                                "sort_mode": sort_name,
                                "filter_score": score,
                            }
                        }
                        new_docs.append(doc)
                        existing_docs.append(doc)
                        page_new += 1

                    print(f"  Page {page + 1:2}: +{page_new:3} new reviews (Total new: {len(new_docs):,})")

                    if page_new == 0:
                        consecutive_zero_new += 1
                        if consecutive_zero_new >= 2:
                            print(f"    ⏩ Cell already mined. Skipping to next.")
                            break
                    else:
                        consecutive_zero_new = 0

                    if not continuation_token:
                        break
                    time.sleep(0.4)

                # Save checkpoint to raw file after every cell
                with open(RAW_PATH, "w", encoding="utf-8") as f:
                    json.dump(existing_docs, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start_time
    print("\n" + "=" * 65)
    print(f"🎉 PLAY STORE STAR-RATING HARVEST COMPLETE in {elapsed:.1f}s!")
    print(f"  • New unique reviews added: {len(new_docs):,}")
    print(f"  • Total Play Store pool:    {len(existing_docs):,}")
    print(f"  • Saved to: {RAW_PATH}")
    print("=" * 65)

if __name__ == "__main__":
    main()
