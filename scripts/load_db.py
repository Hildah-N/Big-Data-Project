"""
load_db.py
Loads all 4 tables into SQLite using single-transaction bulk inserts.

Fast because:
  - One BEGIN/COMMIT per table (no per-chunk commits)
  - Indexes dropped before insert, rebuilt after
  - Data already clean from clean.py — no re-validation needed

Run AFTER: clean.py
"""

import sqlite3
import pandas as pd
from pathlib import Path
import time

# ── Config ─────────────────────────────────────────────────────────────────────
DB_PATH = "patent_db"
CLEAN   = Path("data/clean")
CHUNK   = 500_000


# ── Tables config ──────────────────────────────────────────────────────────────
# (csv_file, table_name, columns, indexes)
TABLES = [
    (
        "clean_patents.csv",
        "patents",
        ["patent_id", "title", "abstract", "filing_date", "year"],
        ["idx_year:year"]
    ),
    (
        "clean_inventors.csv",
        "inventors",
        ["inventor_id", "name", "country"],
        ["idx_inv_country:country"]
    ),
    (
        "clean_companies.csv",
        "companies",
        ["company_id", "name"],
        []
    ),
    (
        "clean_relationships.csv",
        "relationships",
        ["patent_id", "inventor_id", "company_id"],
        ["idx_rel_patent:patent_id", "idx_rel_inv:inventor_id", "idx_rel_comp:company_id"]
    ),
]


# ── SQLite speed settings ──────────────────────────────────────────────────────
def optimize_sqlite(conn):
    conn.execute("PRAGMA journal_mode  = WAL;")
    conn.execute("PRAGMA synchronous   = NORMAL;")
    conn.execute("PRAGMA cache_size    = -128000;")  # 128 MB
    conn.execute("PRAGMA temp_store    = MEMORY;")
    conn.execute("PRAGMA foreign_keys  = OFF;")       # re-enabled after all tables load


# ── Load a single table ────────────────────────────────────────────────────────
def load_table(conn, csv_file, table, columns, indexes):
    path = CLEAN / csv_file

    print(f"\n{'─' * 60}")
    print(f"  [{table}]  ←  {csv_file}")
    print(f"{'─' * 60}")

    if not path.exists():
        print(f"  ✗ File not found: {path}")
        return 0

    # Count rows for progress display
    print("  Counting rows...")
    with open(path, encoding="utf-8", errors="ignore") as f:
        total_rows = sum(1 for _ in f) - 1
    print(f"  ✓ {total_rows:,} rows to insert")

    # Clear existing data
    conn.execute(f"DELETE FROM {table}")
    conn.commit()
    print("  ✓ Cleared existing rows")

    # Drop indexes before insert
    for idx_def in indexes:
        idx_name = idx_def.split(":")[0]
        conn.execute(f"DROP INDEX IF EXISTS {idx_name}")
    conn.commit()
    if indexes:
        print(f"  ✓ Dropped indexes")

    # Build insert SQL
    cols_str    = ", ".join(columns)
    placeholders = ", ".join(["?"] * len(columns))
    insert_sql  = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"

    # ── Single transaction for entire table ───────────────────────────────────
    inserted = 0
    t0 = time.time()

    conn.execute("BEGIN")
    for chunk in pd.read_csv(
        path,
        dtype=str,
        chunksize=CHUNK,
        on_bad_lines="skip",
        usecols=columns
    ):
        chunk = chunk.where(pd.notnull(chunk), None)
        conn.executemany(
            insert_sql,
            chunk[columns].itertuples(index=False, name=None)
        )
        inserted += len(chunk)
        elapsed  = time.time() - t0
        rate     = inserted / elapsed if elapsed > 0 else 0
        pct      = inserted / total_rows * 100
        print(
            f"\r  {inserted:>12,} / {total_rows:,}  ({pct:.1f}%)  {rate:,.0f} rows/s",
            end="", flush=True
        )

    conn.execute("COMMIT")

    elapsed = time.time() - t0
    print(f"\r  ✓ Inserted {inserted:,} rows in {int(elapsed//60)}m {int(elapsed%60)}s          ")

    # Rebuild indexes
    if indexes:
        print("  Rebuilding indexes...")
        for idx_def in indexes:
            idx_name, idx_col = idx_def.split(":")
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({idx_col})"
            )
        conn.commit()
        print("  ✓ Indexes rebuilt")

    return inserted


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  DATABASE LOADER")
    print("=" * 60)

    if not CLEAN.exists():
        print(f"\n  ✗ {CLEAN}/ not found. Run clean.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    print(f"\n  ✓ Connected to SQLite → {DB_PATH}")

    optimize_sqlite(conn)

    totals = {}
    t_start = time.time()

    for csv_file, table, columns, indexes in TABLES:
        rows = load_table(conn, csv_file, table, columns, indexes)
        totals[table] = rows

    # Re-enable FK checks after everything is loaded
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.close()

    total_elapsed = time.time() - t_start
    mins = int(total_elapsed // 60)
    secs = int(total_elapsed % 60)

    print(f"\n{'=' * 60}")
    print(f"  ✓ ALL TABLES LOADED  —  {mins}m {secs}s total")
    print(f"{'─' * 60}")
    for table, rows in totals.items():
        print(f"  {table:<20}  {rows:>12,} rows")
    print(f"{'─' * 60}")
    print(f"  Run: python queries.py")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
