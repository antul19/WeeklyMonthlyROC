import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="ETF Seasonality", layout="wide")

st.title("📈 ETF Seasonality Dashboard")
st.markdown("Analyze historical averages, win rates, and cumulative trends.")

# --- UPDATED: Win Rate Explanation with Example ---
st.info("**💡 What is Win Rate?** The Win Rate shows the percentage of time this specific week/month historically ended with a positive return. \n\n*Example: A Win Rate of 80% for Week 12 means that over the last 10 years, Week 12 went UP 8 times and went DOWN 2 times. It helps you identify high-probability seasonal trends rather than just relying on the average return!*")

# --- USER CONTROLS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    ticker = st.text_input("Enter Ticker:", value="QQQ").upper()

with col2:
    start_year = st.number_input("Start Year (For 'Max' Chart):", value=2010, min_value=1950, max_value=datetime.now().year - 1, step=1)

with col3:
    period_type = st.radio("Timeframe:", ["Weekly", "Monthly"], horizontal=True)

with col4:
    st.write("") 
    show_win_rate = st.checkbox("Show Win Rate %", value=True)
    show_spaghetti = st.checkbox("Show All Past Years", value=True)

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

@st.cache_data(ttl=3600)
def get_historical_data(ticker_symbol, interval, start_yr):
    return yf.download(ticker_symbol, start=f"{start_yr}-01-01", interval=interval)

