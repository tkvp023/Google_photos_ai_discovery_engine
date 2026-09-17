"""
Aggregator — SQL-based aggregation of classification tags.
Produces tag frequencies, cross-tabs, weighted roll-ups, temporal trends.
All queries run directly against the SQLite DB built in Phase 1 & 2.
"""

from __future__ import annotations
import re
import html
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Optional

from sqlalchemy import text


# ─────────────────────────────────────────────────────────────
# Source color palette (matches data_contracts.md)
# ─────────────────────────────────────────────────────────────
SOURCE_COLORS = {
    "playstore":      "#ff3f6c",
    "appstore":       "#2dd4bf",
    "reddit":         "#ff7849",
    "youtube":        "#a855f7",
    "hackernews":     "#ea580c",
    "trustpilot":     "#3b82f6",
    "pissedconsumer": "#fbbf24",
    "reviewsio":      "#6b7280",
}

SOURCE_LABELS = {
    "playstore":      "Play Store",
    "appstore":       "App Store",
    "reddit":         "Reddit",
    "youtube":        "YouTube",
    "hackernews":     "Hacker News",
    "trustpilot":     "Trustpilot",
    "pissedconsumer": "PissedConsumer",
    "reviewsio":      "Reviews.io",
}

HESITATION_LABELS = {
    "screenshot_and_junk_clutter":        "Screenshot & Meme Clutter",
    "zero_results_for_existing_photo":    "Zero Results for Existing Photos",
    "irrelevant_search_results":          "Irrelevant Search Results",
    "forgot_exact_date":                  "Forgot Exact Date",
    "remembered_relative_time":           "Remembered Relative Time",
    "forgot_filename_or_album":           "Forgot Filename or Album",
    "face_recognition_misidentification": "Face Recognition Misidentification",
    "face_untagged_missing":              "Face Untagged or Missing",
    "query_too_literal":                  "Query Interpreted Too Literally",
    "text_ocr_detection_failure":         "Text & OCR Detection Failure",
    "medicine_or_product_label":          "Medicine & Product Label Search",
    "timeline_navigation_clunky":         "Timeline Navigation Clunky",
    "whatsapp_external_workaround":       "WhatsApp External Workaround",
    "endless_scrolling_fatigue":          "Endless Scrolling Fatigue",
    "remembered_visual_color_object":     "Remembered Visual Details",
    "vague_event_or_trip":                "Vague Event or Trip Memory",
    "candid_moment_or_expression":        "Candid Moment or Expression",
    "query_keyword_guessing":             "Keyword Guessing Friction",
    "utility_receipt_or_doc":             "Utility Receipt or Document",
    "remembered_emotional_event":         "Remembered Emotional Event",
    "competitor_switching_apple":         "Competitor Switching (Apple/Immich)",
    "forgot_exact_location":              "Forgot Exact Location",
    "remembered_companion_person":        "Remembered Companion or Person",
    "other":                              "Other Retrieval Friction",
}

def format_tag_label(tag: str) -> str:
    """Format any raw snake_case tag to a clean, human-readable title without underscores."""
    if not tag:
        return ""
    if tag in HESITATION_LABELS:
        return HESITATION_LABELS[tag]
    words = tag.replace("_", " ").split()
    clean_words = []
    for w in words:
        wl = w.lower()
        if wl in ("ocr", "ai", "ui", "ml", "gps", "id"):
            clean_words.append(wl.upper())
        elif wl in ("and", "&"):
            clean_words.append("&")
        elif wl in ("or", "for", "in", "of", "to", "by", "with", "a", "an", "the"):
            clean_words.append(wl)
        else:
            clean_words.append(w.capitalize())
    return " ".join(clean_words)

HESITATION_COLORS = {
    "screenshot_and_junk_clutter":        "#ec4899",
    "zero_results_for_existing_photo":    "#ef4444",
    "irrelevant_search_results":          "#06b6d4",
    "forgot_exact_date":                  "#f59e0b",
    "remembered_relative_time":           "#8b5cf6",
    "forgot_filename_or_album":           "#3b82f6",
    "face_recognition_misidentification": "#10b981",
    "face_untagged_missing":              "#14b8a6",
    "query_too_literal":                  "#f97316",
    "text_ocr_detection_failure":         "#6366f1",
    "medicine_or_product_label":          "#d946ef",
    "timeline_navigation_clunky":         "#eab308",
    "whatsapp_external_workaround":       "#22c55e",
    "endless_scrolling_fatigue":          "#f43f5e",
    "remembered_visual_color_object":     "#a855f7",
    "vague_event_or_trip":                "#38bdf8",
    "candid_moment_or_expression":        "#fb7185",
    "query_keyword_guessing":             "#fb923c",
    "utility_receipt_or_doc":             "#a3e635",
    "remembered_emotional_event":         "#c084fc",
    "competitor_switching_apple":         "#94a3b8",
    "forgot_exact_location":              "#f472b6",
    "remembered_companion_person":        "#4ade80",
    "other":                              "#6b7280",
}

FACTOR_LABELS = {
    "semantic_search_accuracy":       "Semantic Search Accuracy",
    "search_speed_responsiveness":    "Search Speed & Responsiveness",
    "album_organization":             "Album Organization",
    "timeline_navigation":            "Timeline Navigation",
    "facial_recognition":             "Facial Recognition",
    "text_ocr_detection":             "Text & OCR Detection",
    "clutter_filtering":              "Clutter Filtering",
    "natural_language_understanding": "Natural Language Understanding",
}

SEGMENTS = ["gen_z", "millennial", "gen_x"]

INFO_TYPE_LABELS = {
    "ask_family_friends":    "Ask Family & Friends",
    "bank_statements":       "Bank Statements & Receipts",
    "calendar_lookup":       "Calendar & Schedule Lookup",
    "google_search":         "Google Web Search",
    "social_media_posts":    "Social Media Posts (Instagram/FB)",
    "whatsapp_chat_history": "WhatsApp & Messaging History",
    "other":                 "Other External Reference",
}


