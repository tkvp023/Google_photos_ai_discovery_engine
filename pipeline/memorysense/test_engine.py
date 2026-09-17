import sys
sys.path.insert(0, ".")
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from pipeline.memorysense.engine import get_memory_engine

engine = get_memory_engine()

queries = [
    "small café blue chairs paella trip 2-3 years ago",
    "medicine bottle for fever when I was sick last winter",
    "daughter eating ice cream at an outdoor plaza"
]

for q in queries:
    res = engine.search(q, quarantine_clutter=True)
    print("=" * 60)
    print("QUERY:", q)
    p = res["parsed_context"]
    print("Intent:", p["intent"], "| Time:", p["temporal_label"], "| Visuals:", p["visual_cues"])
    print("Quarantined Clutter Count:", p["clutter_quarantined_count"])
    print("Conversational Prompt:", res["conversational_prompt"])
    top = res["results"][0]
    print(f"Top Match: {top['title']} (Score: {top['similarity_score']})")
    print("Reasons:", top["matched_reasons"])
    print("Clarification Chips:", [c["label"] for c in res["clarification_chips"]])
