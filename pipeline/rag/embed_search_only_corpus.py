"""
Search-Only Vector Store Embedder & Indexer
Indexes all 1,616 verified search retrieval documents from data/search_only_corpus/search_only_corpus.sqlite
into a dedicated high-dimensional TF-IDF vector index with full metadata and stage filtering.

Usage:
    python -m pipeline.rag.embed_search_only_corpus
"""

import sys
import os
import json
import sqlite3
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.rag.vector_store import VectorStore

SEARCH_CORPUS_DIR = PROJECT_ROOT / "data" / "search_only_corpus"
DB_PATH = SEARCH_CORPUS_DIR / "search_only_corpus.sqlite"
JSON_PATH = SEARCH_CORPUS_DIR / "search_only_corpus.json"
MODEL_OUT = SEARCH_CORPUS_DIR / "vector_model.joblib"
META_OUT = SEARCH_CORPUS_DIR / "vector_meta.json"

def build_search_only_index():
    print("=" * 65)
    print("🧠 INDEXING SEARCH-ONLY RETRIEVAL CORPUS INTO VECTOR STORE")
    print("   Source: data/search_only_corpus/search_only_corpus.sqlite")
    print("=" * 65)

    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Query only in_scope verified documents
    c.execute("""
        SELECT doc_id, source, source_id, author, created_at, content, url,
               classification, search_mode, verbatim_quote, confidence, reason,
               is_quote_verified, model_used, classified_at
        FROM search_only_documents
        WHERE classification = 'in_scope'
    """)
    rows = c.fetchall()
    print(f"  📄 Loaded {len(rows):,} verified in-scope documents from database")

    # Fetch stage associations
    c.execute("SELECT doc_id, stage FROM flow_stages_evidenced")
    stage_rows = c.fetchall()
    conn.close()

    stages_by_doc = {}
    for did, st in stage_rows:
        stages_by_doc.setdefault(did, []).append(st)

    doc_ids = []
    documents = []
    metadatas = []

    for r in rows:
        did = r[0]
        src = r[1]
        src_id = r[2]
        author = r[3]
        created_at = str(r[4] or "")[:10]
        content = r[5] or ""
        url = r[6] or ""
        search_mode = r[8] or "unspecified_search"
        quote = r[9] or ""
        confidence = float(r[10]) if r[10] is not None else 0.85
        reason = r[11] or ""
        stages = stages_by_doc.get(did, [])

        meta = {
            "doc_id": did,
            "source": src,
            "source_id": str(src_id or ""),
            "timestamp": created_at,
            "author": author or "",
            "search_mode": search_mode,
            "verbatim_quote": quote,
            "confidence": confidence,
            "reason": reason,
            "stages_evidenced": ",".join(stages),
            "content_preview": content[:400],
            "url": url,
        }

        doc_ids.append(did)
        # We index the content + search quote + stages for optimal lexical/semantic matching
        indexable_text = f"{content}\n\nSearch evidence: {quote}\nStages: {', '.join(stages)}"
        documents.append(indexable_text)
        metadatas.append(meta)

    # Initialize VectorStore targeting SEARCH_CORPUS_DIR
    store = VectorStore(data_dir=SEARCH_CORPUS_DIR)
    store.build_and_save(doc_ids, documents, metadatas)

    print(f"\n  ✅ Search-Only Indexing complete!")
    print(f"  📊 VectorStore contains {store.count():,} indexed search retrieval documents.")
    print(f"  💾 Model saved to: {MODEL_OUT}")
    print(f"  💾 Metadata saved to: {META_OUT}")

if __name__ == "__main__":
    build_search_only_index()
