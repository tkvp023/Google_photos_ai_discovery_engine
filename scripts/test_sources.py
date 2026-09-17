import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import requests

# 1. Test Hacker News Algolia API
print("1. Testing Hacker News API...")
try:
    hn_url = "https://hn.algolia.com/api/v1/search?query=%22google+photos%22+search&tags=comment&hitsPerPage=10"
    r = requests.get(hn_url, timeout=10)
    print(f"   Status: {r.status_code}, Hits: {len(r.json().get('hits', []))}")
except Exception as e:
    print(f"   HN Error: {e}")

# 2. Test Bluesky Public Search API
print("\n2. Testing Bluesky API...")
try:
    bsky_url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    params = {"q": "google photos search", "limit": 10}
    r = requests.get(bsky_url, params=params, timeout=10)
    posts = r.json().get("posts", [])
    print(f"   Status: {r.status_code}, Posts: {len(posts)}")
    if posts:
        print(f"   Sample: {posts[0].get('record', {}).get('text', '')[:100]}")
except Exception as e:
    print(f"   Bluesky Error: {e}")
