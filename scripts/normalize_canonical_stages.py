import json
import sqlite3
from pathlib import Path

CORPUS_DIR = Path("data/search_only_corpus")
DB_PATH = CORPUS_DIR / "search_only_corpus.sqlite"
JSON_PATH = CORPUS_DIR / "search_only_corpus.json"
CHECKPOINT_PATH = CORPUS_DIR / "classification_checkpoint.json"
SUMMARY_PATH = CORPUS_DIR / "funnel_summary.json"
REPORT_PATH = CORPUS_DIR / "COLLECTION_FUNNEL_REPORT.md"

CANONICAL_STAGES = [
    "Intent",
    "Articulation",
    "Search",
    "Initial Results",
    "Scrolling Results",
    "Iterative Refinement",
    "Outcome",
]

STAGE_ALIAS = {
    "iteration": "Iterative Refinement",
    "iterative refinement": "Iterative Refinement",
    "refinement": "Iterative Refinement",
    "initial result": "Initial Results",
    "scrolling result": "Scrolling Results",
}

def normalize_stage_name(st: str) -> str:
    cleaned = st.strip()
    low = cleaned.lower()
    if low in STAGE_ALIAS:
        return STAGE_ALIAS[low]
    for c in CANONICAL_STAGES:
        if low == c.lower():
            return c
    return cleaned

def main():
    print("Normalizing flow stages to the 7 canonical stages...")

    # 1. Update Checkpoint
    with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
        chk = json.load(f)

    for k, v in chk.items():
        if "stages_evidenced" in v and isinstance(v["stages_evidenced"], list):
            new_stages = []
            for st in v["stages_evidenced"]:
                norm = normalize_stage_name(st)
                if norm in CANONICAL_STAGES and norm not in new_stages:
                    new_stages.append(norm)
            v["stages_evidenced"] = new_stages

    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        json.dump(chk, f)

    # 2. Update JSON
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    stage_counts = {s: 0 for s in CANONICAL_STAGES}

    for item in corpus:
        if "stages_evidenced" in item and isinstance(item["stages_evidenced"], list):
            new_stages = []
            for st in item["stages_evidenced"]:
                norm = normalize_stage_name(st)
                if norm in CANONICAL_STAGES and norm not in new_stages:
                    new_stages.append(norm)
            item["stages_evidenced"] = new_stages
            for s in new_stages:
                stage_counts[s] += 1

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    # 3. Update SQLite DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM flow_stages_evidenced")
    for item in corpus:
        doc_id = item["doc_id"]
        for st in item["stages_evidenced"]:
            c.execute("INSERT OR REPLACE INTO flow_stages_evidenced (doc_id, stage) VALUES (?, ?)", (doc_id, st))
    conn.commit()
    conn.close()

    # 4. Update funnel summary
    with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
        summary = json.load(f)

    summary["stage_distribution"] = stage_counts
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # 5. Regenerate markdown table in report
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        report_text = f.read()

    # Verify stage distribution output
    print("Stage Distribution after canonical normalization:")
    for s, count in stage_counts.items():
        pct = (count / len(corpus)) * 100
        print(f"  • {s:20}: {count:4} ({pct:5.1f}%)")

if __name__ == "__main__":
    main()
