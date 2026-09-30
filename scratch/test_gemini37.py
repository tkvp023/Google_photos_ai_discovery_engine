import os
import json
import time
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.7-flash")

prompt = """
Classify these 2 reviews into JSON:
[Document 1]: "I searched 'beach vacation' and got zero results."
[Document 2]: "Why does the app delete all my photos when I turn off sync?"

Output JSON:
{
  "results": [
    {
      "doc_id": "1",
      "classification": "in_scope",
      "stages_evidenced": ["Search", "Initial Results", "Outcome"],
      "search_mode": "classic_keyword",
      "verbatim_quote": "I searched 'beach vacation' and got zero results.",
      "confidence": 0.98,
      "reason": "User performed keyword search resulting in zero results."
    },
    {
      "doc_id": "2",
      "classification": "out_of_scope",
      "stages_evidenced": [],
      "search_mode": "none",
      "verbatim_quote": "",
      "confidence": 0.99,
      "reason": "Pure sync/deletion issue with no search attempt."
    }
  ]
}
"""

t0 = time.time()
resp = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
print("Time:", time.time() - t0)
print(resp.text)
