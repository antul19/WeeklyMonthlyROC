"""
=========================================================
📈 MACRO SEASONALITY DASHBOARD (app.py)
=========================================================
Main Streamlit entry point. Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import io

from config import CURRENT_YEAR, FINANCIAL_CRISES, GEOPOLITICAL_WARS, COLORS, load_css
from data_engine import (
    fetch_seasonality_data_v5, 
    fetch_presidential_cycle_data, 
    fetch_global_macro_data, 
    compute_seasonality, 
    compute_cycle_seasonality, 
    fetch_sector_data, 
    compute_rrg, 
    build_rrg_table,
    fetch_volatility_surface,
    compute_vol_surface_grid
)
from plot_engine import (
    make_bar_chart, 
    make_cumulative_chart, 
    make_presidential_cycle_chart, 
    make_rebased_macro_chart, 
    make_rrg_chart,
    make_volatility_surface_chart
)

# ─────────────────────────────────────────────
# PAGE CONFIG & CSS
# ─────────────────────────────────────────────
st.set_page_config(page_title="Macro Seasonality Terminal", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
st.markdown(load_css(), unsafe_allow_html=True)

def build_csv(data: dict, timeframe: str) -> bytes:
    periods, label, rows = data["periods"], "Week" if timeframe == "Weekly" else "Month", []
    for p in periods:
        rows.append({
            label: p, 
            "Avg_5yr_%": round(data["avg_5"].get(p, np.nan), 4), 
            "Avg_10yr_%": round(data["avg_10"].get(p, np.nan), 4), 
            "Avg_Max_%": round(data["avg_max"].get(p, np.nan), 4), 
            "WinRate_5yr": round(data["wr_5"].get(p, np.nan), 1), 
            "WinRate_10yr": round(data["wr_10"].get(p, np.nan), 1), 
            "WinRate_Max": round(data["wr_max"].get(p, np.nan), 1), 
            f"{CURRENT_YEAR}_Actual_%": round(data["cur_roc"].get(p, np.nan), 4)
        })
    buf = io.BytesIO()
    pd.DataFrame(rows).to_csv(buf, index=False)
    return buf.getvalue()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-header">Configuration</div>', unsafe_allow_html=True)
    ticker = st.text_input("Ticker Symbol", value="QQQ").upper().strip()
    start_year = st.number_input("Start Year", min_value=1950, max_value=CURRENT_YEAR - 1, value=2010)
    timeframe = st.radio("Timeframe", ["Weekly", "Monthly"], horizontal=True)
    show_winrate = st.checkbox("Show Win Rate %", value=True)
    show_spaghetti = st.checkbox("Show All Past Years", value=True)
    
    st.markdown('<div class="section-header">Sector SPDR Dictionary</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: #8d9ab0; line-height: 1.6;">
    <strong>XLK:</strong> Technology<br>
    <strong>XLF:</strong> Financials<br>
    <strong>XLV:</strong> Health Care<br>
    <strong>XLE:</strong> Energy<br>
    <strong>XLY:</strong> Cons. Discretionary<br>
    <strong>XLP:</strong> Cons. Staples<br>
    <strong>XLI:</strong> Industrials<br>
    <strong>XLU:</strong> Utilities<br>
    <strong>XLB:</strong> Materials<br>
    <strong>XLRE:</strong> Real Estate<br>
    <strong>XLC:</strong> Communications
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN HEADER & METRICS
# ─────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="main-title">📈 Macro Seasonality Terminal</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">{ticker} · {timeframe} · Since {start_year}</div>', unsafe_allow_html=True)

with st.spinner(f"Loading {ticker} data…"):
    roc_df = fetch_seasonality_data_v5(ticker, start_year, timeframe)

if roc_df is None or roc_df.empty:
    st.error(f"❌ Could not retrieve data for {ticker}. Please check the symbol.")
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

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Average Returns", 
    "〰️ Cumulative Trend", 
    "🇺🇸 Presidential Cycle", 
    "🌍 Macro Events", 
    "🔄 Sector Rotation",
    "🌊 Volatility Surface"
])

with tab1:
    # Notice the Ticker is now dynamically passed into the title label
    for wk, lbl in [("5", f"{ticker} Average Returns (Last 5 Years)"), 
                    ("10", f"{ticker} Average Returns (Last 10 Years)"), 
                    ("max", f"{ticker} Average Returns (Max Since {start_year})")]: 
        st.plotly_chart(make_bar_chart(data, wk, show_winrate, timeframe, lbl), use_container_width=True)

with tab2:
    # Ticker dynamically added here as well
    for wk, lbl in [("5", f"{ticker} Cumulative Trend (Last 5 Years)"), 
                    ("10", f"{ticker} Cumulative Trend (Last 10 Years)"), 
                    ("max", f"{ticker} Cumulative Trend (Max Since {start_year})")]: 
        st.plotly_chart(make_cumulative_chart(data, wk, show_spaghetti, timeframe, lbl), use_container_width=True)

with tab3:
    spx_df = fetch_presidential_cycle_data()
    if spx_df is not None: 
        st.plotly_chart(make_presidential_cycle_chart(compute_cycle_seasonality(spx_df)), use_container_width=True)

with tab4:
    global_data = fetch_global_macro_data()
    if global_data:
        cols = st.columns(4)
        selected_assets = [name for i, name in enumerate(global_data.keys()) if cols[i % 4].checkbox(name, value=("US" in name or "Gold" in name or "Crude" in name))]
        if selected_assets:
            filtered_data = {k: global_data[k] for k in selected_assets}
            st.plotly_chart(make_rebased_macro_chart(filtered_data, FINANCIAL_CRISES, COLORS["crisis_zone"], "Financial Liquidity Crises"), use_container_width=True)
            st.plotly_chart(make_rebased_macro_chart(filtered_data, GEOPOLITICAL_WARS, COLORS["war_zone"], "Geopolitical Conflicts"), use_container_width=True)

with tab5:
    st.markdown("""
    <div style="background-color: #12151c; border: 1px solid #1e2330; border-left: 3px solid #39FF14; border-radius: 6px; padding: 1rem; margin-bottom: 1rem; font-size: 0.85rem; color: #8d9ab0; line-height: 1.6;">
    <strong>Relative Sector Rotation Graph (RRG):</strong> Maps the 11 major S&P 500 Select Sector SPDRs against the benchmark (SPY). Follow the "tails" to see how capital is currently rotating through the 4 quadrants.<br><br>
    <ul style="margin-top: 0.5rem; margin-bottom: 0;">
        <li><strong style="color:#00E5FF;">LEADING (Top-Right):</strong> Outperforming SPY & accelerating. (Money flowing IN).</li>
        <li><strong style="color:#FF9900;">WEAKENING (Bottom-Right):</strong> Outperforming, but losing speed. (Profit taking).</li>
        <li><strong style="color:#BBBBBB;">LAGGING (Bottom-Left):</strong> Underperforming & decelerating. (Dead money).</li>
        <li><strong style="color:#39FF14;">IMPROVING (Top-Left):</strong> Underperforming, but momentum is rising. (Accumulation).</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Calculating Sector Rotation matrix..."):
        sector_df = fetch_sector_data()
        if sector_df is not None:
            rrg_data = compute_rrg(sector_df)
            if rrg_data:
                
                # --- NEW: Interactive Filtering & Tail Control ---
                st.markdown('<div class="section-header">RRG Controls</div>', unsafe_allow_html=True)
                
                # Use Streamlit columns to put the Filter and Slider side-by-side
                ctrl_col1, ctrl_col2 = st.columns([2, 1])
                
                with ctrl_col1:
                    available_sectors = list(rrg_data['ratio'].columns)
                    selected_sectors = st.multiselect(
                        "Filter Sectors:",
                        options=available_sectors,
                        default=available_sectors
                    )
                
                with ctrl_col2:
                    # Slider to control how many weeks the "tail" reaches back
                    # Default is 15. Max is length of the available smoothed data (usually ~40-50 weeks)
                    max_tail = min(50, len(rrg_data['ratio']))
                    tail_length = st.slider("Tail Length (Trading Days):", min_value=1, max_value=max_tail, value=15)
                
                # Filter the data based on UI inputs
                filtered_rrg_data = {
                    # .tail() limits the lookback window based on the slider
                    "ratio": rrg_data['ratio'][selected_sectors].tail(tail_length),
                    "momentum": rrg_data['momentum'][selected_sectors].tail(tail_length),
                    "current_date": rrg_data['current_date']
                }

                # Render Interactive Plotly Chart
                st.plotly_chart(make_rrg_chart(filtered_rrg_data), use_container_width=True, config={"displayModeBar": False})
                
                # Render Data Table
                st.markdown('<div class="section-header">Current Quadrant Summary</div>', unsafe_allow_html=True)
                # Note: The table always uses the current day (row -1), so tail length doesn't affect it,
                # but we still pass the filtered data so it only shows selected sectors.
                summary_df = build_rrg_table(filtered_rrg_data)
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
                
            else:
                st.error("Failed to compute sector rotation math.")
        else:
            st.error("Failed to fetch underlying sector ETF data.")
