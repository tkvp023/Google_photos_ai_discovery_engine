import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.rag.vector_store import VectorStore

def main():
    store = VectorStore()
    print("VectorStore data directory:", store.data_dir)
    print("Total documents in VectorStore:", store.count())

    queries = [
        "cannot find old photo keyword search",
        "Ask Photos AI search prompt failure",
        "receipt prescription text search document",
        "face recognition people pets names",
    ]

    for q in queries:
        res = store.query(q, top_k=2)
        print(f"\n{'='*20}\nQuery: '{q}'\n{'='*20}")
        for r in res:
            src = r.get("source", "unknown")
            sim = r.get("similarity", 0.0)
            mode = r.get("search_mode", "unknown")
            quote = r.get("verbatim_quote", "")
            stages = r.get("stages_evidenced", "")
            print(f"  • [{src}] Similarity: {sim:.3f} | Mode: {mode}")
            print(f"    Quote: {quote[:120]}...")
            print(f"    Stages: {stages}")

if __name__ == "__main__":
    main()
