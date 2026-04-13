from __future__ import annotations
from sqlalchemy import text
from database import engine, init_db

def run_sql(query: str):
    with engine.begin() as conn:
        result = conn.execute(text(query))
        try:
            rows = result.fetchall()
            return rows
        except Exception:
            return result.rowcount

# Ensure table exists
init_db()

query = """SELECT * FROM appointments"""
print("Before insert:", run_sql(query))

query = """INSERT INTO appointments (patient_name, reason, start_time, canceled, created_at) VALUES('john doe', 'checkup', '2026-03-01 10:00:00', 0, datetime('now'))"""
print("Insert rowcount:", run_sql(query))

print("After insert:", run_sql("SELECT * FROM appointments"))