with tab6:
    st.markdown("""
    <div style="background-color: #12151c; border: 1px solid #1e2330; border-left: 3px solid #00E5FF; border-radius: 6px; padding: 1rem; margin-bottom: 1rem; font-size: 0.85rem; color: #8d9ab0; line-height: 1.6;">
    <strong>Live Implied Volatility (IV) Surface:</strong> Maps the current options chain for the selected asset. 
    Look for "spikes" or "dents" in the surface to identify mispriced risk. High-elevation areas (Red/Yellow) indicate elevated premiums, ideal for net-credit strategies. Low-elevation valleys (Blue) indicate cheap volatility, ideal for net-debit hedges.
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner(f"Fetching live options chain for {ticker}..."):
        raw_options = fetch_volatility_surface(ticker)
        if raw_options is not None:
            vol_grid = compute_vol_surface_grid(raw_options)
            if vol_grid is not None:
                st.plotly_chart(make_volatility_surface_chart(vol_grid, ticker), use_container_width=True, config={"displayModeBar": False})
            else:
                st.error("Failed to construct the 3D surface matrix. Options data may be too sparse.")
        else:
            st.error(f"No active options data found for {ticker}. Ensure you are searching an asset with liquid options chains (e.g., SPY, QQQ, TSLA).")
# ─────────────────────────────────────────────
# GLOBAL EXPORT SECTION
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Data Export</div>', unsafe_allow_html=True)
st.download_button(
    label=f"⬇️ Download {ticker} Seasonality Data (.csv)", 
    data=build_csv(data, timeframe), 
    file_name=f"{ticker}_{timeframe.lower()}_seasonality.csv", 
    mime="text/csv"
)
