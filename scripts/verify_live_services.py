"""
Comprehensive Live HTTP Service Verification for AI Discovery Engine
Tests:
- Next.js Dashboard Routes (/, /ask, /findings, /gaps, /questions/1-10)
- FastAPI RAG Sidecar (/health, /api/ask)
"""

import sys
import json
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

routes = [
    "http://localhost:3000/",
    "http://localhost:3000/ask",
    "http://localhost:3000/findings",
    "http://localhost:3000/gaps",
    "http://localhost:3000/questions/1",
    "http://localhost:3000/questions/2",
    "http://localhost:3000/questions/3",
    "http://localhost:3000/questions/4",
    "http://localhost:3000/questions/5",
    "http://localhost:3000/questions/6",
    "http://localhost:3000/questions/7",
    "http://localhost:3000/questions/8",
    "http://localhost:3000/questions/9",
    "http://localhost:3000/questions/10",
    "http://localhost:8000/health"
]

print("=" * 65)
print("🌐 VERIFYING ALL LIVE HTTP ROUTES (AI DISCOVERY ENGINE)")
print("=" * 65)

all_passed = True
for r in routes:
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            data = resp.read()
            print(f"[OK {resp.status}] {r:<35} ({len(data):,} bytes)")
    except Exception as e:
        print(f"[FAIL] {r:<35} ({e})")
        all_passed = False

# Test live RAG Query API
print("\n[Testing Live RAG Query POST /api/ask]")
try:
    req_rag = urllib.request.Request(
        "http://localhost:8000/api/ask",
        data=json.dumps({
            "query": "Why do users struggle to find photos when they only remember friends or a vacation?"
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_rag, timeout=25) as resp:
        rag_res = json.loads(resp.read().decode("utf-8"))
        lat = rag_res.get("latency_ms")
        docs = rag_res.get("docs_retrieved")
        cits = len(rag_res.get("citations", []))
        ans = repr(rag_res.get("answer", "")[:140])
        print(f"[OK 200] RAG Latency: {lat} ms | Retrieved docs: {docs}")
        print(f"         Citations count: {cits}")
        print(f"         Answer preview: {ans}...")
except Exception as e:
    print("[FAIL RAG API]:", e)
    all_passed = False

print("\n" + "=" * 65)
print(f"ALL LIVE HTTP SERVICES OPERATIONAL: {'✅ TRUE (100% HEALTHY)' if all_passed else '❌ FALSE'}")
print("=" * 65)
