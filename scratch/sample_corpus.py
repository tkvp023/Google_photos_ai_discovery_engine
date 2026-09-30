import json

data = json.load(open("data/search_only_corpus/search_only_corpus.json", "r", encoding="utf-8"))
print(f"Total verified in-scope items: {len(data):,}\n")
for src in ['hackernews', 'reddit', 'youtube', 'playstore', 'appstore']:
    items = [d for d in data if d.get('source') == src]
    if items:
        d = items[0]
        print(f"=== Platform: {src.upper()} (Total in corpus: {len(items):,}) ===")
        print(f"Doc ID:      {d.get('doc_id')}")
        print(f"Quote:       \"{d.get('verbatim_quote')}\"")
        print(f"Stages:      {d.get('stages_evidenced')}")
        print(f"Search Mode: {d.get('search_mode')}")
        print(f"Reason:      {d.get('reason')}\n")
