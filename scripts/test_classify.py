import os
import sys
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()

from pipeline.classification.classifier import GeminiClassifier
from pipeline.classification.batch_processor import BatchProcessor

bp = BatchProcessor()
docs = bp.load_clean_docs()
c_ids = bp.load_checkpoint()
unclass = [d for d in docs if d.get('doc_id') not in c_ids][:2]
print(f"Testing classification of {len(unclass)} docs...", flush=True)
gc = GeminiClassifier()
print(f"Models to try: {gc.models_to_try}", flush=True)

import time
t0 = time.time()
try:
    results, err = gc.classify(unclass)
    print(f"Done in {time.time() - t0:.2f}s. Results: {len(results)}, Error: '{err}'", flush=True)
    if results:
        print("First result keys:", list(results[0].keys()), flush=True)
        print("Sample:", results[0].get("doc_id"), results[0].get("wishlist_intent"), flush=True)
except Exception as e:
    print(f"Exception after {time.time() - t0:.2f}s: {e}", flush=True)
