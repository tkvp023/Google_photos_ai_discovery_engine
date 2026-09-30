"""
Reclassify the 640 candidate documents that temporarily fell back to out_of_scope
due to Google's server network timeouts during the previous run.
Uses gemini-3.1-flash-lite (which is active and responding with HTTP 200).
Strict integrity gate: 100% character-for-character quote grounding.
Directly updates classification_checkpoint.json and re-populates search_only_corpus.sqlite.
"""

import os
import sys
import json
import time
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from scripts.build_search_only_corpus import (
    CHECKPOINT_FILE,
    DB_PATH,
    CORPUS_DIR,
    SYSTEM_PROMPT,
    load_all_raw_documents,
    call_gemini_api,
    is_quote_grounded,
    init_corpus_db,
)

MODELS = ["gemini-3.1-flash-lite", "gemini-3.1-flash-lite-preview"]

def classify_batch(batch_docs, timeout: int = 15):
    user_prompt = "Classify each of the following documents according to the strict system instructions:\n\n"
    for d in batch_docs:
        content_clean = d["content"].strip().replace("\r", "")
        snippet = content_clean[:900]
        user_prompt += f"--- DOCUMENT doc_id: \"{d['doc_id']}\" (Platform: {d.get('source', '')}) ---\n{snippet}\n\n"

    last_err = None
    for model_name in MODELS:
        for attempt in range(2):
            try:
                resp = call_gemini_api(model_name, user_prompt, timeout=timeout)
                if resp.status_code == 200:
                    res_data = resp.json()
                    out_text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if out_text.startswith("```json"):
                        out_text = out_text[7:]
                    if out_text.startswith("```"):
                        out_text = out_text[3:]
                    if out_text.endswith("```"):
                        out_text = out_text[:-3]
                    out_text = out_text.strip()
                    data = json.loads(out_text)
                    if isinstance(data, dict) and "results" in data:
                        return data["results"], model_name, None
                    elif isinstance(data, list):
                        return data, model_name, None
                    else:
                        return [], model_name, f"Unexpected JSON format: {type(data)}"
                elif resp.status_code == 429:
                    last_err = f"429 rate limit on {model_name}"
                    time.sleep(3)
                else:
                    last_err = f"HTTP {resp.status_code} on {model_name}: {resp.text[:120]}"
            except Exception as e:
                last_err = f"Exception on {model_name}: {e}"
                time.sleep(1)

    return [], None, last_err

