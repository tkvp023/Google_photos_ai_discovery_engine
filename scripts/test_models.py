import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
models = [
    'gemini-3.1-flash-lite',
    'gemini-flash-lite-latest',
    'gemini-3.5-flash-lite',
    'gemini-3.5-flash',
    'gemini-3.6-flash'
]

for m in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": 'Reply with JSON: {"status": "ok"}'}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"{m}: HTTP {r.status_code}")
        if r.status_code != 200:
            print(f"  Error: {r.text[:120]}")
        else:
            print(f"  Response: {r.json()['candidates'][0]['content']['parts'][0]['text'].strip()}")
    except Exception as e:
        print(f"{m} Exception: {e}")
