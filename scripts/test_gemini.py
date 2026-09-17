import os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GEMINI_API_KEY")
import google.generativeai as genai
genai.configure(api_key=key)

for m in ["gemini-3.6-flash", "gemini-3.8-flash", "gemini-3.5-flash"]:
    try:
        model = genai.GenerativeModel(m)
        res = model.generate_content("Reply with: 'System OK'", request_options={"timeout": 15})
        print(f"Model {m}: SUCCESS -> {res.text.strip()}")
    except Exception as e:
        print(f"Model {m}: ERROR -> {e}")
