import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-flash-latest")

# Load 5 candidates
raw_file = PROJECT_ROOT / "data" / "search_only_corpus" / "raw" / "hackernews_raw.json"
with open(raw_file, "r", encoding="utf-8") as f:
    docs = json.load(f)[:5]

print(f"Testing batch of {len(docs)} docs with gemini-flash-latest...")

SYSTEM_PROMPT = """You are a senior qualitative research analyst on the Google Photos Core Experience team.
Classify each document for search-based retrieval: in_scope, out_of_scope, or ambiguous.
Scope: User engages the search feature (keyword search or Gemini/Ask Photos AI search).
Manual browsing with no search attempt is out_of_scope.
Tag flow stages: Intent, Articulation, Search, Initial Results, Scrolling Results, Iterative Refinement, Outcome.

JSON schema:
{
  "results": [
    {
      "doc_id": "string",
      "classification": "in_scope | out_of_scope | ambiguous",
      "stages_evidenced": ["..."],
      "search_mode": "classic_keyword | gemini_ai | both | unspecified_search",
      "verbatim_quote": "exact substring",
      "confidence": float,
      "reason": "explanation"
    }
  ]
}
"""

user_prompt = ""
for d in docs:
    user_prompt += f"--- DOCUMENT doc_id: \"{d['doc_id']}\" ---\n{d['content'][:600]}\n\n"

t0 = time.time()
try:
    resp = model.generate_content(
        [SYSTEM_PROMPT, user_prompt],
        generation_config={"response_mime_type": "application/json", "temperature": 0.1},
        request_options={"timeout": 60}
    )
    print(f"Success in {time.time() - t0:.2f}s!")
    data = json.loads(resp.text)
    print("Results count:", len(data.get("results", [])))
    for r in data.get("results", []):
        print(f"  [{r.get('classification')}] doc: {r.get('doc_id')} | stages: {r.get('stages_evidenced')}")
        print(f"    quote: \"{r.get('verbatim_quote')[:60]}...\"")
        print(f"    reason: {r.get('reason')}")
except Exception as e:
    print(f"Failed in {time.time() - t0:.2f}s: {e}")
