import sqlite3
import math

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

def test_pair(sys_tag, sys_label, rel_tag, rel_label):
    c.execute("SELECT COUNT(DISTINCT doc_id) FROM hesitation_tags WHERE reason = ?", (sys_tag,))
    s_cnt = c.fetchone()[0]
    
    c.execute("SELECT COUNT(DISTINCT doc_id) FROM hesitation_tags WHERE reason = ?", (rel_tag,))
    h_cnt = c.fetchone()[0]
    
    c.execute("""
        SELECT COUNT(DISTINCT h1.doc_id)
        FROM hesitation_tags h1
        JOIN hesitation_tags h2 ON h1.doc_id = h2.doc_id
        WHERE h1.reason = ? AND h2.reason = ?
    """, (sys_tag, rel_tag))
    co_cnt = c.fetchone()[0]
    
    corr = round(co_cnt / math.sqrt(s_cnt * h_cnt), 2) if (s_cnt * h_cnt) > 0 else 0.0
    return {
        "systemic_issue": sys_label,
        "systemic_frequency": s_cnt,
        "related_hesitation": rel_label,
        "hesitation_frequency": h_cnt,
        "co_occurrence": co_cnt,
        "correlation_hint": corr
    }

print("=== Testing candidate pairs for correlation table ===")
# Candidate 1: Screenshot clutter with timeline navigation clunky or scrolling fatigue
print(test_pair("screenshot_and_junk_clutter", "Screenshot & Clutter Overflow", "timeline_navigation_clunky", "Timeline Navigation Clunky"))

# Candidate 2: Zero recall with query too literal
print(test_pair("zero_results_for_existing_photo", "Zero Recall on Existing Photos", "query_too_literal", "Query Interpreted Too Literally"))

# Candidate 3: Facial clustering with face untagged
print(test_pair("face_recognition_misidentification", "Facial Clustering Errors", "face_untagged_missing", "Face Untagged or Missing"))

# Candidate 4: OCR detection failure with medicine or product label
print(test_pair("text_ocr_detection_failure", "OCR & Document Indexing Gap", "medicine_or_product_label", "Medicine & Product Label Search"))

