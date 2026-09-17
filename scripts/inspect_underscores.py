import os
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

data_dir = r"c:\Users\THARUN\Videos\AI DISCOVERY ENGINE GOOGLE PHOTOS\dashboard\public\data"

found = []
for f in sorted(os.listdir(data_dir)):
    if f.endswith(".json"):
        path = os.path.join(data_dir, f)
        with open(path, "r", encoding="utf-8") as fp:
            try:
                d = json.load(fp)
                def check_obj(obj, prefix=""):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if isinstance(v, str) and "_" in v:
                                if k in ["label", "name", "title", "headline", "short", "tag_label", "theme", "category"]:
                                    found.append((f, f"{prefix}.{k}", v))
                            elif isinstance(v, (dict, list)):
                                check_obj(v, f"{prefix}.{k}")
                    elif isinstance(obj, list):
                        for i, v in enumerate(obj):
                            if isinstance(v, (dict, list)):
                                check_obj(v, f"{prefix}[{i}]")
                check_obj(d)
            except Exception as e:
                pass

print(f"Total underscore labels found in JSON files: {len(found)}")
for item in found:
    print(f"{item[0]} [{item[1]}]: '{item[2]}'")
