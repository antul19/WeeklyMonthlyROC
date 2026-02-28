"""
ETF Seasonality Dashboard
=========================
A professional, web-based ETF seasonality analysis tool built with Streamlit + Plotly.
Run: streamlit run etf_seasonality_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import io

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ETF Seasonality Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — dark, refined, financial aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0d0f14;
    color: #d4d8e2;
}

.stApp { background-color: #0d0f14; }

section[data-testid="stSidebar"] {
    background: #12151c !important;
    border-right: 1px solid #1e2330;
}

.main-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: #e8ecf5;
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}
.sub-title {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.85rem;
    color: #5a6278;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

.info-box {
    background: linear-gradient(135deg, #141826 0%, #1a1f2e 100%);
    border: 1px solid #2a3045;
    border-left: 3px solid #4a9eff;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: 1.5rem;
    font-size: 0.85rem;
    color: #8d9ab0;
    line-height: 1.6;
}
.info-box strong { color: #a8b8cc; }

.metric-row { display: flex; gap: 12px; margin-bottom: 1.5rem; }
.metric-card {
    flex: 1;
    background: #12151c;
    border: 1px solid #1e2330;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
}
.metric-label {
    font-size: 0.7rem;
    color: #4a5568;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}
.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.4rem;
    font-weight: 600;
    color: #e2e8f0;
}
.metric-pos { color: #FFFFFF; } 
.metric-neg { color: #BBBBBB; } 

.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: #4a9eff;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 0.5rem;
    margin-top: 1.5rem;
    border-bottom: 1px solid #1e2330;
    padding-bottom: 0.4rem;
}

.stTabs [data-baseweb="tab-list"] {
    background: #12151c;
    border-bottom: 1px solid #1e2330;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    color: #5a6278;
    padding: 0.6rem 1.4rem;
    border-radius: 0;
    letter-spacing: 0.05em;
}
.stTabs [aria-selected="true"] {
    color: #4a9eff !important;
    border-bottom: 2px solid #4a9eff !important;
    background: transparent !important;
}

.stTextInput input, .stNumberInput input {
    background: #12151c !important;
    border: 1px solid #1e2330 !important;
    color: #d4d8e2 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    border-radius: 4px !important;
}
.stRadio label, .stCheckbox label { color: #8d9ab0 !important; font-size: 0.85rem !important; }
.stRadio [data-testid="stRadio"] > div { gap: 0.5rem; }

.stDownloadButton button {
    background: #1a2540 !important;
    border: 1px solid #2a4070 !important;
    color: #4a9eff !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    border-radius: 4px !important;
    letter-spacing: 0.05em;
}
.stDownloadButton button:hover {
    background: #223060 !important;
    border-color: #4a9eff !important;
}

.stSpinner { color: #4a9eff; }
.js-plotly-plot { border-radius: 6px; }
.stAlert { border-radius: 6px; font-size: 0.85rem; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #1e2330; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2a3045; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS & THEME
# ─────────────────────────────────────────────
CURRENT_YEAR = datetime.today().year
PLOTLY_TEMPLATE = "plotly_dark"

COLORS = {
    "pos_bar":    "#555555",   
    "neg_bar":    "#BBBBBB",   
    "cur_year":   "#FFFFFF",                   # Bold white for Cumulative Chart
    "cur_year_bar": "rgba(255, 255, 255, 0.4)",# Dull, semi-transparent white for Bar Chart line
    "avg_line":   "#00E5FF",   
    "spaghetti":  "rgba(255, 255, 255, 0.15)", 
    "vline":      "#FF4444",   
    "text_annot": "#cbd5e1",
    "bg":         "#0d0f14",
    "grid":       "#1a1f2e",
    "border":     "#1e2330",
}

# ─────────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(ticker: str, start_year: int) -> pd.DataFrame | None:
    try:
        start_str = f"{start_year}-01-01"
        df = yf.download(ticker, start=start_str, auto_adjust=True, progress=False)
        if df.empty: return None
        close = df["Close"]
        if isinstance(close, pd.DataFrame): close = close.squeeze()
        close = close.dropna()
        close.index = pd.to_datetime(close.index)
        return close.to_frame(name="close")
    except Exception:
        return None

def compute_seasonality(df: pd.DataFrame, timeframe: str, start_year: int) -> dict:
    close = df["close"].copy()

    if timeframe == "Weekly":
        resampled = close.resample("W-FRI").last().dropna()
        roc = resampled.pct_change().dropna() * 100
        roc.index = pd.to_datetime(roc.index)
        roc_df = roc.to_frame(name="roc")
        roc_df["year"] = roc_df.index.isocalendar().year.astype(int)
        roc_df["period"] = roc_df.index.isocalendar().week.astype(int)
        w53_years = roc_df[roc_df["period"] == 53]["year"].nunique()
        if w53_years < 3: roc_df = roc_df[roc_df["period"] != 53]
    else:
        resampled = close.resample("ME").last().dropna()
        roc = resampled.pct_change().dropna() * 100
        roc.index = pd.to_datetime(roc.index)
        roc_df = roc.to_frame(name="roc")
        roc_df["year"] = roc_df.index.year
        roc_df["period"] = roc_df.index.month

    today = datetime.today()
    current_period = today.isocalendar().week if timeframe == "Weekly" else today.month

    cur_year_data = roc_df[roc_df["year"] == CURRENT_YEAR].copy()
    hist_data = roc_df[roc_df["year"] < CURRENT_YEAR].copy()

    completed_years = sorted(hist_data["year"].unique())
    pivot = hist_data.pivot_table(index="year", columns="period", values="roc")
    periods = sorted(pivot.columns.tolist())

    def _avg(pivot_subset): return pivot_subset.mean()
    def _winrate(pivot_subset): return (pivot_subset > 0).sum() / pivot_subset.notna().sum() * 100
    def _window(pivot, n):
        years = sorted(pivot.index.tolist())
        subset = years[-n:] if len(years) >= n else years
        return pivot.loc[subset]

    pv5, pv10, pvmax = _window(pivot, 5), _window(pivot, 10), pivot 
    avg_5, avg_10, avg_max = _avg(pv5), _avg(pv10), _avg(pvmax)
    wr_5, wr_10, wr_max = _winrate(pv5), _winrate(pv10), _winrate(pvmax)

    cur_pivot = cur_year_data.pivot_table(index="year", columns="period", values="roc")
    cur_roc = cur_pivot.iloc[0] if not cur_pivot.empty else pd.Series(dtype=float)

    return {
        "periods": periods, "avg_5": avg
