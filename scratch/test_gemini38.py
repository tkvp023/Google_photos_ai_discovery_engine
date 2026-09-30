import os
import json
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.8-flash")

prompt = """
You are an expert qualitative data classifier.
Classify this user review:
"I searched for 'dog' and it showed a cat. I tried typing 'golden retriever' instead and found nothing."

Output JSON schema:
{
  "classification": "in_scope",
  "stages_evidenced": ["Intent", "Search", "Initial Results", "Iterative Refinement", "Outcome"],
  "search_mode": "classic_keyword",
  "verbatim_quote": "I searched for 'dog' and it showed a cat.",
  "reason": "User searched for dog, got wrong results, refined query, and had a negative outcome."
}
"""

resp = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
print("Response:")
print(resp.text)
