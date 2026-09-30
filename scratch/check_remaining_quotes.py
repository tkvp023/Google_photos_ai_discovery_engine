import sqlite3
import json
import html
from pathlib import Path

conn = sqlite3.connect('data/db.sqlite')
c = conn.cursor()

def check_quotes(filename, quotes):
    for q in quotes:
        txt = q['text'].strip()
        unescaped = html.unescape(txt)
        match = c.execute('SELECT count(*) FROM documents WHERE INSTR(content, ?) > 0 OR INSTR(content, ?) > 0', (txt, unescaped)).fetchone()[0]
        if match == 0:
            short = unescaped[:40]
            match_short = c.execute('SELECT count(*) FROM documents WHERE INSTR(content, ?) > 0', (short,)).fetchone()[0]
            print(f'FAIL in {filename}: "{txt[:50]}" (short match: {match_short})')
        else:
            print(f'  [VERIFIED] {filename}: "{txt[:60]}..." (Conf: {q.get("confidence")})')

print("Checking Q1 - Q10 quotes:")
total_q = 0
for i in range(1, 11):
    with open(f'dashboard/public/data/q{i}.json', encoding='utf-8') as f:
        d = json.load(f)
        quotes = d.get('key_quotes', [])
        total_q += len(quotes)
        print(f"Q{i} ({len(quotes)} quotes):")
        check_quotes(f'q{i}.json', quotes)

print(f"\nTotal quotes across Q1-Q10: {total_q}")

print("\nChecking systemic_gaps.json quotes:")
with open('dashboard/public/data/systemic_gaps.json', encoding='utf-8') as f:
    d = json.load(f)
    check_quotes('systemic_gaps.json', d.get('key_quotes', []))

print("\nAll checks completed!")
