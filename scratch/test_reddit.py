import requests
import json

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
url = "https://www.reddit.com/r/googlephotos/search.json?q=search&restrict_sr=1&limit=25"
try:
    r = requests.get(url, headers=headers, timeout=10)
    print("Status:", r.status_code)
    if r.status_code == 200:
        posts = r.json().get("data", {}).get("children", [])
        print("Found posts:", len(posts))
        for p in posts[:3]:
            d = p["data"]
            print(f"  • {d.get('title')} ({d.get('num_comments')} comments)")
    else:
        print("Error:", r.text[:200])
except Exception as e:
    print("Exception:", e)
