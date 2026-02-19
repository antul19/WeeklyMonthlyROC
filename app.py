import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# --- PAGE SETUP ---
# This makes the app look good on mobile
st.set_page_config(page_title="ETF Seasonality", layout="centered")

st.title("📈 ETF Weekly Seasonality")
st.markdown("Analyze historical weekly average returns for any ETF or stock.")

# --- USER INPUT ---
# Creates a text box on the website. Defaults to "QQQ".
ticker = st.text_input("Enter Ticker Symbol:", value="QQQ").upper()

# --- DATA FETCHING ---
# We use a spinner to show the user that data is loading
with st.spinner(f"Fetching data for {ticker}..."):
    try:
        data = yf.download(ticker, start="2010-01-01", interval="1wk")
        
        if data.empty:
            st.error("No data found. Please check the ticker symbol.")
        else:
            df = pd.DataFrame()
            if isinstance(data.columns, pd.MultiIndex):
                df['Close'] = data['Close'].iloc[:, 0]
            else:
                df['Close'] = data['Close']

            df['ROC'] = df['Close'].pct_change() * 100
            df['Year'] = df.index.isocalendar().year
            df['Week'] = df.index.isocalendar().week

            current_year = datetime.now().year
            df_5yr = df[df['Year'] > (current_year - 5)]
            df_10yr = df[df['Year'] > (current_year - 10)]
            df_max = df

            # --- PLOTTING LOGIC ---
            plt.style.use('dark_background')
            background_color = '#1E1E1E'

            def plot_roc_bars(ax, dataset, title):
                grid = dataset.pivot_table(values='ROC', index='Week', columns='Year')
                if 53 in grid.index and grid.loc[53].isna().sum() > (len(grid.columns) / 2):
                    grid = grid.drop(index=53)
                    
                grid['Average_ROC'] = grid.mean(axis=1)
                x_vals = np.array(grid.index.astype(int))
                y_vals = np.array(grid['Average_ROC'])
                
                colors = ['#555555' if val > 0 else '#BBBBBB' for val in y_vals]
                ax.bar(x_vals, y_vals, color=colors, edgecolor='none')
                ax.axhline(0, color='white', linewidth=0.8, alpha=0.5)
                
                current_week = datetime.now().isocalendar()[1]
                ax.axvline(x=current_week, color='#FF4444', linestyle='-', linewidth=1.5, alpha=0.8, label=f'Current Week ({current_week})')
                
                ax.set_title(title, fontsize=12, fontweight='bold', color='white', pad=10)
                ax.set_ylabel('Avg ROC (%)', fontsize=9, color='lightgray')
                ax.set_xticks(x_vals)
                ax.tick_params(axis='x', labelsize=8, colors='lightgray')
                ax.tick_params(axis='y', labelsize=8, colors='lightgray')
                ax.grid(axis='y', linestyle=':', color='gray', alpha=0.3)
                
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('gray')
                ax.spines['bottom'].set_color('gray')
                ax.set_facecolor(background_color)
                ax.legend(loc='upper right', fontsize=8, framealpha=0.2, facecolor=background_color)

            fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10, 12), facecolor=background_color)

            plot_roc_bars(axes[0], df_5yr, f"{ticker} 5-Year Average Weekly ROC")
            plot_roc_bars(axes[1], df_10yr, f"{ticker} 10-Year Average Weekly ROC")
            plot_roc_bars(axes[2], df_max, f"{ticker} Max (Since 2010) Average Weekly ROC")

            axes[2].set_xlabel('Week Number of the Year (1-52)', fontsize=10, color='lightgray', labelpad=10)
            plt.tight_layout(pad=3.0)

            # --- DISPLAY ON WEBSITE ---
            # Instead of plt.show(), we pass the figure to Streamlit
            st.pyplot(fig)

    except Exception as e:
        st.error(f"An error occurred: {e}")