import sqlite3

conn = sqlite3.connect("data/db.sqlite")
c = conn.cursor()

def check_table_counts():
    for tbl in ['documents', 'triage_buckets', 'failure_point_tags', 'hesitation_tags', 'factor_mentions', 'unmet_needs', 'question_mappings']:
        c.execute(f"SELECT count(*) FROM {tbl}")
        print(f"Table {tbl}: {c.fetchone()[0]} rows")

check_table_counts()
