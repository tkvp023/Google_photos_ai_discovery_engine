import os
import sys
import requests
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv
from scripts.build_search_only_corpus import SYSTEM_PROMPT

load_dotenv('.env')
key = os.getenv('GEMINI_API_KEY')

for m in ['gemini-3.8-flash', 'gemini-3.7-flash', 'gemini-3.5-flash', 'gemini-3.5-flash-lite', 'gemini-flash-lite-latest', 'gemini-3.1-flash-lite']:
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}'
    payload = {
        'system_instruction': {'parts': [{'text': SYSTEM_PROMPT}]},
        'contents': [{'role': 'user', 'parts': [{'text': 'Classify: --- DOCUMENT doc_id: "test_1" (Platform: Play Store) ---\nI tried typing receipt 2023 in search and it gave me pictures of dogs instead of receipts.'}]}],
        'generationConfig': {'response_mime_type': 'application/json', 'temperature': 0.1}
    }
    r = requests.post(url, json=payload, timeout=12)
    print(f'Model: {m} | Status: {r.status_code}')
    if r.status_code == 200:
        print('   Result:', r.json()['candidates'][0]['content']['parts'][0]['text'][:120])
    else:
        err = r.json().get('error', {})
        print('   Error:', err.get('message', '')[:100].replace('\n', ' '))
