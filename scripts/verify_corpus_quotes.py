import sqlite3
import sys
import json
import re
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


import html

def normalize(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"[\u2018\u2019\u201c\u201d\'\"`\ufffd\-_]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def is_grounded(quote, content):
    if not quote or not content:
        return False
    norm_q = normalize(quote)
    norm_c = normalize(content)
    if norm_q in norm_c:
        return True
    # If quote has ellipsis, check if all subparts exist in content
    parts = [p.strip() for p in re.split(r"\.{2,}|\u2026", quote) if len(p.strip()) >= 8]
    if parts and all(normalize(p) in norm_c for p in parts):
        return True
    return False

def main():
    db_path = Path("data/search_only_corpus/search_only_corpus.sqlite")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT doc_id, verbatim_quote, content FROM search_only_documents WHERE classification='in_scope'")
    rows = c.fetchall()

    verified = 0
    unverified = []
    for doc_id, q, content in rows:
        if is_grounded(q, content):
            verified += 1
            c.execute("UPDATE search_only_documents SET is_quote_verified=1 WHERE doc_id=?", (doc_id,))
        else:
            unverified.append((doc_id, q, content[:150]))

    conn.commit()
    conn.close()

    print(f"✅ Grounding verification complete: {verified}/{len(rows)} verified ({verified/len(rows)*100:.1f}%)")
    if unverified:
        print(f"⚠️ Unverified: {len(unverified)}")
        for doc_id, q, snip in unverified[:5]:
            print(f"  • Doc {doc_id}:")
            print(f"    Quote: {q}")
            print(f"    Snip:  {snip}")

    # Also update JSON export
    json_path = Path("data/search_only_corpus/search_only_corpus.json")
    if json_path.exists():
        docs = json.load(open(json_path, encoding="utf-8"))
        for d in docs:
            d["is_quote_verified"] = is_grounded(d.get("verbatim_quote", ""), d.get("content", ""))
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
        print("✅ Updated search_only_corpus.json with verified flags.")

if __name__ == "__main__":
    main()
