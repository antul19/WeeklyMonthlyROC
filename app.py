import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="ETF Seasonality", layout="centered")

st.title("📈 ETF Seasonality Dashboard")
st.markdown("Analyze historical average returns for any ETF or stock.")

# --- USER CONTROLS ---
# Put the inputs side-by-side using Streamlit columns
col1, col2 = st.columns(2)

with col1:
    ticker = st.text_input("Enter Ticker Symbol:", value="QQQ").upper()

with col2:
    # --- NEW: The Toggle Switch ---
    period_type = st.radio("Select Timeframe:", ["Weekly", "Monthly"], horizontal=True)

# Set dynamic variables based on the toggle
if period_type == "Weekly":
    yf_interval = "1wk"
    time_col = "Week"
    x_label = "Week Number of the Year (1-52)"
    current_time_val = datetime.now().isocalendar()[1]
else:
    yf_interval = "1mo"
    time_col = "Month"
    x_label = "Month of the Year (1-12)"
    current_time_val = datetime.now().month

# --- DATA FETCHING ---
with st.spinner(f"Fetching {period_type.lower()} data for {ticker}..."):
    try:
        # Pass the dynamic interval to yfinance
        data = yf.download(ticker, start="2010-01-01", interval=yf_interval)
        
        if data.empty:
            st.error("No data found. Please check the ticker symbol.")
        else:
            df = pd.DataFrame()
            if isinstance(data.columns, pd.MultiIndex):
                df['Close'] = data['Close'].iloc[:, 0]
            else:
                df['Close'] = data['Close']

            df['ROC'] = df['Close'].pct_change() * 100
            
            # --- NEW: Dynamic Date Extraction ---
            if period_type == "Weekly":
                df['Year'] = df.index.isocalendar().year
                df[time_col] = df.index.isocalendar().week
            else:
                df['Year'] = df.index.year
                df[time_col] = df.index.month

            current_year = datetime.now().year
            df_5yr = df[df['Year'] > (current_year - 5)]
            df_10yr = df[df['Year'] > (current_year - 10)]
            df_max = df

            # --- PLOTTING LOGIC ---
            plt.style.use('dark_background')
            background_color = '#1E1E1E'

            def plot_roc_bars(ax, dataset, title):
                # Pivot dynamically based on Week or Month
                grid = dataset.pivot_table(values='ROC', index=time_col, columns='Year')
                
                # Only try to drop week 53 if we are looking at Weekly data
                if period_type == "Weekly" and 53 in grid.index:
                    if grid.loc[53].isna().sum() > (len(grid.columns) / 2):
                        grid = grid.drop(index=53)
                        
                grid['Average_ROC'] = grid.mean(axis=1)
                x_vals = np.array(grid.index.astype(int))
                y_vals = np.array(grid['Average_ROC'])
                
                colors = ['#555555' if val > 0 else '#BBBBBB' for val in y_vals]
                ax.bar(x_vals, y_vals, color=colors, edgecolor='none')
                ax.axhline(0, color='white', linewidth=0.8, alpha=0.5)
                
                # Draw the dynamic red line
                ax.axvline(x=current_time_val, color='#FF4444', linestyle='-', linewidth=1.5, alpha=0.8, label=f'Current {time_col} ({current_time_val})')
                
                ax.set_title(title, fontsize=12, fontweight='bold', color='white', pad=10)
                ax.set_ylabel('Avg ROC (%)', fontsize=9, color='lightgray')
                
                # Ensure every tick is shown (1-12 or 1-52)
                ax.set_xticks(x_vals)
                ax.tick_params(axis='x', labelsize=8, colors='lightgray')
                ax.tick_params(axis='y', labelsize=8, colors='lightgray')
                ax.grid(axis='y', linestyle=':', color='gray', alpha=0.3)
                
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('gray')
                ax.spines['bottom'].set_color('gray')
                ax.set_facecolor(background_color)
                ax.legend(loc='upper left', fontsize=8, framealpha=0.2, facecolor=background_color)

            fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10, 12), facecolor=background_color)

            plot_roc_bars(axes[0], df_5yr, f"{ticker} 5-Year Average {period_type} ROC")
            plot_roc_bars(axes[1], df_10yr, f"{ticker} 10-Year Average {period_type} ROC")
            plot_roc_bars(axes[2], df_max, f"{ticker} Max (Since 2010) Average {period_type} ROC")

            axes[2].set_xlabel(x_label, fontsize=10, color='lightgray', labelpad=10)
            plt.tight_layout(pad=3.0)

            st.pyplot(fig)

    except Exception as e:
        st.error(f"An error occurred: {e}")