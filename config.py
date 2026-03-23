from datetime import datetime

CURRENT_YEAR = datetime.today().year
PLOTLY_TEMPLATE = "plotly_dark"

COLORS = {
    "pos_bar":    "#555555",   
    "neg_bar":    "#BBBBBB",   
    "cur_year":   "#FFFFFF",                   
    "cur_year_bar": "rgba(255, 255, 255, 0.4)",
    "avg_line":   "#00E5FF",   
    "spaghetti":  "rgba(255, 255, 255, 0.15)", 
    "vline":      "#FF4444",   
    "text_annot": "#cbd5e1",
    "bg":         "#0d0f14",
    "grid":       "#1a1f2e",
    "border":     "#1e2330",
    "cycle_post": "#FF9900",  
    "cycle_mid":  "#B026FF",  
    "cycle_pre":  "#39FF14",  
    "cycle_elec": "#00E5FF",  
    "us":         "#00E5FF",  
    "canada":     "#FF3333",  
    "india":      "#FFA500",  
    "gold":       "#FFD700",  
    "btc":        "#F7931A",  
    "vix":        "#FF00FF",  
    "oil":        "#00FF00",  
    "tnx":        "#B0C4DE",  
    "crisis_zone": "rgba(255, 68, 68, 0.12)",   
    "war_zone":    "rgba(255, 165, 0, 0.15)"    
}

FINANCIAL_CRISES = [
    {"start": "1929-08-01", "end": "1933-03-01", "name": "Great Depression"},
    {"start": "1973-01-01", "end": "1974-12-01", "name": "1970s Stagflation"},
    {"start": "2000-03-01", "end": "2002-10-01", "name": "Dot-Com Crash"},
    {"start": "2007-10-01", "end": "2009-03-01", "name": "Global Fin Crisis"},
    {"start": "2020-02-01", "end": "2020-04-01", "name": "COVID-19 Crash"}
]

GEOPOLITICAL_WARS = [
    {"start": "1939-09-01", "end": "1945-09-02", "name": "World War II"},
    {"start": "1950-06-25", "end": "1953-07-27", "name": "Korean War"},
    {"start": "1962-10-16", "end": "1962-11-20", "name": "Cuban Missile Crisis"},
    {"start": "1964-08-01", "end": "1973-01-27", "name": "Vietnam War (US)"},
    {"start": "1973-10-06", "end": "1974-03-01", "name": "Yom Kippur / Embargo"},
    {"start": "1978-01-01", "end": "1988-08-20", "name": "Iran Rev / Iran-Iraq"},
    {"start": "1990-08-02", "end": "1991-02-28", "name": "Gulf War"},
    {"start": "2001-10-07", "end": "2021-08-30", "name": "Afghanistan War"},
    {"start": "2003-03-20", "end": "2011-12-18", "name": "Iraq War"},
    {"start": "2022-02-24", "end": f"{CURRENT_YEAR}-12-31", "name": "Russia-Ukraine"},
    {"start": "2023-10-07", "end": f"{CURRENT_YEAR}-12-31", "name": "Middle East Conflict"}
]

def load_css():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; background-color: #0d0f14; color: #d4d8e2; }
    .stApp { background-color: #0d0f14; }
    section[data-testid="stSidebar"] { background: #12151c !important; border-right: 1px solid #1e2330; }
    .main-title { font-family: 'IBM Plex Mono', monospace; font-size: 2rem; font-weight: 600; color: #e8ecf5; letter-spacing: -0.02em; margin-bottom: 0.2rem; }
    .sub-title { font-family: 'IBM Plex Sans', sans-serif; font-size: 0.85rem; color: #5a6278; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 1.5rem; }
    .info-box { background: linear-gradient(135deg, #141826 0%, #1a1f2e 100%); border: 1px solid #2a3045; border-left: 3px solid #4a9eff; border-radius: 6px; padding: 1rem 1.2rem; margin-bottom: 1.5rem; font-size: 0.85rem; color: #8d9ab0; line-height: 1.6; }
    .info-box strong { color: #a8b8cc; }
    .metric-card { flex: 1; background: #12151c; border: 1px solid #1e2330; border-radius: 8px; padding: 0.9rem 1.1rem; }
    .metric-label { font-size: 0.7rem; color: #4a5568; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.3rem; }
    .metric-value { font-family: 'IBM Plex Mono', monospace; font-size: 1.4rem; font-weight: 600; color: #e2e8f0; }
    .metric-pos { color: #FFFFFF; } .metric-neg { color: #BBBBBB; }
    .section-header { font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: #4a9eff; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.5rem; margin-top: 1.5rem; border-bottom: 1px solid #1e2330; padding-bottom: 0.4rem; }
    .stTabs [data-baseweb="tab-list"] { background: #12151c; border-bottom: 1px solid #1e2330; gap: 0; }
    .stTabs [data-baseweb="tab"] { font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; color: #5a6278; padding: 0.6rem 1.4rem; border-radius: 0; }
    .stTabs [aria-selected="true"] { color: #4a9eff !important; border-bottom: 2px solid #4a9eff !important; background: transparent !important; }
    .stTextInput input, .stNumberInput input { background: #12151c !important; border: 1px solid #1e2330 !important; color: #d4d8e2 !important; font-family: 'IBM Plex Mono', monospace !important; border-radius: 4px !important; }
    .stDownloadButton button { background: #1a2540 !important; border: 1px solid #2a4070 !important; color: #4a9eff !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 0.8rem !important; }
    </style>
    """

SECTORS = {
    "Tech (XLK)": "XLK", "Financials (XLF)": "XLF", "Healthcare (XLV)": "XLV",
    "Energy (XLE)": "XLE", "Consumer Discretionary (XLY)": "XLY",
    "Consumer Staples (XLP)": "XLP", "Industrials (XLI)": "XLI",
    "Utilities (XLU)": "XLU", "Materials (XLB)": "XLB",
    "Real Estate (XLRE)": "XLRE", "Communication (XLC)": "XLC"
}

SECTOR_COLORS = {
    "XLK": "#00E5FF", "XLF": "#39FF14", "XLV": "#FF3333", "XLE": "#FFA500",
    "XLY": "#FF00FF", "XLP": "#FFFF00", "XLI": "#8A2BE2", "XLU": "#00BFFF",
    "XLB": "#A52A2A", "XLRE": "#FFC0CB", "XLC": "#FFFFFF"
}
