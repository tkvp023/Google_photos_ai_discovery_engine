import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/targeted_inventory.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

docs_to_check = [
    'DOCS/DISCOVERY_ENGINE_A_TO_Z_MASTER_REPORT.md',
    'DOCS/DASHBOARD_FULL_CONTENT_REFERENCE.md',
    'DOCS/DISCOVERY_ENGINE_A_TO_Z_MASTER_PROMPT.md',
    'DOCS/SLIDE_DECK_BLUEPRINT.md',
    'scripts/generate_slide_deck.py',
    'dashboard/lib/mockData.ts',
    'dashboard/public/data/summary.json',
    'dashboard/public/data/bucket_a_findings.json',
    'insights_photos.md'
]

for doc in docs_to_check:
    print(f"\n==================== {doc} ====================")
    doc_items = [it for it in items if it['file'].replace('\\', '/') == doc]
    for it in doc_items:
        print(f"  Line {it['line']}: {it['text']}")
