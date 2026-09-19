"""
Rebuild Pipeline Runner for AI Discovery Engine.
Orchestrates:
  Stage 1: Document Triage (A/B/C/D) across all corpus docs
  Stage 2: Failure-Point Deep-Tagging for Bucket-A docs
  Stage 3: Quantification and JSON Export for Dashboard
"""

import sys
import os
import argparse
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.db.connection import get_session, init_db
from pipeline.db.models import Document, TriageBucket, FailurePointTag
from pipeline.classification.triage_classifier import GeminiTriageClassifier


def run_stage1_triage(session, classifier: GeminiTriageClassifier, batch_size: int = 10, resume: bool = True, limit: int = None):
    """Run Stage 1 Triage on documents."""
    print("\n" + "=" * 60)
    print("STAGE 1: DOCUMENT TRIAGE (A / B / C / D)")
    print("=" * 60)

    # Fetch existing triaged doc_ids if resume
    existing_ids = set()
    if resume:
        rows = session.query(TriageBucket.doc_id).all()
        existing_ids = {r[0] for r in rows}
        print(f"Found {len(existing_ids)} already triaged documents.")

    query = session.query(Document).order_by(Document.doc_id)
    all_docs = query.all()
    total_docs = len(all_docs)
    print(f"Total documents in database: {total_docs}")

    pending_docs = [d for d in all_docs if d.doc_id not in existing_ids]
    if limit:
        pending_docs = pending_docs[:limit]
    
    print(f"Documents to process in this run: {len(pending_docs)}")
    if not pending_docs:
        print("[Stage 1] All documents already triaged!")
        return

    # Counts
    counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    # Pre-populate counts with existing
    if existing_ids:
        for b in session.query(TriageBucket.bucket).all():
            counts[b[0]] = counts.get(b[0], 0) + 1

    start_time = time.time()
    processed_count = 0

    for i in range(0, len(pending_docs), batch_size):
        batch = pending_docs[i : i + batch_size]
        batch_dicts = [{"doc_id": d.doc_id, "content": d.content} for d in batch]

        results, err = classifier.triage_batch(batch_dicts)
        if err:
            print(f"  [Warning] Batch {i // batch_size + 1}: {err}")

        now_iso = datetime.now(timezone.utc).isoformat()
        for res in results:
            bucket_val = res.get("bucket", "D")
            counts[bucket_val] = counts.get(bucket_val, 0) + 1

            tb = TriageBucket(
                doc_id=res["doc_id"],
                bucket=bucket_val,
                bucket_reason=res.get("bucket_reason", ""),
                evidence_quote=res.get("evidence_quote", ""),
                confidence=res.get("confidence", 0.75),
                search_type=res.get("search_type", "unspecified"),
                classified_at=now_iso,
            )
            session.merge(tb)

        session.commit()
        processed_count += len(batch)
        elapsed = time.time() - start_time
        pct = (processed_count / len(pending_docs)) * 100
        print(f"  [Triage] {processed_count}/{len(pending_docs)} ({pct:.1f}%) | Total A: {counts.get('A',0)}, B: {counts.get('B',0)}, C: {counts.get('C',0)}, D: {counts.get('D',0)} | {elapsed:.1f}s", flush=True)

    print("\n[Stage 1 Complete]", flush=True)
    for b in ("A", "B", "C", "D"):
        cnt = counts.get(b, 0)
        pct = (cnt / total_docs * 100) if total_docs > 0 else 0
        print(f"  Bucket {b}: {cnt} ({pct:.1f}%)")


