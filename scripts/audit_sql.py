import os
import re

def audit_sql_queries():
    print("--- Detailed SQL Query Audit in aggregator.py ---")
    with open('pipeline/quantification/aggregator.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        if 'self._q(' in line:
            # check next 10 lines for formatting
            block = "".join(lines[i-1:i+10])
            if 'f"""' in block or "f'''" in block or '.format(' in block or 'f"' in block:
                print(f"Line {i}: dynamic SQL construction:")
                print("   ", line.strip())

if __name__ == "__main__":
    audit_sql_queries()
