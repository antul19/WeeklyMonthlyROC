import streamlit as st
import pandas as pd
import numpy as np
import io
from config import CURRENT_YEAR, FINANCIAL_CRISES, GEOPOLITICAL_WARS, COLORS, load_css
from data_engine import fetch_seasonality_data_v5, fetch_presidential_cycle_data, fetch_global_macro_data, compute_seasonality, compute_cycle_seasonality
from plot_engine import make_bar_chart, make_cumulative_chart, make_presidential_cycle_chart, make_rebased_macro_chart
from data_engine import fetch_seasonality_data_v5, fetch_presidential_cycle_data, fetch_global_macro_data, compute_seasonality, compute_cycle_seasonality, fetch_sector_data, compute_rrg
from plot_engine import make_bar_chart, make_cumulative_chart, make_presidential_cycle_chart, make_rebased_macro_chart, make_rrg_chart

st.set_page_config(page_title="ETF Seasonality Dashboard", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
st.markdown(load_css(), unsafe_allow_html=True)

def build_csv(data: dict, timeframe: str) -> bytes:
    periods, label, rows = data["periods"], "Week" if timeframe == "Weekly" else "Month", []
    for p in periods:
        rows.append({label: p, "Avg_5yr_%": round(data["avg_5"].get(p, np.nan), 4), "Avg_10yr_%": round(data["avg_10"].get(p, np.nan), 4), "Avg_Max_%": round(data["avg_max"].get(p, np.nan), 4), "WinRate_5yr": round(data["wr_5"].get(p, np.nan), 1), "WinRate_10yr": round(data["wr_10"].get(p, np.nan), 1), "WinRate_Max": round(data["wr_max"].get(p, np.nan), 1), f"{CURRENT_YEAR}_Actual_%": round(data["cur_roc"].get(p, np.nan), 4)})
    buf = io.BytesIO()
    pd.DataFrame(rows).to_csv(buf, index=False)
    return buf.getvalue()

with st.sidebar:
    st.markdown('<div class="section-header">Configuration</div>', unsafe_allow_html=True)
    ticker = st.text_input("Ticker Symbol", value="QQQ").upper().strip()
    start_year = st.number_input("Start Year", min_value=1950, max_value=CURRENT_YEAR - 1, value=2010)
    timeframe = st.radio("Timeframe", ["Weekly", "Monthly"], horizontal=True)
    show_winrate = st.checkbox("Show Win Rate %", value=True)
    show_spaghetti = st.checkbox("Show All Past Years", value=True)

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="main-title">📈 ETF Seasonality Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">{ticker} · {timeframe} · Since {start_year}</div>', unsafe_allow_html=True)

with st.spinner(f"Loading {ticker} data…"):
    roc_df = fetch_seasonality_data_v5(ticker, start_year, timeframe)

if roc_df is None or roc_df.empty:
    st.error(f"❌ Could not retrieve data for {ticker}.")
    st.stop()

data = compute_seasonality(roc_df, timeframe, start_year)
cur_p = data["current_period"]
am, wm, ac = data["avg_max"].get(cur_p, np.nan), data["wr_max"].get(cur_p, np.nan), data["cur_roc"].get(cur_p, np.nan)

m1, m2, m3, m4 = st.columns(4)
m1.markdown(f'<div class="metric-card"><div class="metric-label">Avg Return</div><div class="metric-value">{f"{am:+.2f}%" if not pd.isna(am) else "—"}</div></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="metric-card"><div class="metric-label">Win Rate</div><div class="metric-value">{f"{wm:.0f}%" if not pd.isna(wm) else "—"}</div></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="metric-card"><div class="metric-label">{CURRENT_YEAR} Actual</div><div class="metric-value">{f"{ac:+.2f}%" if not pd.isna(ac) else "N/A"}</div></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="metric-card"><div class="metric-label">Dataset Years</div><div class="metric-value">{len(data["completed_years"])}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Average Returns", "〰️ Cumulative Trend", "🇺🇸 Presidential Cycle", "🌍 Macro Events", "🔄 Sector Rotation"])

with tab1:
    for wk, lbl in [("5", "Last 5 Years"), ("10", "Last 10 Years"), ("max", "Max")]: st.plotly_chart(make_bar_chart(data, wk, show_winrate, timeframe, lbl), use_container_width=True)

with tab2:
    for wk, lbl in [("5", "Last 5 Years"), ("10", "Last 10 Years"), ("max", "Max")]: st.plotly_chart(make_cumulative_chart(data, wk, show_spaghetti, timeframe, lbl), use_container_width=True)

with tab3:
    spx_df = fetch_presidential_cycle_data()
    if spx_df is not None: st.plotly_chart(make_presidential_cycle_chart(compute_cycle_seasonality(spx_df)), use_container_width=True)

with tab4:
    global_data = fetch_global_macro_data()
    if global_data:
        cols = st.columns(4)
        selected_assets = [name for i, name in enumerate(global_data.keys()) if cols[i % 4].checkbox(name, value=("US" in name or "Gold" in name or "Crude" in name))]
        if selected_assets:
            filtered_data = {k: global_data[k] for k in selected_assets}
            st.plotly_chart(make_rebased_macro_chart(filtered_data, FINANCIAL_CRISES, COLORS["crisis_zone"], "Financial Crises"), use_container_width=True)
            st.plotly_chart(make_rebased_macro_chart(filtered_data, GEOPOLITICAL_WARS, COLORS["war_zone"], "Geopolitical Conflicts"), use_container_width=True)

with tab5:
    st.markdown("""
    <div style="background-color: #12151c; border: 1px solid #1e2330; border-left: 3px solid #39FF14; border-radius: 6px; padding: 1rem; margin-bottom: 1rem; font-size: 0.85rem; color: #8d9ab0; line-height: 1.6;">
    <strong>Relative Sector Rotation Graph (RRG):</strong> Maps the 11 major S&P 500 Select Sector SPDRs against the benchmark (SPY). Follow the "tails" to see how capital is currently rotating through the 4 quadrants (Leading, Weakening, Lagging, Improving).<br><br>
    <strong>Sector Ticker Legend:</strong>
    <div style="display: flex; flex-wrap: wrap; margin-top: 0.3rem; font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem;">
        <div style="width: 33%;"><strong>XLK:</strong> Technology</div>
        <div style="width: 33%;"><strong>XLF:</strong> Financials</div>
        <div style="width: 33%;"><strong>XLV:</strong> Health Care</div>
        <div style="width: 33%;"><strong>XLE:</strong> Energy</div>
        <div style="width: 33%;"><strong>XLY:</strong> Cons. Discretionary</div>
        <div style="width: 33%;"><strong>XLP:</strong> Cons. Staples</div>
        <div style="width: 33%;"><strong>XLI:</strong> Industrials</div>
        <div style="width: 33%;"><strong>XLU:</strong> Utilities</div>
        <div style="width: 33%;"><strong>XLB:</strong> Materials</div>
        <div style="width: 33%;"><strong>XLRE:</strong> Real Estate</div>
        <div style="width: 33%;"><strong>XLC:</strong> Communications</div>
    </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Calculating Sector Rotation matrix..."):
        sector_df = fetch_sector_data()
        if sector_df is not None:
            rrg_data = compute_rrg(sector_df)
            if rrg_data:
                st.plotly_chart(make_rrg_chart(rrg_data), use_container_width=True, config={"displayModeBar": False})
            else:
                st.error("Failed to compute sector rotation math.")
        else:
            st.error("Failed to fetch underlying sector ETF data.")
            

st.download_button("⬇️ Download CSV", build_csv(data, timeframe), f"{ticker}_seasonality.csv", "text/csv")
