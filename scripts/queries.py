"""
queries.py
All 7 required SQL queries matching project schema.
Run AFTER: load_db.py
"""

import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────
DB_PATH = "patent_db"
OUTPUT = Path("output")
OUTPUT.mkdir(parents=True, exist_ok=True)


def get_engine():
    url = f"sqlite:///{DB_PATH}"
    return create_engine(url, echo=False)


def run_query(engine, label: str, sql: str, save_as: str = None):
    print(f"\n{'─' * 60}")
    print(f"  {label}")
    print(f"{'─' * 60}")
    df = pd.read_sql(sql, engine)
    print(df.to_string(index=False, max_rows=20))
    if save_as:
        path = OUTPUT / save_as
        df.to_csv(path, index=False)
        print(f"\n  → Saved to: {path}")
    return df


# Q1: Top Inventors
Q1 = """
SELECT 
    i.name,
    i.country,
    COUNT(DISTINCT r.patent_id) AS patent_count
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id, i.name, i.country
ORDER BY patent_count DESC
LIMIT 20;
"""

# Q2: Top Companies
Q2 = """
SELECT 
    c.name,
    COUNT(DISTINCT r.patent_id) AS patent_count
FROM companies c
JOIN relationships r ON c.company_id = r.company_id
GROUP BY c.company_id, c.name
ORDER BY patent_count DESC
LIMIT 20;
"""

# Q3: Top Countries
Q3 = """
SELECT 
    i.country,
    COUNT(DISTINCT r.patent_id) AS patent_count,
    ROUND(COUNT(DISTINCT r.patent_id) * 100.0 / (SELECT COUNT(*) FROM patents), 2) AS share_pct
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
WHERE i.country NOT IN ('UNKNOWN', '')
GROUP BY i.country
ORDER BY patent_count DESC
LIMIT 20;
"""

# Q4: Trends Over Time
Q4 = """
SELECT 
    year,
    COUNT(*) AS patent_count
FROM patents
WHERE year IS NOT NULL
GROUP BY year
ORDER BY year;
"""

# Q5: JOIN Query (patents + inventors + companies)
Q5 = """
SELECT 
    p.patent_id,
    p.title,
    p.filing_date,
    p.year,
    i.name AS inventor_name,
    i.country AS inventor_country,
    c.name AS company_name
FROM patents p
LEFT JOIN relationships r ON p.patent_id = r.patent_id
LEFT JOIN inventors i ON r.inventor_id = i.inventor_id
LEFT JOIN companies c ON r.company_id = c.company_id
WHERE p.year >= 2010
ORDER BY p.filing_date DESC
LIMIT 100;
"""

# Q6: CTE Query
Q6 = """
WITH inventor_patents AS (
    SELECT 
        i.inventor_id,
        i.name,
        i.country,
        COUNT(DISTINCT r.patent_id) AS patent_count
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id, i.name, i.country
),
country_ranked AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY country ORDER BY patent_count DESC) AS rank_in_country
    FROM inventor_patents
    WHERE country NOT IN ('UNKNOWN', '')
)
SELECT 
    country,
    name AS top_inventor,
    patent_count
FROM country_ranked
WHERE rank_in_country <= 3
ORDER BY country, rank_in_country;
"""

# Q7: Ranking Query (Window Functions)
Q7 = """
SELECT 
    i.name,
    i.country,
    COUNT(DISTINCT r.patent_id) AS patent_count,
    RANK() OVER (ORDER BY COUNT(DISTINCT r.patent_id) DESC) AS global_rank,
    DENSE_RANK() OVER (PARTITION BY i.country ORDER BY COUNT(DISTINCT r.patent_id) DESC) AS rank_in_country
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
WHERE i.country NOT IN ('UNKNOWN', '')
GROUP BY i.inventor_id, i.name, i.country
ORDER BY global_rank
LIMIT 30;
"""


def main():
    print("=" * 60)
    print("  PATENT ANALYSIS — 7 REQUIRED QUERIES")
    print("=" * 60)

    engine = get_engine()

    run_query(engine, "Q1: Top Inventors", Q1, "top_inventors.csv")
    run_query(engine, "Q2: Top Companies", Q2, "top_companies.csv")
    run_query(engine, "Q3: Top Countries", Q3, "country_trends.csv")
    run_query(engine, "Q4: Trends Over Time", Q4, "yearly_trends.csv")
    run_query(engine, "Q5: JOIN Query", Q5, "joined_data.csv")
    run_query(engine, "Q6: CTE Query", Q6, "cte_results.csv")
    run_query(engine, "Q7: Ranking Query", Q7, "rankings.csv")

    print("\n" + "=" * 60)
    print("  ✓ ALL 7 QUERIES COMPLETE")
    print("  Run: python report.py")
    print("=" * 60)


if __name__ == "__main__":
    main()