# --- DATA FETCHING ---
with st.spinner(f"Fetching {period_type.lower()} data for {ticker}..."):
    try:
        data = get_historical_data(ticker, yf_interval, start_year)
        
        if data.empty:
            st.error("No data found. Please check the ticker symbol.")
        else:
            df = pd.DataFrame()
            if isinstance(data.columns, pd.MultiIndex):
                df['Close'] = data['Close'].iloc[:, 0]
            else:
                df['Close'] = data['Close']

            df['ROC'] = df['Close'].pct_change() * 100
            
            if period_type == "Weekly":
                df['Year'] = df.index.isocalendar().year
                df[time_col] = df.index.isocalendar().week
            else:
                df['Year'] = df.index.year
                df[time_col] = df.index.month

            current_year = datetime.now().year
            
            df_5yr = df[df['Year'] >= (current_year - 5)]
            df_10yr = df[df['Year'] >= (current_year - 10)]
            df_max = df

            # --- PLOTTING LOGIC SETUP ---
            plt.style.use('dark_background')
            background_color = '#1E1E1E'

            # --- FUNCTION 1: THE BAR CHART ---
            def plot_roc_bars(ax, dataset, title, short_label):
                grid = dataset.pivot_table(values='ROC', index=time_col, columns='Year')
                if period_type == "Weekly" and 53 in grid.index:
                    if grid.loc[53].isna().sum() > (len(grid.columns) / 2):
                        grid = grid.drop(index=53)
                
                if current_year in grid.columns:
                    hist_grid = grid.drop(columns=[current_year])
                else:
                    hist_grid = grid
                
                win_rate_series = (hist_grid > 0).sum(axis=1) / hist_grid.notna().sum(axis=1) * 100
                grid['Average_ROC'] = hist_grid.mean(axis=1)
                
                x_vals = np.array(grid.index.astype(int))
                y_vals = np.array(grid['Average_ROC'])
                win_rates = np.array(win_rate_series)
                
                colors = ['#555555' if val > 0 else '#BBBBBB' for val in y_vals]
                ax.bar(x_vals, y_vals, color=colors, edgecolor='none', label='Historical Avg', zorder=1)
                ax.axhline(0, color='white', linewidth=0.8, alpha=0.5, zorder=2)
                
                if show_win_rate:
                    offset = max(abs(y_vals[~np.isnan(y_vals)])) * 0.08 
                    for i, x in enumerate(x_vals):
                        if not np.isnan(y_vals[i]):
                            y_pos = y_vals[i]
                            wr_text = f"{int(win_rates[i])}%"
                            rot = 90 if period_type == "Weekly" else 0
                            if y_pos > 0:
                                ax.text(x, y_pos + offset, wr_text, ha='center', va='bottom', fontsize=7, color='white', rotation=rot, zorder=4)
                            else:
                                ax.text(x, y_pos - offset, wr_text, ha='center', va='top', fontsize=7, color='white', rotation=rot, zorder=4)

                current_yr_arr = np.full(len(x_vals), np.nan)
                if current_year in grid.columns:
                    current_year_data = grid[current_year]
                    ax.plot(x_vals, current_year_data, color='#FFFFFF', marker='o', markersize=4, 
                            linestyle='-', linewidth=2, label=f'{current_year} Actual ROC', zorder=3)
                    current_yr_arr = np.array(current_year_data)
                
                ax.axvline(x=current_time_val, color='#FF4444', linestyle='--', linewidth=1.5, alpha=0.8, label=f'Current {time_col}', zorder=0)
                ax.set_title(title, fontsize=12, fontweight='bold', color='white', pad=15)
                ax.set_ylabel('ROC (%)', fontsize=9, color='lightgray')
                
                y_min, y_max = ax.get_ylim()
                ax.set_ylim(y_min * 1.25, y_max * 1.25)
                
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
                
                output_df = pd.DataFrame({
                    f'{short_label} Avg ROC (%)': np.round(y_vals, 2),
                    f'{short_label} Win Rate (%)': np.round(win_rates, 1)
                }, index=grid.index)
                if short_label == "Max":
                    output_df[f'{current_year} Actual ROC (%)'] = np.round(current_yr_arr, 2)
                return output_df

            # --- FUNCTION 2: THE CUMULATIVE SPAGHETTI CHART (Anchored to Zero) ---
            def plot_cumulative_lines(ax, dataset, title):
                grid = dataset.pivot_table(values='ROC', index=time_col, columns='Year')
                if period_type == "Weekly" and 53 in grid.index:
                    if grid.loc[53].isna().sum() > (len(grid.columns) / 2):
                        grid = grid.drop(index=53)
                
                if current_year in grid.columns:
                    hist_grid = grid.drop(columns=[current_year])
                else:
                    hist_grid = grid
                
                if show_spaghetti:
                    for yr in hist_grid.columns:
                        yr_data = hist_grid[yr].dropna()
                        if not yr_data.empty:
                            cum_yr_data = ((1 + yr_data / 100).cumprod() - 1) * 100
                            
                            # --- FIXED: Insert a "0" starting point for the spaghetti lines ---
                            x_yr_anchored = np.insert(yr_data.index.astype(int).values, 0, 0)
                            y_yr_anchored = np.insert(cum_yr_data.values, 0, 0.0)
                            
                            ax.plot(x_yr_anchored, y_yr_anchored, color='white', alpha=0.15, linewidth=1, zorder=1)

                avg_roc = hist_grid.mean(axis=1)
                cum_avg_roc = ((1 + avg_roc / 100).cumprod() - 1) * 100
                
                x_vals = np.array(grid.index.astype(int))
                
                # --- FIXED: Insert a "0" starting point for the Average line ---
                x_vals_anchored = np.insert(x_vals, 0, 0)
                cum_avg_anchored = np.insert(cum_avg_roc.values, 0, 0.0)
                
                ax.plot(x_vals_anchored, cum_avg_anchored, color='#00E5FF', linewidth=3, label='Historical Average Path', zorder=2)
                ax.axhline(0, color='white', linewidth=0.8, alpha=0.5, zorder=0)
                
                if current_year in grid.columns:
                    current_roc = grid[current_year].dropna() 
                    if not current_roc.empty:
                        cum_current_roc = ((1 + current_roc / 100).cumprod() - 1) * 100
                        
                        # --- FIXED: Insert a "0" starting point for the Current Year line ---
                        x_curr_anchored = np.insert(current_roc.index.astype(int).values, 0, 0)
                        y_curr_anchored = np.insert(cum_current_roc.values, 0, 0.0)
                        
                        ax.plot(x_curr_anchored, y_curr_anchored, color='#FFFFFF', 
                                marker='o', markersize=4, linestyle='-', linewidth=2.5, label=f'{current_year} Actual Path', zorder=3)
                
                ax.axvline(x=current_time_val, color='#FF4444', linestyle='--', linewidth=1.5, alpha=0.8, label=f'Current {time_col}', zorder=0)
                
                ax.set_title(title, fontsize=12, fontweight='bold', color='white', pad=15)
                ax.set_ylabel('Cumulative Return (%)', fontsize=9, color='lightgray')
                
                # Use the anchored x_vals to ensure '0' shows up neatly on the x-axis
                ax.set_xticks(x_vals_anchored)
                ax.tick_params(axis='x', labelsize=8, colors='lightgray')
                ax.tick_params(axis='y', labelsize=8, colors='lightgray')
                ax.grid(axis='y', linestyle=':', color='gray', alpha=0.3)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('gray')
                ax.spines['bottom'].set_color('gray')
                ax.set_facecolor(background_color)
                
                handles, labels = ax.get_legend_handles_labels()
                by_label = dict(zip(labels, handles))
                ax.legend(by_label.values(), by_label.keys(), loc='upper left', fontsize=8, framealpha=0.2, facecolor=background_color)

            # --- STREAMLIT TABS IMPLEMENTATION ---
            tab1, tab2 = st.tabs(["📊 Average Returns (Bars)", "📈 Cumulative Trend (Lines)"])
            
            with tab1:
                fig1, axes1 = plt.subplots(nrows=3, ncols=1, figsize=(11, 14), facecolor=background_color, dpi=300)
                title_suffix = "| Win Rate % | Current Year" if show_win_rate else "| Current Year"
                
                df1 = plot_roc_bars(axes1[0], df_5yr, f"{ticker} 5-Year Average {title_suffix}", "5-Yr")
                df2 = plot_roc_bars(axes1[1], df_10yr, f"{ticker} 10-Year Average {title_suffix}", "10-Yr")
                df3 = plot_roc_bars(axes1[2], df_max, f"{ticker} Max (Since {start_year}) Average {title_suffix}", "Max")

                axes1[2].set_xlabel(x_label, fontsize=10, color='lightgray', labelpad=10)
                plt.tight_layout(pad=3.0)
                st.pyplot(fig1, width='stretch')
                
            with tab2:
                fig2, axes2 = plt.subplots(nrows=3, ncols=1, figsize=(11, 14), facecolor=background_color, dpi=300)
                
                plot_cumulative_lines(axes2[0], df_5yr, f"{ticker} 5-Year Cumulative Seasonality")
                plot_cumulative_lines(axes2[1], df_10yr, f"{ticker} 10-Year Cumulative Seasonality")
                plot_cumulative_lines(axes2[2], df_max, f"{ticker} Max (Since {start_year}) Cumulative Seasonality")

                axes2[2].set_xlabel(x_label, fontsize=10, color='lightgray', labelpad=10)
                plt.tight_layout(pad=3.0)
                st.pyplot(fig2, width='stretch')

            # --- CSV DOWNLOAD ---
            combined_data = pd.concat([df1, df2, df3], axis=1)
            combined_data.index.name = time_col
            
            @st.cache_data
            def convert_df_to_csv(df):
                return df.to_csv().encode('utf-8')
                
            csv_data = convert_df_to_csv(combined_data)
            
            st.markdown("### 📊 Raw Data Export")
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv_data,
                file_name=f"{ticker}_{period_type}_Seasonality_Data.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")
