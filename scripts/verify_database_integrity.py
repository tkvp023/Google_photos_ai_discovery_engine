import os
import sys
sys.path.insert(0, ".")
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
from dotenv import load_dotenv
import json
from collections import Counter

load_dotenv()

from pipeline.db.connection import get_session
from pipeline.db.models import Document, Classification, HesitationTag, FactorMention

session = get_session()

print("=" * 60)
print("🔍 SQLite Database Integrity & Cleanliness Audit")
print("=" * 60)

total_docs = session.query(Document).count()
print(f"Total documents in database: {total_docs:,}")

# Check sources
sources = Counter([d.source for d in session.query(Document.source).all()])
print("\nDocuments by source:")
for s, count in sources.items():
    print(f"  - {s:<15}: {count:>5} ({count/total_docs*100:.1f}%)")

# Check content validity
empty_docs = session.query(Document).filter((Document.content == None) | (Document.content == "")).all()
short_docs = [d for d in session.query(Document.doc_id, Document.content).all() if len((d.content or "").strip()) < 15]
print(f"\nEmpty documents: {len(empty_docs)}")
print(f"Very short (<15 chars) documents: {len(short_docs)}")

# Check for off-domain contamination (e.g. Myntra / clothing)
off_domain_keywords = ["myntra", "t-shirt", "kurti", "saree", "lehenga", "jeans size", "delivery boy", "return picked up", "refund myntra"]
contaminated = []
for d in session.query(Document.doc_id, Document.content, Document.source).all():
    c_lower = (d.content or "").lower()
    for kw in off_domain_keywords:
        if kw in c_lower:
            contaminated.append((d.doc_id, d.source, kw, d.content[:60]))
            break

print(f"\nOff-domain / contaminated documents found: {len(contaminated)}")
if contaminated:
    for doc_id, src, kw, snippet in contaminated[:5]:
        print(f"  - [{src}] '{kw}': {snippet}...")

# Check classification progress
classified_count = session.query(Classification).count()
tags_count = session.query(HesitationTag).count()
factors_count = session.query(FactorMention).count()
print(f"\nClassified documents: {classified_count:,} / {total_docs:,} ({classified_count/total_docs*100:.1f}%)")
print(f"Total hesitation tags: {tags_count:,}")
print(f"Total factor mentions: {factors_count:,}")

# Check quote grounding on all tags
print("\nChecking quote grounding across all extracted hesitation tags...")
grounded = 0
unquoted = 0
checked_tags = session.query(HesitationTag).all()
for t in checked_tags:
    if not t.evidence_quote:
        unquoted += 1
        continue
    doc = session.query(Document).filter_by(doc_id=t.doc_id).first()
    if doc and doc.content and t.evidence_quote.strip().lower() in doc.content.lower():
        grounded += 1

print(f"Grounding rate: {grounded / max(len(checked_tags), 1) * 100:.1f}% ({grounded}/{len(checked_tags)})")

session.close()
print("=" * 60)
