"""
dashboard.py — Global Patent Intelligence Dashboard
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Patent Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,600;9..144,700&family=Instrument+Sans:wght@400;500;600&family=Fira+Code:wght@400;500&display=swap');

    :root {
        --cream:      #faf8f4;
        --warm-white: #f5f2ec;
        --paper:      #ede9e0;
        --border:     #ddd8ce;
        --border-md:  #c8c2b6;
        --ink:        #1a1714;
        --ink-soft:   #3d3830;
        --ink-muted:  #6b6257;
        --ink-faint:  #9c9287;
        --cobalt:     #1d4ed8;
        --cobalt-lt:  #3b6ef5;
        --cobalt-bg:  rgba(29,78,216,0.07);
        --cobalt-bd:  rgba(29,78,216,0.18);
        --teal:       #0d9488;
        --shadow-sm:  0 1px 4px rgba(26,23,20,0.07);
        --shadow-md:  0 4px 20px rgba(26,23,20,0.10);
        --shadow-lg:  0 12px 40px rgba(26,23,20,0.13);
    }

    html, body, [class*="css"] {
        font-family: 'Instrument Sans', sans-serif;
        color: var(--ink);
    }

    .stApp {
        background-color: var(--cream);
        background-image:
            radial-gradient(ellipse 70% 40% at 100% 0%, rgba(29,78,216,0.05) 0%, transparent 60%),
            radial-gradient(ellipse 50% 30% at 0% 100%, rgba(13,148,136,0.04) 0%, transparent 55%);
    }

    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding-top: 2.2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1360px;
    }

    /* ── HERO ── */
    .hero {
        padding: 0.5rem 0 1rem;
        border-bottom: 1.5px solid var(--border);
        margin-bottom: 1.6rem;
    }
    .hero-title {
        font-family: 'Fraunces', serif;
        font-size: clamp(1.4rem, 2.5vw, 2rem);
        font-weight: 700;
        color: var(--ink);
        letter-spacing: -0.02em;
        line-height: 1;
        margin: 0;
    }
    .hero-title .accent { color: var(--cobalt); }
    .hero-rule {
        width: 36px;
        height: 2px;
        background: linear-gradient(90deg, var(--cobalt), var(--teal));
        border-radius: 2px;
        margin-top: 1rem;
    }

    /* ── KPI CARDS ── */
    [data-testid="metric-container"] {
        background: #ffffff !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 14px !important;
        padding: 20px 22px !important;
        box-shadow: var(--shadow-sm) !important;
        transition: box-shadow 0.22s, border-color 0.22s, transform 0.18s;
        position: relative;
        overflow: hidden;
    }
    [data-testid="metric-container"]::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--cobalt), var(--teal));
        opacity: 0;
        transition: opacity 0.22s;
    }
    [data-testid="metric-container"]:hover {
        border-color: var(--cobalt-bd) !important;
        box-shadow: var(--shadow-md), 0 0 0 3px var(--cobalt-bg) !important;
        transform: translateY(-3px);
    }
    [data-testid="metric-container"]:hover::after { opacity: 1; }

    [data-testid="metric-container"] label {
        font-family: 'Fira Code', monospace !important;
        font-size: 0.62rem !important;
        color: var(--ink-faint) !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Fraunces', serif !important;
        font-size: 2.1rem !important;
        font-weight: 600 !important;
        color: var(--ink) !important;
        letter-spacing: -0.03em !important;
        line-height: 1.1 !important;
    }

    hr {
        border: none !important;
        border-top: 1.5px solid var(--border) !important;
        margin: 1.4rem 0 !important;
    }

    /* ── SECTION HEADER ── */
    .sec {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 1.8rem 0 1.2rem;
    }
    .sec-icon {
        width: 32px; height: 32px;
        background: var(--cobalt-bg);
        border: 1px solid var(--cobalt-bd);
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
        color: var(--cobalt);
    }
    .sec-icon svg { width: 15px; height: 15px; }
    .sec-label {
        font-family: 'Fira Code', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: var(--ink-muted);
    }
    .sec-line { flex: 1; height: 1px; background: var(--border); }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--warm-white) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 2px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
        color: var(--ink-muted) !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 7px 18px !important;
        border: none !important;
        transition: all 0.15s !important;
        font-family: 'Instrument Sans', sans-serif !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff !important;
        font-weight: 700 !important;
        background: #1d4ed8 !important;
    }
    .stTabs [aria-selected="true"] {
        background: #1d4ed8 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: var(--shadow-sm) !important;
        border: none !important;
    }
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] { display: none !important; }

    /* ── CHART IMAGES ── */
    .stImage img {
        border-radius: 12px !important;
        border: 1.5px solid var(--border) !important;
        box-shadow: var(--shadow-sm) !important;
        transition: box-shadow 0.25s, transform 0.25s !important;
        background: #fff;
    }
    .stImage img:hover {
        transform: scale(1.012) !important;
        box-shadow: var(--shadow-lg) !important;
    }

    /* ── INSIGHT CARD ── */
    .insight {
        background: #fff;
        border: 1.5px solid var(--border);
        border-radius: 12px;
        padding: 20px 22px;
        box-shadow: var(--shadow-sm);
    }
    .insight-head {
        font-family: 'Fraunces', serif;
        font-size: 1rem;
        font-weight: 600;
        color: var(--ink);
        margin-bottom: 10px;
        letter-spacing: -0.02em;
    }
    .insight p {
        font-size: 0.82rem;
        color: var(--ink-muted);
        line-height: 1.7;
        margin: 0 0 12px;
    }
    .insight-list { list-style: none; padding: 0; margin: 0; }
    .insight-list li {
        font-size: 0.8rem;
        color: var(--ink-soft);
        padding: 5px 0;
        border-bottom: 1px solid var(--border);
        display: flex; align-items: center; gap: 8px;
    }
    .insight-list li:last-child { border-bottom: none; }
    .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--cobalt); flex-shrink: 0; }
    .chip {
        display: inline-block;
        background: var(--cobalt-bg);
        border: 1px solid var(--cobalt-bd);
        border-radius: 6px;
        padding: 2px 9px;
        font-family: 'Fira Code', monospace;
        font-size: 0.62rem;
        color: var(--cobalt);
        letter-spacing: 0.06em;
        margin: 8px 3px 0 0;
    }

    /* ── MISSING CHART ── */
    .no-chart {
        background: var(--warm-white);
        border: 1.5px dashed var(--border-md);
        border-radius: 12px;
        padding: 3rem;
        text-align: center;
        color: var(--ink-faint);
        font-family: 'Fira Code', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.08em;
    }

    /* ── FOOTER ── */
    .footer {
        text-align: center;
        font-family: 'Fira Code', monospace;
        font-size: 0.62rem;
        color: var(--ink-faint);
        letter-spacing: 0.1em;
        padding: 1.8rem 0 0.5rem;
        border-top: 1.5px solid var(--border);
        margin-top: 2.5rem;
    }
    .footer a { color: var(--cobalt); text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# ── Paths / DB ────────────────────────────────────────────────────────────────
DB_PATH = "patent_db"
OUTPUT  = Path("output")
CHARTS  = OUTPUT / "charts"

@st.cache_resource
def get_engine():
    return create_engine(f"sqlite:///{DB_PATH}", echo=False)

@st.cache_data(ttl=600)
def load_totals():
    engine = get_engine()
    return pd.read_sql("""
        SELECT
            (SELECT COUNT(*) FROM patents)                                      AS total_patents,
            (SELECT COUNT(*) FROM inventors)                                    AS total_inventors,
            (SELECT COUNT(*) FROM companies)                                    AS total_companies,
            (SELECT COUNT(*) FROM relationships WHERE inventor_id IS NOT NULL)  AS inv_links,
            (SELECT COUNT(*) FROM relationships WHERE company_id IS NOT NULL)   AS comp_links
    """, engine).iloc[0]

# ── Helpers ───────────────────────────────────────────────────────────────────
def chart(name, caption=""):
    path = CHARTS / name
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.markdown(
            f'<div class="no-chart">CHART UNAVAILABLE &nbsp;·&nbsp; {name}</div>',
            unsafe_allow_html=True,
        )

# Real Lucide SVG icons (inline, no CDN dependency)
ICON = {
    "trend": """<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
        <polyline points="16 7 22 7 22 13"/></svg>""",

    "users": """<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>""",

    "building": """<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <path d="M9 3v18"/><path d="M3 9h6"/><path d="M3 15h6"/>
        <path d="M15 9h.01"/><path d="M15 15h.01"/>
        <path d="M19 9h.01"/><path d="M19 15h.01"/></svg>""",

    "globe": """<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <line x1="2" y1="12" x2="22" y2="12"/>
        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>""",
}

def section(icon_key, label):
    st.markdown(f"""
    <div class="sec">
        <div class="sec-icon">{ICON[icon_key]}</div>
        <span class="sec-label">{label}</span>
        <div class="sec-line"></div>
    </div>
    """, unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">Global Patent <span class="accent">Intelligence</span></div>
    <div class="hero-rule"></div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
totals = load_totals()
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Patents",  f"{int(totals.total_patents):,}")
k2.metric("Inventors",      f"{int(totals.total_inventors):,}")
k3.metric("Companies",      f"{int(totals.total_companies):,}")
k4.metric("Inventor Links", f"{int(totals.inv_links):,}")
k5.metric("Company Links",  f"{int(totals.comp_links):,}")

st.markdown("<br/>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Trends", "Inventors", "Companies", "Countries"])

with tab1:
    section("trend", "Patent Activity Over Time")
    c1, c2 = st.columns([2, 1])
    with c1:
        chart("04_yearly_trend.png", "Patents Granted Per Year")
    with c2:
        chart("05_decade_breakdown.png", "Distribution by Decade")

with tab2:
    section("users", "Top Inventors by Patent Volume")
    c1, c2 = st.columns([3, 2])
    with c1:
        chart("01_top_inventors.png", "Top Inventors")
    with c2:
        st.markdown("""
        <div class="insight">
            <div class="insight-head">Key Insight</div>
            <p>Top inventors are concentrated in three global innovation hubs, reflecting
            decades of strategic R&amp;D investment.</p>
            <ul class="insight-list">
                <li><span class="dot"></span>United States — Silicon Valley &amp; Research Triangle</li>
                <li><span class="dot"></span>Japan — Tokyo &amp; Osaka tech corridors</li>
                <li><span class="dot"></span>Germany — Munich &amp; Stuttgart clusters</li>
            </ul>
            <div style="margin-top:14px">
                <span class="chip">Semiconductors</span>
                <span class="chip">Biotech</span>
                <span class="chip">Automotive</span>
                <span class="chip">Software</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    section("building", "Top Companies by Patent Portfolio")
    chart("02_top_companies.png", "Top Companies")

with tab4:
    section("globe", "Global Patent Distribution")
    c1, c2 = st.columns([2, 1])
    with c1:
        chart("03_top_countries.png", "Top Countries by Volume")
    with c2:
        chart("06_country_pie.png", "Global Share")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Global Patent Intelligence &nbsp;·&nbsp; Built with Streamlit &nbsp;·&nbsp;
    Data: <a href="https://patentsview.org" target="_blank">USPTO PatentsView</a>
</div>
""", unsafe_allow_html=True)