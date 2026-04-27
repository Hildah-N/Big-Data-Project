"""
visualizations.py
Generates and saves charts as PNG files by reading from already-generated CSVs.

Run AFTER: queries.py  (which produces the CSV files)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────
OUTPUT = Path("output")
CHARTS = Path("output/charts")
CHARTS.mkdir(parents=True, exist_ok=True)

# ── Theme ──────────────────────────────────────────────────────────────────────
DARK_BG    = "#0f1624"
GRID_COLOR = "#1e2940"
TEXT_COLOR = "#8899bb"
ACCENT1    = "#3b82f6"
ACCENT2    = "#10b981"
ACCENT3    = "#f59e0b"
ACCENT4    = "#8b5cf6"
ACCENT5    = "#ef4444"
PALETTE    = [ACCENT1, ACCENT2, ACCENT3, ACCENT4, ACCENT5,
              "#06b6d4", "#f97316", "#84cc16", "#e11d48", "#a855f7"]

plt.rcParams.update({
    "figure.facecolor":  DARK_BG,
    "axes.facecolor":    DARK_BG,
    "axes.edgecolor":    GRID_COLOR,
    "axes.labelcolor":   TEXT_COLOR,
    "axes.titlecolor":   "#c8d0e8",
    "xtick.color":       TEXT_COLOR,
    "ytick.color":       TEXT_COLOR,
    "grid.color":        GRID_COLOR,
    "grid.linewidth":    0.5,
    "text.color":        TEXT_COLOR,
    "font.family":       "monospace",
    "axes.titlesize":    12,
    "axes.titleweight":  "bold",
    "axes.labelsize":    9,
    "savefig.facecolor": DARK_BG,
    "savefig.bbox":      "tight",
    "savefig.dpi":       150,
})


# ── Chart 1: Top Inventors ────────────────────────────────────────────────────
def chart_top_inventors():
    print("  [1/6] Top inventors...")
    df = pd.read_csv(OUTPUT / "top_inventors.csv").head(15)

    fig, ax = plt.subplots(figsize=(11, 6))
    df["label"] = df["name"].str[:28]
    bars = ax.barh(df["label"], df["patent_count"], color=ACCENT1, alpha=0.85, height=0.65)
    ax.invert_yaxis()

    for bar, val, country in zip(bars, df["patent_count"], df["country"]):
        ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height() / 2,
                f"{int(val):,}  ({country})", va="center", ha="left",
                fontsize=7.5, color=TEXT_COLOR)

    ax.set_title("Top 15 Inventors by Patent Count", pad=14)
    ax.set_xlabel("Number of Patents")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    ax.spines[["top", "right", "left"]].set_visible(False)
    plt.tight_layout()
    fig.savefig(CHARTS / "01_top_inventors.png")
    plt.close(fig)
    print("     ✓ Saved: 01_top_inventors.png")


# ── Chart 2: Top Companies ────────────────────────────────────────────────────
def chart_top_companies():
    print("  [2/6] Top companies...")
    df = pd.read_csv(OUTPUT / "top_companies.csv").head(15)

    fig, ax = plt.subplots(figsize=(11, 6))
    df["label"] = df["name"].str[:32]
    bars = ax.barh(df["label"], df["patent_count"], color=ACCENT3, alpha=0.85, height=0.65)
    ax.invert_yaxis()

    for bar, val in zip(bars, df["patent_count"]):
        ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height() / 2,
                f"{int(val):,}", va="center", ha="left",
                fontsize=7.5, color=TEXT_COLOR)

    ax.set_title("Top 15 Companies by Patent Portfolio", pad=14)
    ax.set_xlabel("Number of Patents")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    ax.spines[["top", "right", "left"]].set_visible(False)
    plt.tight_layout()
    fig.savefig(CHARTS / "02_top_companies.png")
    plt.close(fig)
    print("     ✓ Saved: 02_top_companies.png")


# ── Chart 3: Top Countries (bar) ──────────────────────────────────────────────
def chart_countries():
    print("  [3/6] Top countries...")
    df = pd.read_csv(OUTPUT / "country_trends.csv").head(20)

    fig, ax = plt.subplots(figsize=(11, 7))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(df))]
    bars = ax.barh(df["country"], df["patent_count"], color=colors, alpha=0.85, height=0.65)
    ax.invert_yaxis()

    for bar, val, pct in zip(bars, df["patent_count"], df["share_pct"]):
        ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height() / 2,
                f"{int(val):,}  ({pct:.1f}%)", va="center", ha="left",
                fontsize=7.5, color=TEXT_COLOR)

    ax.set_title("Top 20 Countries by Patent Output", pad=14)
    ax.set_xlabel("Number of Patents")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    ax.spines[["top", "right", "left"]].set_visible(False)
    plt.tight_layout()
    fig.savefig(CHARTS / "03_top_countries.png")
    plt.close(fig)
    print("     ✓ Saved: 03_top_countries.png")


# ── Chart 4: Patents Per Year (line chart) ────────────────────────────────────
def chart_yearly_trend():
    print("  [4/6] Yearly trend...")
    df = pd.read_csv(OUTPUT / "yearly_trends.csv")
    df = df[df["year"].between(1976, 2025)]

    fig, ax = plt.subplots(figsize=(13, 5))
    ax.fill_between(df["year"], df["patent_count"], alpha=0.12, color=ACCENT1)
    ax.plot(df["year"], df["patent_count"], color=ACCENT1, linewidth=2.2, zorder=3)

    # Highlight peak year
    peak = df.loc[df["patent_count"].idxmax()]
    ax.scatter([peak["year"]], [peak["patent_count"]], color=ACCENT3, s=70, zorder=5)
    ax.annotate(
        f"Peak: {int(peak['year'])}\n{int(peak['patent_count']):,} patents",
        xy=(peak["year"], peak["patent_count"]),
        xytext=(12, 12), textcoords="offset points",
        fontsize=8, color=ACCENT3,
        arrowprops=dict(arrowstyle="->", color=ACCENT3, lw=0.9)
    )

    # Decade markers
    for decade in range(1980, 2030, 10):
        ax.axvline(decade, color=GRID_COLOR, linewidth=0.8, linestyle="--", alpha=0.5)

    ax.set_title("Global Patent Grants Per Year (1976–2025)", pad=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Patents Granted")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    fig.savefig(CHARTS / "04_yearly_trend.png")
    plt.close(fig)
    print("     ✓ Saved: 04_yearly_trend.png")


# ── Chart 5: Patents by Decade (bar) ─────────────────────────────────────────
def chart_decade_breakdown():
    print("  [5/6] Decade breakdown...")
    df = pd.read_csv(OUTPUT / "yearly_trends.csv")
    df = df[df["year"] >= 1970].copy()
    df["decade"] = (df["year"] // 10) * 10
    df = df.groupby("decade")["patent_count"].sum().reset_index()
    df["label"] = df["decade"].astype(str) + "s"

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(df["label"], df["patent_count"],
                  color=PALETTE[:len(df)], alpha=0.85, width=0.6)

    for bar, val in zip(bars, df["patent_count"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + bar.get_height() * 0.015,
                f"{int(val):,}", ha="center", va="bottom",
                fontsize=8, color=TEXT_COLOR)

    ax.set_title("Total Patents Granted by Decade", pad=14)
    ax.set_ylabel("Patents")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    fig.savefig(CHARTS / "05_decade_breakdown.png")
    plt.close(fig)
    print("     ✓ Saved: 05_decade_breakdown.png")


# ── Chart 6: Country Share Pie ────────────────────────────────────────────────
def chart_country_pie():
    print("  [6/6] Country share pie...")
    df = pd.read_csv(OUTPUT / "country_trends.csv")

    top10  = df.head(10).copy()
    others = df.iloc[10:]["patent_count"].sum()
    if others > 0:
        top10 = pd.concat([
            top10,
            pd.DataFrame([{"country": "Others", "patent_count": others, "share_pct": 0}])
        ], ignore_index=True)

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        top10["patent_count"],
        labels=None,
        autopct="%1.1f%%",
        colors=PALETTE[:len(top10)],
        startangle=140,
        pctdistance=0.82,
        wedgeprops=dict(linewidth=0.8, edgecolor=DARK_BG)
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_color("#000000")
        at.set_fontweight("bold")

    ax.legend(wedges, top10["country"],
              loc="lower center", bbox_to_anchor=(0.5, -0.08),
              ncol=4, fontsize=10, frameon=False,
              labelcolor="#e8eaf0",
              prop={"weight": "bold", "size": 10})
    ax.set_title("Global Patent Share by Country (Top 10)", pad=14,
                 fontsize=13, fontweight="bold", color="#000000")
    plt.tight_layout()
    fig.savefig(CHARTS / "06_country_pie.png")
    plt.close(fig)
    print("     ✓ Saved: 06_country_pie.png")

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  VISUALIZATION GENERATOR")
    print("  Reading from: output/*.csv")
    print("=" * 60 + "\n")

    # Check all required CSVs exist
    required = ["top_inventors.csv", "top_companies.csv",
                "country_trends.csv", "yearly_trends.csv"]
    missing = [f for f in required if not (OUTPUT / f).exists()]
    if missing:
        print(f"  ✗ Missing CSV files: {missing}")
        print(f"    Run queries.py first.")
        return

    chart_top_inventors()
    chart_top_companies()
    chart_countries()
    chart_yearly_trend()
    chart_decade_breakdown()
    chart_country_pie()

    print(f"\n{'=' * 60}")
    print(f"  ✓ ALL 6 CHARTS SAVED  →  {CHARTS}/")
    print(f"{'─' * 60}")
    print(f"  01_top_inventors.png    — Top 15 inventors")
    print(f"  02_top_companies.png    — Top 15 companies")
    print(f"  03_top_countries.png    — Top 20 countries")
    print(f"  04_yearly_trend.png     — Patents per year")
    print(f"  05_decade_breakdown.png — Patents by decade")
    print(f"  06_country_pie.png      — Country share pie")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()