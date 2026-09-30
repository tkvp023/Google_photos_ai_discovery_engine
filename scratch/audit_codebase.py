import os
import re
import sys

def audit():
    print("=== Antigravity Codebase Vulnerability & Bug Audit ===")
    
    # 1. SQL Injection Scan (f-strings / formatting in SQL execution)
    sql_patterns = [
        re.compile(r'\.execute\(\s*f["\']'),
        re.compile(r'\.execute\([^,)]*%\s*'),
        re.compile(r'\.execute\([^,)]*\+\s*'),
        re.compile(r'_fetch_quotes\([^,)]*f["\']')
    ]
    
    sql_issues = []
    
    # 2. Hardcoded Secrets / Keys
    secret_patterns = [
        re.compile(r'(?i)(api[_-]?key|secret[_-]?key|password|token)\s*=\s*["\'][a-zA-Z0-9_\-]{8,}["\']')
    ]
    secret_issues = []
    
    # 3. Bare except clauses (swallowing exceptions completely)
    bare_except_pattern = re.compile(r'^\s*except\s*:')
    bare_excepts = []
    
    # 4. Open redirects / CORS wildcard issues
    cors_pattern = re.compile(r'allow_origins\s*=\s*\[\s*["\']\*["\']\s*\]')
    cors_issues = []

    # 5. Database session leaks (session = get_session() without close or try/finally)
    unclosed_sessions = []
    
    # Walk directory
    for root, dirs, files in os.walk('.'):
        if any(ignored in root for ignored in ['.git', 'node_modules', '.next', '.gemini', 'venv', '__pycache__']):
            continue
            
        for fname in files:
            fpath = os.path.join(root, fname)
            
            # Python files audit
            if fname.endswith('.py'):
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.splitlines()
                    
                    # Session leak check
                    if 'get_session()' in content and 'session.close()' not in content and 'with get_session()' not in content:
                        unclosed_sessions.append((fpath, "Session opened but never closed or wrapped in with/finally"))
                        
                    for idx, line in enumerate(lines, 1):
                        # SQL injections
                        for pat in sql_patterns:
                            if pat.search(line):
                                sql_issues.append((fpath, idx, line.strip()))
                                
                        # Secret checks
                        for pat in secret_patterns:
                            if pat.search(line):
                                # Ignore mock/test placeholders
                                if not any(mock in line.lower() for mock in ['mock', 'dummy', 'test', 'example', 'placeholder', 'none', 'env']):
                                    secret_issues.append((fpath, idx, line.strip()))
                                    
                        # Bare except
                        if bare_except_pattern.search(line):
                            bare_excepts.append((fpath, idx, line.strip()))
                            
                        # CORS
                        if cors_pattern.search(line):
                            cors_issues.append((fpath, idx, line.strip()))

    print(f"\n[1] Potential SQL Injection / Dynamic SQL formatting: {len(sql_issues)}")
    for f, l, txt in sql_issues[:15]:
        print(f"  {f}:{l} -> {txt}")
        
    print(f"\n[2] Hardcoded Secrets: {len(secret_issues)}")
    for f, l, txt in secret_issues[:10]:
        print(f"  {f}:{l} -> {txt}")
        
    print(f"\n[3] Bare Excepts (Silent Crash / Blind Swallowing): {len(bare_excepts)}")
    for f, l, txt in bare_excepts[:10]:
        print(f"  {f}:{l} -> {txt}")
        
    print(f"\n[4] Insecure CORS Configuration: {len(cors_issues)}")
    for f, l, txt in cors_issues:
        print(f"  {f}:{l} -> {txt}")
        
    print(f"\n[5] Potential DB Session Leaks: {len(unclosed_sessions)}")
    for f, issue in unclosed_sessions:
        print(f"  {f} -> {issue}")

if __name__ == '__main__':
    audit()
