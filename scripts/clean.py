"""
clean.py - FINAL CORRECT VERSION
Fixes:
  - Proper joins (no broken merges)
  - Filing dates + year correctly populated
  - Maintains relational integrity
"""

import pandas as pd
from pathlib import Path

# Paths
RAW = Path("data/raw")
CLEAN = Path("data/clean")
CLEAN.mkdir(parents=True, exist_ok=True)

# Limit ONLY base table
NROWS = None


# ============================================================
# 1. PATENTS
# ============================================================
def clean_patents():
    print("[1/4] Cleaning patents...")

    # Base table (LIMITED)
    patents = pd.read_csv(
        RAW / "g_patent.tsv",
        sep="\t",
        usecols=["patent_id", "patent_title"],
        nrows=NROWS,
        dtype={"patent_id": str},
        on_bad_lines="skip",
        low_memory=False
    )

    # FULL abstracts (no limit)
    abstracts = pd.read_csv(
        RAW / "g_patent_abstract.tsv",
        sep="\t",
        usecols=["patent_id", "patent_abstract"],
        dtype={"patent_id": str},
        on_bad_lines="skip",
        low_memory=False
    )

    # FULL applications (no limit)
    applications = pd.read_csv(
        RAW / "g_application.tsv",
        sep="\t",
        usecols=["patent_id", "filing_date"],
        dtype={"patent_id": str},
        on_bad_lines="skip",
        low_memory=False
    )

    # Filter to only needed IDs
    abstracts = abstracts[abstracts["patent_id"].isin(patents["patent_id"])]
    applications = applications[applications["patent_id"].isin(patents["patent_id"])]

    # Merge
    df = patents.merge(abstracts, on="patent_id", how="left")
    df = df.merge(applications, on="patent_id", how="left")

    # Dates
    df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce")
    df["year"] = df["filing_date"].dt.year
    df["filing_date"] = df["filing_date"].dt.strftime("%Y-%m-%d")

    # Rename
    df = df.rename(columns={"patent_title": "title", "patent_abstract": "abstract"})

    # Select columns
    df = df[["patent_id", "title", "abstract", "filing_date", "year"]]

    # Clean
    df = df.dropna(subset=["patent_id", "title"])
    df = df.drop_duplicates(subset=["patent_id"])
    df["title"] = df["title"].astype(str).str.strip()
    df["abstract"] = df["abstract"].fillna("").astype(str).str.strip()

    # Save
    df.to_csv(CLEAN / "clean_patents.csv", index=False, na_rep='\\N')
    print(f"   ✓ {len(df):,} patents")


# ============================================================
# 2. INVENTORS
# ============================================================
def clean_inventors():
    print("[2/4] Cleaning inventors...")

    inventors = pd.read_csv(
        RAW / "g_inventor_disambiguated.tsv",
        sep="\t",
        usecols=["inventor_id", "disambig_inventor_name_first",
                 "disambig_inventor_name_last", "location_id"],
        nrows=NROWS,
        dtype={"inventor_id": str, "location_id": str},
        on_bad_lines="skip",
        low_memory=False
    )

    locations = pd.read_csv(
        RAW / "g_location_disambiguated.tsv",
        sep="\t",
        usecols=["location_id", "disambig_country"],
        dtype={"location_id": str},
        on_bad_lines="skip",
        low_memory=False
    ).drop_duplicates(subset=["location_id"])

    df = inventors.merge(locations, on="location_id", how="left")

    df["name"] = (
        df["disambig_inventor_name_first"].fillna("") + " " +
        df["disambig_inventor_name_last"].fillna("")
    ).str.strip()
    df.loc[df["name"] == "", "name"] = "Unknown"

    df["country"] = df["disambig_country"].fillna("UNKNOWN").str.upper()

    df = df[["inventor_id", "name", "country"]]
    df = df.dropna(subset=["inventor_id"]).drop_duplicates(subset=["inventor_id"])

    df.to_csv(CLEAN / "clean_inventors.csv", index=False, na_rep='\\N')
    print(f"   ✓ {len(df):,} inventors")


# ============================================================
# 3. COMPANIES
# ============================================================
def clean_companies():
    print("[3/4] Cleaning companies...")

    df = pd.read_csv(
        RAW / "g_assignee_disambiguated.tsv",
        sep="\t",
        usecols=["assignee_id", "disambig_assignee_organization"],
        nrows=NROWS,
        dtype={"assignee_id": str},
        on_bad_lines="skip",
        low_memory=False
    )

    df = df.rename(columns={
        "assignee_id": "company_id",
        "disambig_assignee_organization": "name"
    })

    df = df[["company_id", "name"]]
    df = df.dropna(subset=["company_id", "name"])
    df = df.drop_duplicates(subset=["company_id"])
    df["name"] = df["name"].astype(str).str.strip()

    df.to_csv(CLEAN / "clean_companies.csv", index=False, na_rep='\\N')
    print(f"   ✓ {len(df):,} companies")


# ============================================================
# 4. RELATIONSHIPS
# ============================================================
def clean_relationships():
    print("[4/4] Cleaning relationships...")

    inv_links = pd.read_csv(
        RAW / "g_inventor_disambiguated.tsv",
        sep="\t",
        usecols=["patent_id", "inventor_id"],
        nrows=NROWS,
        dtype={"patent_id": str, "inventor_id": str},
        on_bad_lines="skip",
        low_memory=False
    ).dropna().drop_duplicates()

    inv_links["company_id"] = None

    comp_links = pd.read_csv(
        RAW / "g_assignee_disambiguated.tsv",
        sep="\t",
        usecols=["patent_id", "assignee_id"],
        nrows=NROWS,
        dtype={"patent_id": str, "assignee_id": str},
        on_bad_lines="skip"
    ).dropna().drop_duplicates()

    comp_links = comp_links.rename(columns={"assignee_id": "company_id"})
    comp_links["inventor_id"] = None

    df = pd.concat([inv_links, comp_links], ignore_index=True)
    df = df[["patent_id", "inventor_id", "company_id"]]
    df = df.dropna(subset=["patent_id"]).drop_duplicates()

    df.to_csv(CLEAN / "clean_relationships.csv", index=False, na_rep='\\N')
    print(f"   ✓ {len(df):,} relationships")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  CLEANING PIPELINE (FINAL CORRECT VERSION)")
    print("=" * 60 + "\n")

    clean_patents()
    clean_inventors()
    clean_companies()
    clean_relationships()

    print("\n" + "=" * 60)
    print("  ✓ CLEANING COMPLETE")
    print("  Run: python scripts/load_db.py")
    print("=" * 60)
