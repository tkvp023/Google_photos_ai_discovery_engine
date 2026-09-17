import os
from dotenv import load_dotenv
load_dotenv()
from apify_client import ApifyClient

client = ApifyClient(os.getenv("APIFY_API_TOKEN"))
runs = client.runs().list(limit=10)
print(f"Total runs found: {len(runs.items)}")
for r in runs.items:
    rid = getattr(r, "id", None) or (r.get("id") if isinstance(r, dict) else "")
    status = getattr(r, "status", None) or (r.get("status") if isinstance(r, dict) else "")
    ds_id = getattr(r, "default_dataset_id", None) or (r.get("defaultDatasetId") if isinstance(r, dict) else "")
    started = getattr(r, "started_at", None) or (r.get("startedAt") if isinstance(r, dict) else "")
    print(f"Run: {rid} | Status: {status} | Dataset: {ds_id} | Started: {started}")
    if ds_id:
        try:
            ds = client.dataset(ds_id).get()
            count = ds.get("itemCount", 0) if isinstance(ds, dict) else getattr(ds, "item_count", 0)
            print(f"   -> Dataset {ds_id}: {count} items")
        except Exception as e:
            print(f"   -> Error: {e}")
