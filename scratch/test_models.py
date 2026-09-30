import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')
key = os.getenv('GEMINI_API_KEY')

models_to_test = [
    'gemini-3.8-flash',
    'gemini-3.7-flash',
    'gemini-3.6-flash',
    'gemini-3.5-flash',
    'gemini-3.5-flash-lite',
    'gemini-flash-latest',
    'gemini-flash-lite-latest',
    'gemini-3.1-flash-lite',
    'gemini-pro-latest'
]

for m in models_to_test:
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}'
    try:
        r = requests.post(url, json={'contents': [{'parts': [{'text': 'hi'}]}]}, timeout=6)
        print(f'{m}: {r.status_code}')
        if r.status_code != 200:
            err = r.json().get('error', {})
            msg = err.get('message', '')[:100].replace('\n', ' ')
            print(f'   Reason: {msg}')
    except Exception as e:
        print(f'{m}: exception {e}')
