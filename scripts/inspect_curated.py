import json

with open('scripts/curated_quotes_output.json', 'r', encoding='utf-8') as f:
    curated = json.load(f)

for qid in range(1, 11):
    items = curated[str(qid)]
    print(f"\n=================== QUESTION {qid} ({len(items)} quotes) ===================")
    for i, item in enumerate(items[:4]):
        print(f"[{i+1}] ({item['source']} | {item['source_id']} | len={len(item['text'])} | date={item['date']}):")
        print(f"\"{item['text']}\"\n")
