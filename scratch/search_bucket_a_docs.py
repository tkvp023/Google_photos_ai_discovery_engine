import sqlite3

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

def search_docs(term, limit=5):
    c.execute("""
        SELECT d.doc_id, d.source, d.content, d.timestamp, tb.bucket
        FROM documents d
        JOIN triage_buckets tb ON d.doc_id = tb.doc_id
        WHERE d.content LIKE ? AND tb.bucket = 'A'
        LIMIT ?
    """, (f"%{term}%", limit))
    return c.fetchall()

print("=== Search for 'WhatsApp' in Bucket A ===")
for r in search_docs("WhatsApp"):
    print(f"[{r[1]}] {r[2][:100]}...")

print("\n=== Search for 'Apple' or 'Immich' in Bucket A ===")
for r in search_docs("Apple"):
    print(f"[{r[1]}] {r[2][:100]}...")
for r in search_docs("Immich"):
    print(f"[{r[1]}] {r[2][:100]}...")

print("\n=== Search for 'prescription' or 'medicine' or 'license' in Bucket A ===")
for r in search_docs("license"):
    print(f"[{r[1]}] {r[2][:100]}...")
for r in search_docs("prescription"):
    print(f"[{r[1]}] {r[2][:100]}...")
for r in search_docs("receipt"):
    print(f"[{r[1]}] {r[2][:100]}...")

print("\n=== Search for 'scroll' in Bucket A ===")
for r in search_docs("scroll", 3):
    print(f"[{r[1]}] {r[2][:100]}...")