def run_stage2_deep_tag(session, classifier: GeminiTriageClassifier, batch_size: int = 10, resume: bool = True, limit: int = None):
    """Run Stage 2 Deep-Tagging on Bucket-A documents."""
    print("\n" + "=" * 60)
    print("STAGE 2: FAILURE-POINT DEEP-TAGGING (BUCKET-A ONLY)")
    print("=" * 60)

    # Fetch bucket-A doc_ids
    bucket_a_rows = session.query(TriageBucket.doc_id).filter(TriageBucket.bucket == "A").all()
    bucket_a_ids = {r[0] for r in bucket_a_rows}
    print(f"Total Bucket-A documents found: {len(bucket_a_ids)}")

    if not bucket_a_ids:
        print("[Stage 2] No Bucket-A documents found. Run Stage 1 first.")
        return

    # Check already tagged docs
    existing_tagged_ids = set()
    if resume:
        rows = session.query(FailurePointTag.doc_id).distinct().all()
        existing_tagged_ids = {r[0] for r in rows}
        print(f"Found {len(existing_tagged_ids)} already deep-tagged Bucket-A docs.")

    pending_ids = [did for did in bucket_a_ids if did not in existing_tagged_ids]
    if limit:
        pending_ids = pending_ids[:limit]

    print(f"Bucket-A documents to process: {len(pending_ids)}")
    if not pending_ids:
        print("[Stage 2] All Bucket-A documents already deep-tagged!")
        return

    # Fetch pending doc objects
    pending_docs = session.query(Document).filter(Document.doc_id.in_(pending_ids)).all()
    # Map for easy lookup
    doc_map = {d.doc_id: d for d in pending_docs}

    type_counts = {"expression": 0, "interpretation": 0, "evaluation": 0, "recovery": 0}
    total_tags_created = 0
    start_time = time.time()
    processed_count = 0

    for i in range(0, len(pending_ids), batch_size):
        chunk_ids = pending_ids[i : i + batch_size]
        batch_dicts = [{"doc_id": did, "content": doc_map[did].content} for did in chunk_ids if did in doc_map]

        results, err = classifier.deep_tag_batch(batch_dicts)
        if err:
            print(f"  [Warning] Batch {i // batch_size + 1}: {err}")

        for res in results:
            doc_id = res.get("doc_id")
            tags = res.get("tags", [])
            for tag in tags:
                ftype = tag.get("failure_type", "interpretation")
                type_counts[ftype] = type_counts.get(ftype, 0) + 1
                total_tags_created += 1

                fpt = FailurePointTag(
                    doc_id=doc_id,
                    failure_type=ftype,
                    sub_category=tag.get("sub_category", ""),
                    memory_cue_type=tag.get("memory_cue_type", "combined"),
                    confidence=tag.get("confidence", 0.80),
                    evidence_quote=tag.get("evidence_quote", ""),
                    search_type=tag.get("search_type", "unspecified"),
                )
                session.add(fpt)

        session.commit()
        processed_count += len(chunk_ids)
        elapsed = time.time() - start_time
        pct = (processed_count / len(pending_ids)) * 100
        print(f"  [Deep-Tag] {processed_count}/{len(pending_ids)} ({pct:.1f}%) | Tags: {total_tags_created} (Expr: {type_counts.get('expression',0)}, Interp: {type_counts.get('interpretation',0)}, Eval: {type_counts.get('evaluation',0)}, Recov: {type_counts.get('recovery',0)}) | {elapsed:.1f}s", flush=True)

    print("\n[Stage 2 Complete]", flush=True)
    print(f"Total failure-point tags created: {total_tags_created}")
    for ft, cnt in type_counts.items():
        print(f"  {ft}: {cnt}")


def run_stage3_export():
    """Run Stage 3 Export to generate JSON contracts for dashboard."""
    print("\n" + "=" * 60)
    print("STAGE 3: QUANTIFICATION & JSON EXPORT")
    print("=" * 60)
    from pipeline.quantification.export import export_all_data
    export_all_data()
    print("[Stage 3 Complete]")


def main():
    parser = argparse.ArgumentParser(description="Rebuild AI Discovery Engine classification & dashboard data.")
    parser.add_argument("--stage", choices=["triage", "deep-tag", "export", "all"], default="all", help="Pipeline stage to run")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for LLM inference (default: 10)")
    parser.add_argument("--rpm", type=int, default=15, help="Requests per minute limit (default: 15)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of documents for testing")
    parser.add_argument("--no-resume", action="store_true", help="Do not resume; reprocess from start")

    args = parser.parse_args()

    print(f"Initializing database and classifier (RPM limit: {args.rpm})...")
    init_db()
    session = get_session()
    classifier = GeminiTriageClassifier(rpm_limit=args.rpm)

    resume = not args.no_resume

    try:
        if args.stage in ("triage", "all"):
            run_stage1_triage(session, classifier, batch_size=args.batch_size, resume=resume, limit=args.limit)

        if args.stage in ("deep-tag", "all"):
            run_stage2_deep_tag(session, classifier, batch_size=args.batch_size, resume=resume, limit=args.limit)

        if args.stage in ("export", "all"):
            run_stage3_export()

    finally:
        session.close()

    print("\n[SUCCESS] Pipeline execution finished.")


if __name__ == "__main__":
    main()