def main():
    print("=" * 65)
    print("🚀 RECLASSIFYING FALLBACK CANDIDATES WITH GEMINI-3.1-FLASH-LITE")
    print("   Goal: Reach 1,500+ Verified Search Documents with 100% Integrity")
    print("=" * 65)

    with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
        classifications = json.load(f)

    raw_docs = load_all_raw_documents()
    raw_map = {d["doc_id"]: d for d in raw_docs}

    fallback_doc_ids = [
        k for k, v in classifications.items()
        if "safely excluded to protect corpus precision" in v.get("reason", "")
    ]

    print(f"📦 Found {len(fallback_doc_ids):,} candidate docs that experienced network timeout fallbacks.")

    candidates_to_process = [raw_map[did] for did in fallback_doc_ids if did in raw_map]
    print(f"🎯 Successfully matched {len(candidates_to_process):,} raw candidate documents.")

    BATCH_SIZE = 16
    batches = [candidates_to_process[i:i + BATCH_SIZE] for i in range(0, len(candidates_to_process), BATCH_SIZE)]
    print(f"⚡ Processing across {len(batches)} batches with {MODELS}...")

    in_scope_added = 0
    now_str = datetime.now(timezone.utc).isoformat()

    for b_idx, batch in enumerate(batches):
        results, model_used, err = classify_batch(batch)
        if err or not results:
            print(f"  ⚠️ Batch {b_idx + 1}/{len(batches)} error: {err}. Retrying in 3s...")
            time.sleep(3)
            results, model_used, err = classify_batch(batch, timeout=20)

        if results:
            res_map = {r.get("doc_id"): r for r in results}
            for d in batch:
                r = res_map.get(d["doc_id"])
                if r:
                    try:
                        conf = float(r.get("confidence", 0.85))
                    except (ValueError, TypeError):
                        conf = 0.85
                    stages = r.get("stages_evidenced", [])
                    if not isinstance(stages, list):
                        stages = [str(stages)] if stages else []
                    
                    cls_val = r.get("classification", "out_of_scope")
                    if cls_val == "in_scope":
                        in_scope_added += 1

                    classifications[d["doc_id"]] = {
                        "doc_id": d["doc_id"],
                        "classification": cls_val,
                        "stages_evidenced": stages,
                        "search_mode": r.get("search_mode", "unspecified_search"),
                        "verbatim_quote": str(r.get("verbatim_quote", "") or ""),
                        "confidence": conf,
                        "reason": str(r.get("reason", "") or ""),
                        "model_used": model_used or "gemini-3.1-flash-lite",
                        "classified_at": now_str,
                    }
        else:
            print(f"  ⚠️ Batch {b_idx + 1} could not be classified ({err}). Preserving safe fallback.")

        # Live checkpoint save
        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            json.dump(classifications, f)

        total_in_scope = sum(1 for v in classifications.values() if v.get("classification") == "in_scope")
        print(f"  Batch {b_idx + 1:2}/{len(batches)} | +{in_scope_added:3} new in-scope | Total In-Scope: {total_in_scope:,}", flush=True)
        time.sleep(1.5)

    # ─────────────────────────────────────────────────────────────
    # Re-populate SQLite DB & Enforce 100% Quote Grounding Gate
    # ─────────────────────────────────────────────────────────────
    print("\n💾 Populating data/search_only_corpus/search_only_corpus.sqlite...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS search_only_documents")
    c.execute("DROP TABLE IF EXISTS flow_stages_evidenced")
    c.execute("DROP TABLE IF EXISTS collection_funnel")
    init_corpus_db()

    in_scope_list = []
    ambiguous_list = []
    out_of_scope_count = 0

    stage_counts = {
        "Intent": 0,
        "Articulation": 0,
        "Search": 0,
        "Initial Results": 0,
        "Scrolling Results": 0,
        "Iterative Refinement": 0,
        "Outcome": 0,
    }

    verified_quotes_count = 0

    for doc_id, cls in classifications.items():
        d = raw_map.get(doc_id, {})
        classification = cls.get("classification", "out_of_scope")
        content = d.get("content", "")
        quote = cls.get("verbatim_quote", "")
        is_verified = 1 if is_quote_grounded(quote, content) else 0

        # Strict Integrity Gate
        if classification == "in_scope" and not is_verified:
            classification = "ambiguous"
            cls["classification"] = "ambiguous"
            cls["reason"] = f"Reclassified as ambiguous: quote failed verbatim grounding check. ({cls.get('reason', '')})"

        c.execute("""
            INSERT OR REPLACE INTO search_only_documents (
                doc_id, source, source_id, author, created_at, content, url,
                classification, search_mode, verbatim_quote, confidence, reason,
                is_quote_verified, model_used, classified_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            d.get("source", ""),
            d.get("source_id", ""),
            d.get("author", ""),
            d.get("created_at", ""),
            content,
            d.get("url", ""),
            classification,
            cls.get("search_mode", "none"),
            quote,
            cls.get("confidence", 0.85),
            cls.get("reason", ""),
            is_verified,
            cls.get("model_used", "gemini"),
            cls.get("classified_at", ""),
        ))

        if classification == "in_scope":
            verified_quotes_count += 1
            stages = cls.get("stages_evidenced", [])
            for st in stages:
                if st in stage_counts:
                    stage_counts[st] += 1
                c.execute("INSERT OR REPLACE INTO flow_stages_evidenced (doc_id, stage) VALUES (?, ?)", (doc_id, st))

            in_scope_list.append({
                **d,
                **cls,
                "is_quote_verified": True,
            })
        elif classification == "ambiguous":
            ambiguous_list.append({
                **d,
                **cls,
                "is_quote_verified": bool(is_verified),
            })
        else:
            out_of_scope_count += 1

    # Record Funnel in DB
    funnel_metrics = [
        ("raw_documents_reviewed", len(raw_docs)),
        ("retained_search_in_scope", len(in_scope_list)),
        ("excluded_out_of_scope", out_of_scope_count),
        ("logged_ambiguous", len(ambiguous_list)),
    ]
    for k, v in funnel_metrics:
        c.execute("INSERT OR REPLACE INTO collection_funnel (metric_name, metric_value, updated_at) VALUES (?, ?, ?)",
                  (k, v, datetime.now(timezone.utc).isoformat()))

    conn.commit()
    conn.close()

    # Save JSON files
    with open(CORPUS_DIR / "search_only_corpus.json", "w", encoding="utf-8") as f:
        json.dump(in_scope_list, f, ensure_ascii=False, indent=2)

    with open(CORPUS_DIR / "ambiguous_excluded.json", "w", encoding="utf-8") as f:
        json.dump(ambiguous_list, f, ensure_ascii=False, indent=2)

    funnel_summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "classifier_models": MODELS,
        "funnel": {
            "total_raw_reviewed": len(raw_docs),
            "retained_search_in_scope": len(in_scope_list),
            "excluded_out_of_scope": out_of_scope_count,
            "logged_ambiguous": len(ambiguous_list),
            "search_yield_pct": round((len(in_scope_list) / len(raw_docs)) * 100, 2),
            "quote_grounding_verified_pct": round((verified_quotes_count / max(1, len(in_scope_list))) * 100, 1),
        },
        "stage_distribution": stage_counts,
        "platform_breakdown": {},
    }

    for item in in_scope_list:
        src = item.get("source", "unknown")
        funnel_summary["platform_breakdown"][src] = funnel_summary["platform_breakdown"].get(src, 0) + 1

    with open(CORPUS_DIR / "funnel_summary.json", "w", encoding="utf-8") as f:
        json.dump(funnel_summary, f, ensure_ascii=False, indent=2)

    # Markdown Report
    report_md = f"""# Google Photos Search-Only Retrieval Corpus — Collection Funnel Report

**Scope:** Strict Search-Based Retrieval (Collection-Level Scoping)  
**Classifier Suite:** Google Gemini Suite ({', '.join(MODELS)})  
**Timestamp:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Quote Grounding Rate:** {funnel_summary['funnel']['quote_grounding_verified_pct']}% Verifiable Substrings  

---

## 1. The Collection Funnel

| Stage | Document Count | Percentage of Raw Pool | Definition & Scope Boundary |
|:---|---:|---:|:---|
| **1. Total Raw Documents Reviewed** | **{len(raw_docs):,}** | **100.0%** | Multi-source collection across HN, Play Store, App Store, YouTube, Reddit |
| **2. Excluded (Out of Scope)** | **{out_of_scope_count:,}** | **{out_of_scope_count / len(raw_docs) * 100:.1f}%** | Manual timeline scroll without search, backup/sync errors, UI gripes, ratings |
| **3. Logged as Ambiguous** | **{len(ambiguous_list):,}** | **{len(ambiguous_list) / len(raw_docs) * 100:.1f}%** | Unclear whether search was attempted; strictly excluded to protect data purity |
| **4. Retained Search-Only Corpus** | **{len(in_scope_list):,}** | **{len(in_scope_list) / len(raw_docs) * 100:.1f}%** | **100% Verified Search-Based Retrieval Attempts** (Classic Keyword or Gemini/Ask Photos) |

---

## 2. Retrieval Flow Stage Tagging

Every retained document evidences one or more chronological stages of the retrieval journey:

$$\\text{{Intent}} \\rightarrow \\text{{Articulation}} \\rightarrow \\text{{Search}} \\rightarrow \\text{{Initial Results}} \\rightarrow \\text{{Scrolling Results}} \\rightarrow \\text{{Iterative Refinement}} \\rightarrow \\text{{Outcome}}$$

| Flow Stage | Description | Documents Evidencing Stage | Share of Search Corpus |
|:---|:---|---:|---:|
| **Intent** | User remembers a specific photo/moment and intends to retrieve it | **{stage_counts['Intent']}** | **{stage_counts['Intent'] / max(1, len(in_scope_list)) * 100:.1f}%** |
| **Articulation** | User phrases the memory into words, keywords, or conversational prompt | **{stage_counts['Articulation']}** | **{stage_counts['Articulation'] / max(1, len(in_scope_list)) * 100:.1f}%** |
| **Search** | User executes search via search bar or Ask Photos AI | **{stage_counts['Search']}** | **{stage_counts['Search'] / max(1, len(in_scope_list)) * 100:.1f}%** |
| **Initial Results** | First results returned (irrelevant photos, zero results, accurate hit) | **{stage_counts['Initial Results']}** | **{stage_counts['Initial Results'] / max(1, len(in_scope_list)) * 100:.1f}%** |
| **Scrolling Results** | Looking/skimming through returned search results to locate target photo | **{stage_counts['Scrolling Results']}** | **{stage_counts['Scrolling Results'] / max(1, len(in_scope_list)) * 100:.1f}%** |
| **Iterative Refinement** | Trying another query, rephrasing, adding terms, or asking follow-ups | **{stage_counts['Iterative Refinement']}** | **{stage_counts['Iterative Refinement'] / max(1, len(in_scope_list)) * 100:.1f}%** |
| **Outcome** | Finding the photo, giving up, abandoning search, or forced scroll fallback | **{stage_counts['Outcome']}** | **{stage_counts['Outcome'] / max(1, len(in_scope_list)) * 100:.1f}%** |

---

## 3. Retained Search-Only Corpus by Source Platform

| Platform | Channel Nature | Retained Search Documents | Percentage of Search Corpus |
|:---|:---|---:|---:|
"""
    for src, count in sorted(funnel_summary["platform_breakdown"].items(), key=lambda x: x[1], reverse=True):
        report_md += f"| **{src}** | {src.capitalize()} | **{count:,}** | **{count / max(1, len(in_scope_list)) * 100:.1f}%** |\n"

    report_md += f"""| **Total Retained** | **All 5 Channels** | **{len(in_scope_list):,}** | **100.0%** |

---

## 4. Grounding & Storage Artifacts

- **Dedicated SQLite Database:** `data/search_only_corpus/search_only_corpus.sqlite`
- **Clean JSON Dataset:** `data/search_only_corpus/search_only_corpus.json`
- **Ambiguous Cases Log:** `data/search_only_corpus/ambiguous_excluded.json`
- **Verification:** {funnel_summary['funnel']['quote_grounding_verified_pct']}% of quotes character-for-character verified against raw review text (`INSTR > 0`).
"""

    with open(CORPUS_DIR / "COLLECTION_FUNNEL_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    print("\n" + "=" * 65)
    print("🎉 FINAL SEARCH-ONLY RETRIEVAL CORPUS COMPLETED!")
    print(f"  • Raw Documents Reviewed:   {len(raw_docs):,}")
    print(f"  • Retained In-Scope Search: {len(in_scope_list):,}")
    print(f"  • Excluded Out-of-Scope:    {out_of_scope_count:,}")
    print(f"  • Logged as Ambiguous:      {len(ambiguous_list):,}")
    print(f"  • Quote Grounding Rate:     {funnel_summary['funnel']['quote_grounding_verified_pct']}%")
    print(f"  • Saved report: data/search_only_corpus/COLLECTION_FUNNEL_REPORT.md")
    print("=" * 65)

if __name__ == "__main__":
    main()
