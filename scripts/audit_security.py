import os
import re
import sys

def audit_codebase():
    issues = []
    
    # 1. Check SQL formatting in python files
    print("--- 1. Auditing SQL Queries for Injection Risks ---")
    sql_patterns = [
        (re.compile(r'execute\(\s*f["\']', re.IGNORECASE), "f-string inside execute() call"),
        (re.compile(r'execute\([^,]+\.format\(', re.IGNORECASE), ".format() inside execute() call"),
        (re.compile(r'execute\([^,]+%\s*\(', re.IGNORECASE), "% operator inside execute() call"),
    ]
    for root, dirs, files in os.walk('.'):
        if any(d in root for d in ['.git', 'node_modules', '.next', 'venv', '__pycache__']):
            continue
        for f in files:
            if f.endswith('.py'):
                p = os.path.join(root, f)
                with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                    for i, line in enumerate(fp, 1):
                        for pat, desc in sql_patterns:
                            if pat.search(line):
                                issues.append((p, i, "SQL_INJECTION_RISK", desc, line.strip()[:100]))
                                
    # 2. Check for dangerouslySetInnerHTML in TSX files
    print("--- 2. Auditing XSS / dangerouslySetInnerHTML in Frontend ---")
    for root, dirs, files in os.walk('dashboard'):
        if any(d in root for d in ['node_modules', '.next']):
            continue
        for f in files:
            if f.endswith(('.tsx', '.ts')):
                p = os.path.join(root, f)
                with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                    for i, line in enumerate(fp, 1):
                        if 'dangerouslySetInnerHTML' in line:
                            issues.append((p, i, "XSS_RISK", "dangerouslySetInnerHTML usage", line.strip()[:100]))

    # 3. Check for hardcoded API keys / tokens
    print("--- 3. Auditing Hardcoded Secrets ---")
    secret_pat = re.compile(r'(?:api[_-]?key|secret|password|token)\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']', re.IGNORECASE)
    for root, dirs, files in os.walk('.'):
        if any(d in root for d in ['.git', 'node_modules', '.next', 'venv', '__pycache__', '.env']):
            continue
        for f in files:
            if f.endswith(('.py', '.ts', '.tsx', '.json', '.yaml', '.yml')) and not f.endswith('package-lock.json'):
                p = os.path.join(root, f)
                with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                    for i, line in enumerate(fp, 1):
                        if secret_pat.search(line) and 'process.env' not in line and 'os.getenv' not in line:
                            issues.append((p, i, "SECRET_EXPOSURE", "Potential hardcoded secret", line.strip()[:100]))

    # 4. Check for unhandled exceptions or missing alt / aria tags in JSX
    print("--- 4. Auditing Accessibility & Accessibility Tags in JSX ---")
    img_no_alt = re.compile(r'<img\b(?![^>]*\balt=)[^>]*>', re.IGNORECASE)
    btn_no_label = re.compile(r'<button\b(?![^>]*\b(?:aria-label|aria-labelledby)=)[^>]*>\s*<svg', re.IGNORECASE)
    for root, dirs, files in os.walk('dashboard'):
        if any(d in root for d in ['node_modules', '.next']):
            continue
        for f in files:
            if f.endswith(('.tsx', '.jsx')):
                p = os.path.join(root, f)
                with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    for m in img_no_alt.finditer(content):
                        issues.append((p, 0, "A11Y_NO_ALT", "<img> tag missing alt attribute", m.group(0)[:80]))

    print(f"\nTotal potential findings: {len(issues)}")
    for file, line, cat, desc, snippet in issues:
        print(f"[{cat}] {file}:{line} - {desc}\n  --> {snippet}")

if __name__ == "__main__":
    audit_codebase()
