
import json
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────────
DB_PATH = "patent_db"
OUTPUT = Path("reports")
OUTPUT.mkdir(parents=True, exist_ok=True)


def get_engine():
    url = f"sqlite:///{DB_PATH}"
    return create_engine(url, echo=False)


def fetch_data(engine):
    """Fetch all data needed for reports"""
    data = {}

    # Totals
    data["total_patents"] = pd.read_sql("SELECT COUNT(*) as n FROM patents", engine).iloc[0]["n"]

    # Top inventors
    data["top_inventors"] = pd.read_sql("""
        SELECT i.name, i.country, COUNT(DISTINCT r.patent_id) as patents
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.inventor_id, i.name, i.country
        ORDER BY patents DESC LIMIT 10
    """, engine)

    # Top companies
    data["top_companies"] = pd.read_sql("""
        SELECT c.name, COUNT(DISTINCT r.patent_id) as patents
        FROM companies c
        JOIN relationships r ON c.company_id = r.company_id
        GROUP BY c.company_id, c.name
        ORDER BY patents DESC LIMIT 10
    """, engine)

    # Top countries
    data["top_countries"] = pd.read_sql("""
        SELECT i.country, COUNT(DISTINCT r.patent_id) as patents,
               ROUND(COUNT(DISTINCT r.patent_id) * 100.0 / (SELECT COUNT(*) FROM patents), 2) as share_pct
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        WHERE i.country NOT IN ('UNKNOWN', '')
        GROUP BY i.country
        ORDER BY patents DESC LIMIT 10
    """, engine)

    # Yearly trends
    data["yearly_trends"] = pd.read_sql("""
        SELECT year, COUNT(*) as patents
        FROM patents WHERE year IS NOT NULL
        GROUP BY year ORDER BY year
    """, engine)

    return data


# A: Console Report
def console_report(data):
    LINE = "=" * 65
    print("\n" + LINE)
    print("                    PATENT INTELLIGENCE REPORT")
    print(f"                    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(LINE)

    print(f"\n TOTAL PATENTS: {data['total_patents']:,}")

    print("\n TOP 10 INVENTORS")
    print("  " + "-" * 50)
    for i, row in data["top_inventors"].iterrows():
        print(f"   {i+1:2}. {row['name'][:35]:<35} {int(row['patents']):>8,} patents  ({row['country']})")

    print("\n TOP 10 COMPANIES")
    print("  " + "-" * 50)
    for i, row in data["top_companies"].iterrows():
        name = row['name'][:40] + "..." if len(str(row['name'])) > 40 else row['name']
        print(f"   {i+1:2}. {name:<43} {int(row['patents']):>8,} patents")

    print("\n TOP 10 COUNTRIES")
    print("  " + "-" * 50)
    for i, row in data["top_countries"].iterrows():
        print(f"   {i+1:2}. {row['country']:<15} {int(row['patents']):>10,} patents  ({row['share_pct']:.1f}%)")

    print("\n YEARLY PATENT TRENDS (Last 10 Years)")
    print("  " + "-" * 50)
    recent = data["yearly_trends"].tail(10)
    max_val = recent["patents"].max() if not recent.empty else 1
    for _, row in recent.iterrows():
        bar = "█" * int(row["patents"] / max_val * 30)
        print(f"   {int(row['year'])}  {bar:<30} {int(row['patents']):>8,}")

    print("\n" + LINE)


# B: CSV Exports
def csv_reports(data):
    files = {
        "top_inventors.csv": data["top_inventors"],
        "top_companies.csv": data["top_companies"],
        "country_trends.csv": data["top_countries"],
    }
    for fname, df in files.items():
        path = OUTPUT / fname
        df.to_csv(path, index=False)
        print(f"  ✓ {fname}")


# C: JSON Report
def json_report(data):
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_patents": int(data["total_patents"]),
        "top_inventors": [
            {"rank": i+1, "name": row["name"], "country": row["country"], "patents": int(row["patents"])}
            for i, row in data["top_inventors"].iterrows()
        ],
        "top_companies": [
            {"rank": i+1, "name": row["name"], "patents": int(row["patents"])}
            for i, row in data["top_companies"].iterrows()
        ],
        "top_countries": [
            {"rank": i+1, "country": row["country"], "patents": int(row["patents"]), "share_pct": float(row["share_pct"])}
            for i, row in data["top_countries"].iterrows()
        ],
        "yearly_trends": [
            {"year": int(row["year"]), "patents": int(row["patents"])}
            for _, row in data["yearly_trends"].iterrows()
        ]
    }

    path = OUTPUT / "report.json"
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"  ✓ report.json")


def main():
    print("=" * 60)
    print("  REPORT GENERATOR")
    print("=" * 60)

    engine = get_engine()
    data = fetch_data(engine)

    print("\n  ── A: Console Report ──")
    console_report(data)

    print("\n  ── B: CSV Exports ──")
    csv_reports(data)

    print("\n  ── C: JSON Report ──")
    json_report(data)

    print(f"\n  ✓ All reports saved to {OUTPUT}/")
    print("=" * 60)


if __name__ == "__main__":
    main()