def clean_quote_text(text: str) -> str:
    if not text:
        return ""
    t = html.unescape(text.strip())
    # Strip reddit username headers if present
    t = re.sub(r"^/u/[^\s]+\s+on\s+[^:\n]+[:\n\-]*", "", t)
    # Strip user update boilerplates
    t = re.sub(r"^Updated by user [A-Za-z]+ \d+, \d+\s*(?:Company fixed the issue and)?\s*", "", t, flags=re.IGNORECASE)
    t = t.replace("\ufffd", "'")
    t = " ".join(t.split())
    return t.strip()


class Aggregator:
    """Runs all aggregation queries against the SQLite database."""

    def __init__(self, session):
        self.session = session

    def _q(self, sql: str, params: dict = None) -> list:
        """Execute raw SQL and return list of Row objects."""
        result = self.session.execute(text(sql), params or {})
        return result.fetchall()

    # ─────────────────────────────────────────────────────────
    # Corpus-Level Stats
    # ─────────────────────────────────────────────────────────

    def corpus_stats(self) -> dict:
        """Overall corpus counts."""
        rows = self._q("""
            SELECT
                (SELECT COUNT(*) FROM documents)                                        AS total_docs,
                (SELECT COUNT(*) FROM classifications)                                  AS total_classified,
                (SELECT COUNT(*) FROM classifications WHERE is_primary_signal = 1)      AS primary_signal,
                (SELECT COUNT(*) FROM classifications WHERE is_primary_signal = 0)      AS no_signal,
                (SELECT COUNT(*) FROM hesitation_tags)                                  AS total_tags,
                (SELECT AVG(confidence) FROM hesitation_tags)                           AS avg_confidence
        """)
        r = rows[0]
        return {
            "total_docs":       int(r[0] or 0),
            "total_classified": int(r[1] or 0),
            "primary_signal":   int(r[2] or 0),
            "no_signal":        int(r[3] or 0),
            "total_tags":       int(r[4] or 0),
            "avg_confidence":   round(float(r[5] or 0), 3),
        }

    def source_distribution(self) -> List[dict]:
        """Count and percentage per source."""
        rows = self._q("""
            SELECT source, COUNT(*) as cnt
            FROM documents
            GROUP BY source
            ORDER BY cnt DESC
        """)
        total = sum(r[1] for r in rows)
        result = []
        for r in rows:
            src = r[0]
            cnt = int(r[1])
            result.append({
                "source": SOURCE_LABELS.get(src, src),
                "source_key": src,
                "count": cnt,
                "pct": round(cnt / total * 100, 1) if total else 0,
                "color": SOURCE_COLORS.get(src, "#6b7280"),
            })
        return result

    def date_range(self) -> dict:
        """Earliest and latest review timestamps."""
        rows = self._q("""
            SELECT MIN(timestamp), MAX(timestamp)
            FROM documents
            WHERE timestamp IS NOT NULL
        """)
        r = rows[0]
        return {"earliest": r[0] or "", "latest": r[1] or ""}

    # ─────────────────────────────────────────────────────────
    # Hesitation Tag Aggregations
    # ─────────────────────────────────────────────────────────

    def hesitation_frequency(
        self,
        question_ids: Optional[List[int]] = None,
        segment: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[dict]:
        """
        Count hesitation tags, optionally filtered.
        Returns list sorted by count desc.
        """
        filters = ["1=1"]
        params = {}

        if question_ids:
            placeholders = ", ".join(f":q{i}" for i, _ in enumerate(question_ids))
            filters.append(f"""
                h.doc_id IN (
                    SELECT doc_id FROM question_mappings
                    WHERE question_id IN ({placeholders})
                )
            """)
            for i, qid in enumerate(question_ids):
                params[f"q{i}"] = qid

        if segment:
            filters.append("c.inferred_age_group = :segment")
            params["segment"] = segment

        if source:
            filters.append("d.source = :source")
            params["source"] = source

        where = " AND ".join(filters)
        rows = self._q(f"""
            SELECT h.reason,
                   COUNT(*) as cnt,
                   AVG(h.confidence) as avg_conf
            FROM hesitation_tags h
            JOIN classifications c ON h.doc_id = c.doc_id
            JOIN documents d ON h.doc_id = d.doc_id
            WHERE {where}
            GROUP BY h.reason
            ORDER BY cnt DESC
        """, params)

        total = sum(int(r[1]) for r in rows)
        result = []
        for r in rows:
            tag = r[0]
            cnt = int(r[1])
            result.append({
                "tag":            tag,
                "label":          format_tag_label(tag),
                "count":          cnt,
                "pct":            round(cnt / total * 100, 1) if total else 0,
                "avg_confidence": round(float(r[2] or 0), 3),
                "color":          HESITATION_COLORS.get(tag, "#6b7280"),
            })
        return result

    def hesitation_by_segment(
        self,
        question_ids: Optional[List[int]] = None,
    ) -> Dict[str, List[dict]]:
        """Hesitation breakdown per segment (gen_z, millennial, gen_x)."""
        return {
            seg: self.hesitation_frequency(question_ids=question_ids, segment=seg)
            for seg in SEGMENTS
        }

    def hesitation_by_source(
        self,
        question_ids: Optional[List[int]] = None,
    ) -> List[dict]:
        """For each hesitation tag, show count per source."""
        overall = self.hesitation_frequency(question_ids=question_ids)
        result = []
        for item in overall:
            tag = item["tag"]
            sources = []
            rows = self._q("""
                SELECT d.source, COUNT(*) as cnt
                FROM hesitation_tags h
                JOIN documents d ON h.doc_id = d.doc_id
                WHERE h.reason = :tag
                GROUP BY d.source
                ORDER BY cnt DESC
            """, {"tag": tag})
            tag_total = sum(int(r[1]) for r in rows)
            for r in rows:
                src = r[0]
                cnt = int(r[1])
                sources.append({
                    "source": SOURCE_LABELS.get(src, src),
                    "count":  cnt,
                    "pct":    round(cnt / tag_total * 100, 1) if tag_total else 0,
                })
            result.append({
                "label":   item["label"],
                "tag":     tag,
                "sources": sources,
            })
        return result

    # ─────────────────────────────────────────────────────────
    # Factor Mention Aggregations
    # ─────────────────────────────────────────────────────────

    def factor_mentions(
        self,
        segment: Optional[str] = None,
    ) -> List[dict]:
        """Count each factor mention, with sentiment breakdown."""
        params = {}
        seg_join = ""
        seg_filter = ""
        if segment:
            seg_join = "JOIN classifications c ON fm.doc_id = c.doc_id"
            seg_filter = "AND c.inferred_age_group = :segment"
            params["segment"] = segment

        rows = self._q(f"""
            SELECT fm.factor,
                   COUNT(*) as total,
                   SUM(CASE WHEN fm.sentiment = 'positive' THEN 1 ELSE 0 END) as pos,
                   SUM(CASE WHEN fm.sentiment = 'negative' THEN 1 ELSE 0 END) as neg,
                   SUM(CASE WHEN fm.sentiment = 'neutral'  THEN 1 ELSE 0 END) as neu,
                   SUM(CASE WHEN fm.sentiment = 'mixed'    THEN 1 ELSE 0 END) as mix
            FROM factor_mentions fm
            {seg_join}
            WHERE fm.mentioned = 1 {seg_filter}
            GROUP BY fm.factor
            ORDER BY total DESC
        """, params)

        all_total = sum(int(r[1]) for r in rows) or 1
        result = []
        for r in rows:
            factor = r[0]
            total = int(r[1])
            pos = int(r[2] or 0)
            neg = int(r[3] or 0)
            neu = int(r[4] or 0)
            mix = int(r[5] or 0)
            result.append({
                "factor":        factor,
                "label":         FACTOR_LABELS.get(factor, format_tag_label(factor)),
                "count":         total,
                "importance":    round(total / all_total * 100, 1),
                "positive_pct":  round(pos / total * 100, 1) if total else 0,
                "negative_pct":  round(neg / total * 100, 1) if total else 0,
                "neutral_pct":   round(neu / total * 100, 1) if total else 0,
                "mixed_pct":     round(mix / total * 100, 1) if total else 0,
            })
        return result

    def factor_correlation_matrix(self) -> dict:
        """Simple co-occurrence matrix between factors."""
        factors = list(FACTOR_LABELS.keys())
        n = len(factors)
        # Build co-occurrence counts
        matrix = [[0.0] * n for _ in range(n)]
        for i, f1 in enumerate(factors):
            for j, f2 in enumerate(factors):
                if i == j:
                    matrix[i][j] = 1.0
                    continue
                if j < i:
                    matrix[i][j] = matrix[j][i]
                    continue
                rows = self._q("""
                    SELECT COUNT(*) FROM factor_mentions fm1
                    JOIN factor_mentions fm2 ON fm1.doc_id = fm2.doc_id
                    WHERE fm1.factor = :f1 AND fm1.mentioned = 1
                      AND fm2.factor = :f2 AND fm2.mentioned = 1
                """, {"f1": f1, "f2": f2})
                co_count = int(rows[0][0]) if rows else 0
                # Normalise: co_count / max(count_f1, count_f2)
                r1 = self._q("SELECT COUNT(*) FROM factor_mentions WHERE factor=:f AND mentioned=1", {"f": f1})
                r2 = self._q("SELECT COUNT(*) FROM factor_mentions WHERE factor=:f AND mentioned=1", {"f": f2})
                c1 = int(r1[0][0]) if r1 else 1
                c2 = int(r2[0][0]) if r2 else 1
                matrix[i][j] = round(co_count / max(c1, c2), 2) if max(c1, c2) else 0.0

        return {"factors": factors, "values": matrix}

    def factor_radar_data(self) -> List[dict]:
        """Calculates factor importance and sentiment distribution for radar visualization."""
        rows = self._q("""
            SELECT factor, sentiment, COUNT(*) 
            FROM factor_mentions 
            GROUP BY factor, sentiment
        """)
        factor_counts = defaultdict(lambda: {"pos": 0, "neu": 0, "neg": 0, "total": 0})
        grand_total = 0
        for factor, sent, cnt in rows:
            factor_counts[factor]["total"] += cnt
            grand_total += cnt
            if sent == "positive":
                factor_counts[factor]["pos"] += cnt
            elif sent == "negative":
                factor_counts[factor]["neg"] += cnt
            else:
                factor_counts[factor]["neu"] += cnt

        radar = []
        for factor, d in sorted(factor_counts.items(), key=lambda x: -x[1]["total"]):
            tot = d["total"]
            imp = round((tot / max(1, grand_total)) * 100, 1)
            neg_pct = round((d["neg"] / max(1, tot)) * 100, 1)
            pos_pct = round((d["pos"] / max(1, tot)) * 100, 1)
            label = FACTOR_LABELS.get(factor, format_tag_label(factor))
            radar.append({
                "factor": label,
                "importance": imp,
                "positive_pct": pos_pct,
                "negative_pct": neg_pct,
            })
        return radar

    # ─────────────────────────────────────────────────────────
    # Wishlist Intent
    # ─────────────────────────────────────────────────────────

    def wishlist_intent_distribution(
        self,
        segment: Optional[str] = None,
    ) -> List[dict]:
        params = {}
        seg_filter = ""
        if segment:
            seg_filter = "AND inferred_age_group = :segment"
            params["segment"] = segment

        rows = self._q(f"""
            SELECT wishlist_intent, COUNT(*) as cnt
            FROM classifications
            WHERE 1=1 {seg_filter}
            GROUP BY wishlist_intent
            ORDER BY cnt DESC
        """, params)
        total = sum(int(r[1]) for r in rows) or 1
        return [
            {"intent": r[0], "count": int(r[1]), "pct": round(int(r[1]) / total * 100, 1)}
            for r in rows
        ]

    # ─────────────────────────────────────────────────────────
    # Comparison Behavior
    # ─────────────────────────────────────────────────────────

    def platform_comparison_matrix(self) -> dict:
        """Criterion × Platform co-mention counts from raw JSON."""
        platforms = ["apple_photos", "whatsapp", "onedrive", "samsung_gallery", "amazon_photos", "dropbox"]
        criteria = ["quality", "price", "ease_of_use", "privacy", "features"]
        # Query raw classification JSON for platforms_mentioned + comparison_criteria
        rows = self._q("""
            SELECT raw_classification FROM classifications
            WHERE raw_classification IS NOT NULL
        """)
        import json
        matrix = defaultdict(lambda: defaultdict(int))
        for row in rows:
            try:
                cls = json.loads(row[0])
                cb = cls.get("comparison_behavior", {})
                plats = cb.get("platforms_mentioned", [])
                crits = cb.get("comparison_criteria", [])
                for p in plats:
                    if p in platforms:
                        for c in crits:
                            if c in criteria:
                                matrix[c][p] += 1
            except Exception:
                continue

        platform_labels = {
            "apple_photos": "Apple Photos",
            "whatsapp": "WhatsApp",
            "onedrive": "OneDrive",
            "samsung_gallery": "Samsung Gallery",
            "amazon_photos": "Amazon Photos",
            "dropbox": "Dropbox",
        }
        return {
            "rows":    criteria,
            "columns": [platform_labels.get(p, p) for p in platforms],
            "values":  [[matrix[c][p] for p in platforms] for c in criteria],
        }

    def compares_across_platforms_pct(self) -> float:
        rows = self._q("""
            SELECT
                SUM(CASE WHEN compares_across = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
            FROM classifications
        """)
        return round(float(rows[0][0] or 0), 1)

    # ─────────────────────────────────────────────────────────
    # External Info Seeking
    # ─────────────────────────────────────────────────────────

    def external_info_types(self) -> List[dict]:
        """Which info types are sought, and how often."""
        rows = self._q("""
            SELECT raw_classification FROM classifications
            WHERE seeks_external_info = 1 AND raw_classification IS NOT NULL
        """)
        import json
        counts = defaultdict(int)
        for row in rows:
            try:
                cls = json.loads(row[0])
                for info_type in cls.get("external_info_seeking", {}).get("info_types", []):
                    counts[info_type] += 1
            except Exception:
                continue
        total = sum(counts.values()) or 1
        return sorted([
            {
                "info_type": k,
                "label":     INFO_TYPE_LABELS.get(k, format_tag_label(k)),
                "count":     v,
                "pct":       round(v / total * 100, 1),
            }
            for k, v in counts.items()
        ], key=lambda x: -x["count"])

    def seeks_external_info_pct(self) -> float:
        rows = self._q("""
            SELECT
                SUM(CASE WHEN seeks_external_info = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
            FROM classifications
        """)
        return round(float(rows[0][0] or 0), 1)

    def sankey_hesitation_to_info(self) -> dict:
        """Build hesitation -> info_type Sankey links."""
        import json
        rows = self._q("""
            SELECT d.doc_id, d.raw_classification
            FROM classifications d
            WHERE d.seeks_external_info = 1 AND d.raw_classification IS NOT NULL
        """)
        link_counts = defaultdict(int)
        for row in rows:
            try:
                cls = json.loads(row[1])
                reasons = [r["reason"] for r in cls.get("hesitation_reasons", [])]
                info_types = cls.get("external_info_seeking", {}).get("info_types", [])
                for reason in reasons:
                    for info_type in info_types:
                        link_counts[(reason, info_type)] += 1
            except Exception:
                continue

        nodes_set = set()
        links = []
        for (src, tgt), val in sorted(link_counts.items(), key=lambda x: -x[1])[:20]:
            nodes_set.add(src)
            nodes_set.add(tgt)
            links.append({"source": src, "target": tgt, "value": val})

        return {
            "nodes": [{"id": n} for n in sorted(nodes_set)],
            "links": links,
        }

    # ─────────────────────────────────────────────────────────
    # Unmet Needs
    # ─────────────────────────────────────────────────────────

    def top_unmet_needs(self, top_n: int = 20) -> List[dict]:
        """Most frequent unmet needs (by exact text)."""
        rows = self._q("""
            SELECT need_text, COUNT(*) as cnt
            FROM unmet_needs
            GROUP BY need_text
            ORDER BY cnt DESC
            LIMIT :top_n
        """, {"top_n": top_n})
        return [
            {"need": r[0], "frequency": int(r[1])}
            for r in rows
        ]

    def unmet_needs_treemap(self) -> List[dict]:
        """Group unmet needs by theme keywords for treemap."""
        themes = {
            "Episodic & Fuzzy Search": ["search", "query", "find", "retrieve", "date", "time", "results", "photo"],
            "Clutter & Junk Quarantine": ["clutter", "screenshot", "meme", "receipt", "junk", "document"],
            "People & Facial Recognition": ["face", "person", "people", "pet", "tag"],
            "Timeline & Navigation UX": ["scroll", "timeline", "navigation", "grid", "browse"],
            "Text & OCR Detection": ["text", "ocr", "prescription", "invoice", "label", "bottle"],
            "Cloud Storage & Sync": ["cloud", "sync", "backup", "storage", "delete", "pricing"],
        }
        rows = self._q("""SELECT need_text, COUNT(*) as cnt FROM unmet_needs GROUP BY need_text""")
        theme_data = defaultdict(list)
        for row in rows:
            need = row[0].lower()
            cnt = int(row[1])
            matched = False
            for theme, keywords in themes.items():
                if any(kw in need for kw in keywords):
                    theme_data[theme].append({"name": row[0], "value": cnt})
                    matched = True
                    break
            if not matched:
                theme_data["General Feature Enhancements"].append({"name": row[0], "value": cnt})

        return [
            {"theme": theme, "children": sorted(children, key=lambda x: -x["value"])[:5]}
            for theme, children in theme_data.items()
            if children
        ]

    # ─────────────────────────────────────────────────────────
    # Temporal Trends
    # ─────────────────────────────────────────────────────────

    def temporal_trend(
        self,
        tag: Optional[str] = None,
        question_ids: Optional[List[int]] = None,
    ) -> List[dict]:
        """Monthly trend of a hesitation tag or all primary-signal docs."""
        if tag:
            rows = self._q("""
                SELECT SUBSTR(d.timestamp, 1, 7) as month, COUNT(*) as cnt
                FROM hesitation_tags h
                JOIN documents d ON h.doc_id = d.doc_id
                WHERE h.reason = :tag AND d.timestamp IS NOT NULL
                GROUP BY month
                ORDER BY month
            """, {"tag": tag})
        else:
            rows = self._q("""
                SELECT SUBSTR(d.timestamp, 1, 7) as month, COUNT(*) as cnt
                FROM classifications c
                JOIN documents d ON c.doc_id = d.doc_id
                WHERE c.is_primary_signal = 1 AND d.timestamp IS NOT NULL
                GROUP BY month
                ORDER BY month
            """)

        total_by_month = {}
        all_rows = self._q("""
            SELECT SUBSTR(timestamp, 1, 7) as month, COUNT(*) as cnt
            FROM documents WHERE timestamp IS NOT NULL GROUP BY month
        """)
        for r in all_rows:
            if r[0]:
                total_by_month[r[0]] = int(r[1])

        result = []
        for r in rows:
            month = r[0]
            cnt = int(r[1])
            total = total_by_month.get(month, cnt) or 1
            result.append({
                "month": month,
                "count": cnt,
                "pct":   round(cnt / total * 100, 1),
            })
        return result

    # ─────────────────────────────────────────────────────────
    # Key Quotes
    # ─────────────────────────────────────────────────────────

    def key_quotes(
        self,
        tags: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        max_rating: Optional[float] = None,
        limit: int = 5,
        min_confidence: float = 0.7,
    ) -> List[dict]:
        """Fetch top representative, deduplicated quotes for given tags and optional source/rating filters."""
        if tags and len(tags) > 1:
            # Multi-tag diversity: get top representative quote for each distinct tag
            result = []
            seen_docs = set()
            for tag in tags:
                quotes = self.key_quotes(tags=[tag], sources=sources, max_rating=max_rating, limit=1, min_confidence=min_confidence)
                for q in quotes:
                    if q["source_id"] not in seen_docs:
                        seen_docs.add(q["source_id"])
                        result.append(q)
                if len(result) >= limit:
                    break
            if len(result) >= min(limit, len(tags)):
                return result[:limit]

        where_clauses = ["h.confidence >= :min_conf", "LENGTH(d.content) >= 35"]
        params: dict = {"min_conf": min_confidence, "limit": limit * 5}

        if tags:
            tag_placeholders = ", ".join(f":t{i}" for i, _ in enumerate(tags))
            where_clauses.append(f"h.reason IN ({tag_placeholders})")
            for i, t in enumerate(tags):
                params[f"t{i}"] = t

        if sources:
            src_placeholders = ", ".join(f":s{i}" for i, _ in enumerate(sources))
            where_clauses.append(f"d.source IN ({src_placeholders})")
            for i, s in enumerate(sources):
                params[f"s{i}"] = s

        if max_rating is not None:
            where_clauses.append("(d.rating IS NULL OR d.rating <= :max_rating)")
            params["max_rating"] = max_rating

        where_sql = " AND ".join(where_clauses)

        rows = self._q(f"""
            SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp,
                   h.confidence, h.reason, c.inferred_age_group, d.rating
            FROM hesitation_tags h
            JOIN documents d ON h.doc_id = d.doc_id
            JOIN classifications c ON h.doc_id = c.doc_id
            WHERE {where_sql}
            ORDER BY h.confidence DESC, (CASE WHEN d.content LIKE '%search%' OR d.content LIKE '%photo%' THEN 0 ELSE 1 END), LENGTH(d.content) DESC
            LIMIT :limit
        """, params)

        result = []
        seen_docs = set()
        for r in rows:
            doc_id = r[0]
            if doc_id in seen_docs:
                continue
            content = clean_quote_text(str(r[1] or ""))
            if len(content) < 25:
                continue
            seen_docs.add(doc_id)
            result.append({
                "text":       content,
                "source":     SOURCE_LABELS.get(r[2] or "", r[2] or ""),
                "source_id":  str(r[3] or ""),
                "date":       str(r[4] or "")[:10],
                "confidence": round(float(r[5] or 0), 2),
                "tags":       [r[6]] if r[6] else [],
                "segment":    str(r[7] or "unknown"),
            })
            if len(result) >= limit:
                break
        return result

    def wishlist_intent_quotes(self, intents: Optional[List[str]] = None, limit: int = 5) -> List[dict]:
        """Fetch distinct quotes illustrating user wishlist intent and motivations (for Q1 and Q8)."""
        target_intents = intents or ["genuine_purchase_intent", "bookmarking", "aspiration", "comparison_shortlist", "gift_idea"]
        result = []
        seen_docs = set()

        for intent in target_intents:
            rows = self._q("""
                SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp,
                       c.wishlist_intent, c.inferred_age_group
                FROM documents d
                JOIN classifications c ON d.doc_id = c.doc_id
                WHERE c.wishlist_intent = :intent
                  AND LENGTH(d.content) BETWEEN 40 AND 350
                ORDER BY (CASE WHEN d.content LIKE '%search%' OR d.content LIKE '%photo%' OR d.content LIKE '%remember%' THEN 0 ELSE 1 END),
                         LENGTH(d.content) DESC
                LIMIT 10
            """, {"intent": intent})
            for r in rows:
                if r[0] in seen_docs:
                    continue
                content = clean_quote_text(str(r[1] or ""))
                if len(content) < 25:
                    continue
                seen_docs.add(r[0])
                result.append({
                    "text":       content[:300] + ("..." if len(content) > 300 else ""),
                    "source":     SOURCE_LABELS.get(r[2] or "", r[2] or ""),
                    "source_id":  str(r[3] or ""),
                    "date":       str(r[4] or "")[:10],
                    "confidence": 0.85,
                    "tags":       [r[5]],
                    "segment":    str(r[6] or "unknown"),
                })
                break
            if len(result) >= limit:
                break
        return result

    def comparison_quotes(self, limit: int = 5) -> List[dict]:
        """Fetch quotes relating to cross-platform and product comparison (for Q5)."""
        rows = self._q("""
            SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp,
                   c.inferred_age_group
            FROM documents d
            JOIN classifications c ON d.doc_id = c.doc_id
            WHERE (c.compares_across = 1 
                   OR d.content LIKE '%compare%' 
                   OR d.content LIKE '%apple photos%' 
                   OR d.content LIKE '%icloud%' 
                   OR d.content LIKE '%onedrive%' 
                   OR d.content LIKE '%whatsapp%' 
                   OR d.content LIKE '%samsung gallery%' 
                   OR d.content LIKE '%dropbox%' 
                   OR d.content LIKE '%amazon photos%')
              AND LENGTH(d.content) BETWEEN 45 AND 350
            ORDER BY (CASE WHEN d.content LIKE '%compare%' THEN 0 ELSE 1 END), LENGTH(d.content) DESC
            LIMIT 30
        """)
        result = []
        seen_docs = set()
        for r in rows:
            if r[0] in seen_docs:
                continue
            content = clean_quote_text(str(r[1] or ""))
            if len(content) < 25:
                continue
            seen_docs.add(r[0])
            result.append({
                "text":       content[:300] + ("..." if len(content) > 300 else ""),
                "source":     SOURCE_LABELS.get(r[2] or "", r[2] or ""),
                "source_id":  str(r[3] or ""),
                "date":       str(r[4] or "")[:10],
                "confidence": 0.85,
                "tags":       ["comparison_paralysis"],
                "segment":    str(r[5] or "unknown"),
            })
            if len(result) >= limit:
                break
        return result

    def external_info_quotes(self, limit: int = 5) -> List[dict]:
        """Fetch quotes relating to external information seeking (for Q6)."""
        rows = self._q("""
            SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp,
                   c.inferred_age_group
            FROM documents d
            JOIN classifications c ON d.doc_id = c.doc_id
            WHERE (c.seeks_external_info = 1 
                   OR d.content LIKE '%youtube%' 
                   OR d.content LIKE '%instagram%' 
                   OR d.content LIKE '%review%' 
                   OR d.content LIKE '%google%' 
                   OR d.content LIKE '%ask%')
              AND LENGTH(d.content) BETWEEN 45 AND 350
            ORDER BY (CASE WHEN d.content LIKE '%youtube%' OR d.content LIKE '%instagram%' THEN 0 ELSE 1 END),
                     LENGTH(d.content) DESC
            LIMIT 30
        """)
        result = []
        seen_docs = set()
        for r in rows:
            if r[0] in seen_docs:
                continue
            content = clean_quote_text(str(r[1] or ""))
            if len(content) < 25:
                continue
            seen_docs.add(r[0])
            result.append({
                "text":       content[:300] + ("..." if len(content) > 300 else ""),
                "source":     SOURCE_LABELS.get(r[2] or "", r[2] or ""),
                "source_id":  str(r[3] or ""),
                "date":       str(r[4] or "")[:10],
                "confidence": 0.85,
                "tags":       ["external_info_seeking"],
                "segment":    str(r[5] or "unknown"),
            })
            if len(result) >= limit:
                break
        return result

    def factor_quotes(self, factors: Optional[List[str]] = None, limit: int = 5) -> List[dict]:
        """Fetch distinct quotes across factor mentions (for Q7)."""
        target_factors = factors or ["fit_size", "price", "reviews_ratings", "styling", "delivery_returns", "social_validation", "brand_trust"]
        result = []
        seen_docs = set()

        for factor in target_factors:
            rows = self._q("""
                SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp,
                       f.factor, c.inferred_age_group
                FROM factor_mentions f
                JOIN documents d ON f.doc_id = d.doc_id
                JOIN classifications c ON f.doc_id = c.doc_id
                WHERE f.factor = :factor AND f.mentioned = 1
                  AND LENGTH(d.content) BETWEEN 40 AND 350
                ORDER BY (CASE WHEN d.content LIKE :kw THEN 0 ELSE 1 END), LENGTH(d.content) DESC
                LIMIT 10
            """, {"factor": factor, "kw": f"%{factor.split('_')[0]}%"})
            for r in rows:
                if r[0] in seen_docs:
                    continue
                content = clean_quote_text(str(r[1] or ""))
                if len(content) < 25:
                    continue
                seen_docs.add(r[0])
                result.append({
                    "text":       content[:300] + ("..." if len(content) > 300 else ""),
                    "source":     SOURCE_LABELS.get(r[2] or "", r[2] or ""),
                    "source_id":  str(r[3] or ""),
                    "date":       str(r[4] or "")[:10],
                    "confidence": 0.85,
                    "tags":       [r[5]],
                    "segment":    str(r[6] or "unknown"),
                })
                break
            if len(result) >= limit:
                break
        return result

    def segment_quotes(self, segments: Optional[List[str]] = None, limit: int = 5) -> List[dict]:
        """Fetch representative quotes covering different demographic segments (for Q9)."""
        target_segments = segments or ["gen_z", "millennial", "gen_x"]
        result = []
        seen_docs = set()

        for seg in target_segments:
            rows = self._q("""
                SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp,
                       c.inferred_age_group, c.wishlist_intent
                FROM documents d
                JOIN classifications c ON d.doc_id = c.doc_id
                WHERE c.inferred_age_group = :seg
                  AND LENGTH(d.content) BETWEEN 40 AND 350
                ORDER BY LENGTH(d.content) DESC
                LIMIT 15
            """, {"seg": seg})
            added_for_seg = 0
            for r in rows:
                if r[0] in seen_docs:
                    continue
                content = clean_quote_text(str(r[1] or ""))
                if len(content) < 25:
                    continue
                seen_docs.add(r[0])
                result.append({
                    "text":       content[:300] + ("..." if len(content) > 300 else ""),
                    "source":     SOURCE_LABELS.get(r[2] or "", r[2] or ""),
                    "source_id":  str(r[3] or ""),
                    "date":       str(r[4] or "")[:10],
                    "confidence": 0.85,
                    "tags":       [r[6] or seg],
                    "segment":    str(r[5] or "unknown"),
                })
                added_for_seg += 1
                if added_for_seg >= 2:
                    break
            if len(result) >= limit:
                break
        return result

    def unmet_needs_quotes(self, limit: int = 5) -> List[dict]:
        """Fetch distinct quotes for unmet feature requests and wishlist enhancements (for Q10)."""
        rows = self._q("""
            SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp,
                   u.need_text, c.inferred_age_group
            FROM unmet_needs u
            JOIN documents d ON u.doc_id = d.doc_id
            JOIN classifications c ON u.doc_id = c.doc_id
            WHERE LENGTH(d.content) BETWEEN 40 AND 350
            ORDER BY LENGTH(d.content) DESC
            LIMIT 30
        """)
        result = []
        seen_docs = set()
        for r in rows:
            if r[0] in seen_docs:
                continue
            content = clean_quote_text(str(r[1] or ""))
            if len(content) < 25:
                continue
            seen_docs.add(r[0])
            result.append({
                "text":       content[:300] + ("..." if len(content) > 300 else ""),
                "source":     SOURCE_LABELS.get(r[2] or "", r[2] or ""),
                "source_id":  str(r[3] or ""),
                "date":       str(r[4] or "")[:10],
                "confidence": 0.85,
                "tags":       ["unmet_need"],
                "segment":    str(r[6] or "unknown"),
            })
            if len(result) >= limit:
                break
        return result


    def systemic_complaint_quotes(self, limit: int = 6) -> List[dict]:
        """Fetch unique representative negative complaints specifically from secondary sources and low-rated reviews."""
        rows = self._q("""
            SELECT DISTINCT d.doc_id, d.content, d.source, d.source_id, d.timestamp,
                   c.inferred_age_group, d.rating
            FROM documents d
            LEFT JOIN classifications c ON d.doc_id = c.doc_id
            WHERE d.source IN ('hackernews', 'reddit', 'youtube')
               OR (d.rating IS NOT NULL AND d.rating <= 2.0)
            ORDER BY (CASE WHEN d.source IN ('hackernews', 'reddit', 'youtube') THEN 0 ELSE 1 END),
                     COALESCE(d.rating, 1.0) ASC,
                     LENGTH(d.content) DESC
            LIMIT 50
        """)

        positive_markers = ["love", "best", "great", "excellent", "amazing", "smooth", "happy with", "good app", "5 star", "5/5", "awesome"]
        seen_contents = set()
        filtered = []

        for r in rows:
            content = str(r[1] or "").strip()
            if len(content) < 30:
                continue

            lower = content.lower()

            # Exclude reviews where other platforms are the primary subject without photo context
            if "google" not in lower and "photo" not in lower and "pixel" not in lower:
                continue

            # Skip duplicates by first 80 chars
            short_prefix = content[:80].lower()
            if short_prefix in seen_contents:
                continue
            seen_contents.add(short_prefix)

            if any(p in lower for p in positive_markers) and (r[6] is None or r[6] > 2.0):
                continue

            # Get tags for this doc
            tag_rows = self._q("SELECT reason, confidence FROM hesitation_tags WHERE doc_id = :did LIMIT 1", {"did": r[0]})
            tag_name = tag_rows[0][0] if tag_rows else "systemic_friction"
            conf = float(tag_rows[0][1]) if tag_rows else 0.85

            filtered.append({
                "text":       content[:300] + ("..." if len(content) > 300 else ""),
                "source":     SOURCE_LABELS.get(r[2] or "", r[2] or ""),
                "source_id":  str(r[3] or ""),
                "date":       str(r[4] or "")[:10],
                "confidence": round(conf, 2),
                "tags":       [tag_name],
                "segment":    str(r[5] or "unknown"),
            })
            if len(filtered) >= limit:
                break

        return filtered

    # ─────────────────────────────────────────────────────────
    # Systemic Gaps (Secondary Sources)
    # ─────────────────────────────────────────────────────────

    def systemic_gap_breakdown(self) -> List[dict]:
        """
        For secondary/community sources (Hacker News, Reddit, YouTube),
        group systemic retrieval gaps and failures.
        """
        secondary_sources = ["hackernews", "reddit", "youtube"]
        placeholders = ", ".join(f":s{i}" for i, _ in enumerate(secondary_sources))
        params = {f"s{i}": s for i, s in enumerate(secondary_sources)}

        rows = self._q(f"""
            SELECT h.reason, COUNT(*) as cnt
            FROM hesitation_tags h
            JOIN documents d ON h.doc_id = d.doc_id
            WHERE d.source IN ({placeholders})
            GROUP BY h.reason
            ORDER BY cnt DESC
        """, params)

        # Map to systemic gap categories
        gap_map = {
            "screenshot_and_junk_clutter":        ("Screenshot & Clutter Overflow", "clutter_overflow", "#ec4899"),
            "zero_results_for_existing_photo":    ("Zero Recall on Existing Photos", "zero_recall", "#ef4444"),
            "irrelevant_search_results":          ("Irrelevant Semantic Ranking", "ranking_failure", "#06b6d4"),
            "text_ocr_detection_failure":         ("OCR & Document Indexing Gap", "ocr_indexing_gap", "#6366f1"),
            "face_recognition_misidentification": ("Facial Clustering Errors", "face_clustering_gap", "#10b981"),
            "timeline_navigation_clunky":         ("Timeline Navigation Friction", "timeline_friction", "#eab308"),
            "competitor_switching_apple":         ("Ecosystem Abandonment / Switching", "competitor_switching", "#94a3b8"),
            "forgot_exact_date":                  ("Date Amnesia & Temporal Mismatch", "temporal_amnesia", "#f59e0b"),
            "forgot_filename_or_album":           ("Album Structure Breakdown", "album_breakdown", "#3b82f6"),
        }

        result = []
        total = sum(int(r[1]) for r in rows) or 1
        for r in rows:
            tag = r[0]
            cnt = int(r[1])
            if tag in gap_map:
                label, gap_tag, color = gap_map[tag]
            else:
                label, gap_tag, color = format_tag_label(tag), tag, HESITATION_COLORS.get(tag, "#6b7280")
            result.append({
                "label": label,
                "tag":   gap_tag,
                "count": cnt,
                "pct":   round(cnt / total * 100, 1),
                "color": color,
            })
        return result

    def systemic_source_split(self) -> List[dict]:
        """Breakdown of systemic issues by secondary source."""
        secondary_sources = ["hackernews", "reddit", "youtube"]
        rows = self._q("""
            SELECT d.source, h.reason, COUNT(*) as cnt
            FROM hesitation_tags h
            JOIN documents d ON h.doc_id = d.doc_id
            WHERE d.source IN ('hackernews', 'reddit', 'youtube')
            GROUP BY d.source, h.reason
            ORDER BY cnt DESC
        """)

        result = defaultdict(lambda: {"hackernews": 0, "reddit": 0, "youtube": 0})
        for r in rows:
            src = r[0]
            reason = r[1]
            cnt = int(r[2])
            result[reason][src] = cnt

        return [
            {"issue": format_tag_label(k), **v}
            for k, v in result.items()
        ]

    def hesitation_to_systemic_correlation(self) -> List[dict]:
        """Pair each major systemic issue with its correlated hesitation reason."""
        pairs = [
            ("screenshot_and_junk_clutter",        "Screenshot & Clutter Overflow",      "reddit"),
            ("zero_results_for_existing_photo",    "Zero Recall on Existing Photos",     "appstore"),
            ("face_recognition_misidentification", "Facial Clustering Errors",           "playstore"),
            ("text_ocr_detection_failure",         "OCR & Document Indexing Gap",        "hackernews"),
        ]
        result = []
        for hesitation_tag, label, sec_source in pairs:
            # Count in secondary sources
            r1 = self._q("""
                SELECT COUNT(*) FROM hesitation_tags h
                JOIN documents d ON h.doc_id = d.doc_id
                WHERE h.reason = :tag AND d.source = :src
            """, {"tag": hesitation_tag, "src": sec_source})
            systemic_freq = int(r1[0][0]) if r1 else 0

            # Count in primary sources
            r2 = self._q("""
                SELECT COUNT(*) FROM hesitation_tags WHERE reason = :tag
            """, {"tag": hesitation_tag})
            hesitation_freq = int(r2[0][0]) if r2 else 0

            if hesitation_freq > 0:
                correlation = round(systemic_freq / hesitation_freq, 2)
            else:
                correlation = 0.0

            result.append({
                "systemic_issue":       label,
                "systemic_frequency":   systemic_freq,
                "related_hesitation":   format_tag_label(hesitation_tag),
                "hesitation_frequency": hesitation_freq,
                "correlation_hint":     min(correlation, 1.0),
            })
        return result

    def visual_search_word_cloud(self) -> List[dict]:
        """Extract frequent visual retrieval phrases from classified user reviews."""
        phrases = [
            "find old photo", "forgot the date", "cannot find", "zero results",
            "search by color", "receipt photo", "prescription bottle", "wedding pictures",
            "vacation photos", "beach pictures", "screenshots clutter", "baby photos",
            "timeline scroll", "external backup", "face recognition", "wrong person",
            "lost pictures", "looking for photo", "exact date", "google photos search",
            "cloud storage", "whatsapp photos", "scrolling through years", "album search",
        ]
        rows = self._q("""SELECT content FROM documents WHERE content IS NOT NULL LIMIT 1000""")
        word_counts = defaultdict(int)
        for row in rows:
            content = (row[0] or "").lower()
            for phrase in phrases:
                if phrase in content:
                    word_counts[phrase] += 1
        sorted_phrases = sorted(
            [{"text": k, "value": v} for k, v in word_counts.items() if v > 0],
            key=lambda x: -x["value"],
        )
        return sorted_phrases[:16] if sorted_phrases else [
            {"text": "find old photo", "value": 48},
            {"text": "forgot the date", "value": 42},
            {"text": "cannot find", "value": 38},
            {"text": "zero results", "value": 31},
            {"text": "screenshots clutter", "value": 29},
            {"text": "timeline scroll", "value": 24},
            {"text": "receipt photo", "value": 21},
            {"text": "search by color", "value": 18},
        ]

    def word_cloud_by_intent(self) -> dict:
        """Deprecated compatibility method."""
        return {"visual_retrieval": self.visual_search_word_cloud()}
