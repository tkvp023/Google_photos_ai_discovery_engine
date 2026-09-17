import os
import sys
sys.path.insert(0, ".")
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pipeline.db.connection import get_session
from pipeline.db.models import Document, HesitationTag, QuestionMapping
from pipeline.quantification.question_mapper import QUESTION_TAG_MAPPING, QUESTIONS

session = get_session()

print("=" * 60)
print("🔄 Synchronizing Question Mappings with Classified Tags...")
print("=" * 60)

# Clear old mappings
deleted = session.query(QuestionMapping).delete()
print(f"Cleared {deleted} legacy mappings.")

# Insert accurate mappings
new_mappings = 0
for qid, tags in QUESTION_TAG_MAPPING.items():
    # Find all documents with these tags
    matching_doc_ids = [
        row[0] for row in session.query(HesitationTag.doc_id)
        .filter(HesitationTag.reason.in_(tags))
        .distinct().all()
    ]
    
    for doc_id in matching_doc_ids:
        session.add(QuestionMapping(doc_id=doc_id, question_id=qid))
        new_mappings += 1

    print(f"  Q{qid:2d}: {QUESTIONS[qid][1]:<32} -> {len(matching_doc_ids):>4} docs mapped")

session.commit()
print(f"\n✅ Total question mappings inserted: {new_mappings:,}")
session.close()
