import sqlite3
from pathlib import Path

conn = sqlite3.connect("patent_db")
with open("sql/schema.sql") as f:
    conn.executescript(f.read())
conn.close()
print("Tables created successfully!")