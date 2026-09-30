import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load 5 candidates
raw_file = PROJECT_ROOT / "data" / "search_only_corpus" / "raw" / "hackernews_raw.json"
with open(raw_file, "r", encoding="utf-8") as f:
    docs = json.load(f)[:5]

print(f"Testing 5 docs with openai/gpt-oss-120b on Groq...")

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
      "stages_evidenced": ["Intent", "Articulation", "Search", "Initial Results", "Scrolling Results", "Iterative Refinement", "Outcome"],
      "search_mode": "classic_keyword | gemini_ai | both | unspecified_search",
      "verbatim_quote": "exact substring from text",
      "confidence": float,
      "reason": "explanation"
    }
  ]
}
"""

user_prompt = "Classify each document below strictly according to instructions:\n\n"
for d in docs:
    user_prompt += f"--- DOCUMENT doc_id: \"{d['doc_id']}\" ---\n{d['content'][:600]}\n\n"

t0 = time.time()
try:
    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    print(f"Success in {time.time() - t0:.2f}s!")
    data = json.loads(resp.choices[0].message.content)
    print("Results count:", len(data.get("results", [])))
    for r in data.get("results", []):
        print(f"  [{r.get('classification')}] doc: {r.get('doc_id')} | stages: {r.get('stages_evidenced')}")
        print(f"    quote: \"{r.get('verbatim_quote')[:60]}...\"")
        print(f"    reason: {r.get('reason')}")
except Exception as e:
    print(f"Failed in {time.time() - t0:.2f}s: {e}")
