import sqlite3

conn = sqlite3.connect('data/db.sqlite')
cursor = conn.cursor()

# 1. vague_memory_cue
print("=== VAGUE MEMORY CUE ===")
cursor.execute("SELECT content, source FROM documents WHERE content LIKE '%random results%' OR content LIKE '%unrelated%' LIMIT 3")
for r in cursor.fetchall():
    print(f"[{r[1]}] {r[0][:120]}")

# 2. literal_keyword_match
print("\n=== LITERAL KEYWORD MATCH ===")
cursor.execute("SELECT content, source FROM documents WHERE content LIKE '%exact%' AND content LIKE '%search%' LIMIT 3")
for r in cursor.fetchall():
    print(f"[{r[1]}] {r[0][:120]}")

# 3. query_formulation_gap
print("\n=== QUERY FORMULATION GAP ===")
cursor.execute("SELECT content, source FROM documents WHERE content LIKE '%try to search%' OR content LIKE '%describe%' LIMIT 3")
for r in cursor.fetchall():
    print(f"[{r[1]}] {r[0][:120]}")

# 4. forced_scroll_or_abandon
print("\n=== FORCED SCROLL OR ABANDON ===")
cursor.execute("SELECT content, source FROM documents WHERE content LIKE '%scrolling%' AND content LIKE '%manually%' LIMIT 3")
for r in cursor.fetchall():
    print(f"[{r[1]}] {r[0][:120]}")

# 5. zero_recall_miss
print("\n=== ZERO RECALL MISS ===")
cursor.execute("SELECT content, source FROM documents WHERE content LIKE '%no results%' LIMIT 3")
for r in cursor.fetchall():
    print(f"[{r[1]}] {r[0][:120]}")

# 6. scrolling_friction
print("\n=== SCROLLING FRICTION ===")
cursor.execute("SELECT content, source FROM documents WHERE content LIKE '%scroll down search%' OR content LIKE '%keeps jumping%' OR content LIKE '%timeline%' LIMIT 3")
for r in cursor.fetchall():
    print(f"[{r[1]}] {r[0][:120]}")
