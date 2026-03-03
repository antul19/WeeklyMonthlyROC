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
from datetime import datetime
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
# CUSTOM CSS
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
