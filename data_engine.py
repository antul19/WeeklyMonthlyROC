import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from config import CURRENT_YEAR

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_seasonality_data_v5(ticker: str, start_year: int, timeframe: str) -> pd.DataFrame | None:
    try:
        start_str = f"{start_year - 1}-11-01"
        interval = "1wk" if timeframe == "Weekly" else "1mo"
        
        # Fetch data
        df = yf.download(ticker, start=start_str, interval=interval, auto_adjust=False, progress=False)
        if df.empty: return None
        
        # Bulletproof column extraction (handles new yfinance MultiIndex updates)
        if isinstance(df.columns, pd.MultiIndex):
            close = df["Close"][ticker]
        else:
            close = df["Close"].squeeze() if isinstance(df["Close"], pd.DataFrame) else df["Close"]
            
        roc = close.dropna().pct_change() * 100
        roc_df = roc.to_frame(name="roc")
        roc_df.index = pd.to_datetime(roc_df.index)
        
        if timeframe == "Weekly":
            roc_df["year"] = roc_df.index.isocalendar().year.astype(int)
            roc_df["period"] = roc_df.index.isocalendar().week.astype(int)
            if roc_df[roc_df["period"] == 53]["year"].nunique() < 3: 
                roc_df = roc_df[roc_df["period"] != 53]
        else:
            roc_df["year"] = roc_df.index.year
            roc_df["period"] = roc_df.index.month
            
        return roc_df[roc_df["year"] >= start_year]
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_presidential_cycle_data() -> pd.DataFrame | None:
    try:
        df = yf.download("^GSPC", start="1980-12-01", interval="1mo", auto_adjust=False, progress=False)
        if df.empty: return None
        
        if isinstance(df.columns, pd.MultiIndex):
            close = df["Close"]["^GSPC"]
        else:
            close = df["Close"].squeeze() if isinstance(df["Close"], pd.DataFrame) else df["Close"]
            
        roc_df = (close.dropna().pct_change() * 100).to_frame(name="roc")
        roc_df.index = pd.to_datetime(roc_df.index)
        roc_df["year"], roc_df["period"] = roc_df.index.year, roc_df.index.month
        return roc_df[roc_df["year"] >= 1981]
    except: return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_global_macro_data() -> dict:
    tickers = {"US (^GSPC)": "^GSPC", "Canada (^GSPTSE)": "^GSPTSE", "India (^NSEI)": "^NSEI", 
               "Gold (GC=F)": "GC=F", "Bitcoin (BTC-USD)": "BTC-USD", "Volatility (^VIX)": "^VIX", 
               "Crude Oil (CL=F)": "CL=F", "10Yr Yield (^TNX)": "^TNX"}
    data_dict = {}
    for name, ticker in tickers.items():
        try:
            df = yf.download(ticker, start="1927-12-01", interval="1d", auto_adjust=False, progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    close = df["Close"][ticker]
                else:
                    close = df["Close"].squeeze() if isinstance(df["Close"], pd.DataFrame) else df["Close"]
                data_dict[name] = close.dropna().resample("ME").last().dropna()
        except: pass
    return data_dict

def compute_seasonality(roc_df: pd.DataFrame, timeframe: str, start_year: int) -> dict:
    periods = list(range(1, 53)) if timeframe == "Weekly" else list(range(1, 13))
    today = datetime.today()
    cur_period = today.isocalendar().week if timeframe == "Weekly" else today.month
    
    cur_data = roc_df[roc_df["year"] == CURRENT_YEAR]
    hist_data = roc_df[roc_df["year"] < CURRENT_YEAR]
    pivot = hist_data.pivot_table(index="year", columns="period", values="roc")
    
    def _avg(p): return p.mean()
    def _wr(p): return (p > 0).sum() / p.notna().sum() * 100
    def _win(p, n): 
        yrs = sorted(p.index.tolist())
        return p.loc[yrs[-n:] if len(yrs) >= n else yrs]
    
    pv5 = _win(pivot, 5)
    pv10 = _win(pivot, 10)
    
    cur_pivot = cur_data.pivot_table(index="year", columns="period", values="roc")
    cur_roc = cur_pivot.iloc[0] if not cur_pivot.empty else pd.Series(dtype=float)
    
    return {
        "periods": periods, "avg_5": _avg(pv5), "avg_10": _avg(pv10), "avg_max": _avg(pivot),
        "wr_5": _wr(pv5), "wr_10": _wr(pv10), "wr_max": _wr(pivot),
        "cur_roc": cur_roc,
        "pivot": pivot, "completed_years": sorted(hist_data["year"].unique()), 
        "current_period": cur_period, "start_year": start_year
    }

def compute_cycle_seasonality(roc_df: pd.DataFrame) -> dict:
    def get_cycle_month(y, m):
        rem = y % 4
        offsets = {1: 0, 2: 12, 3: 24, 0: 36}
        return offsets.get(rem, 0) + m
        
    roc_df["cycle_month"] = roc_df.apply(lambda r: get_cycle_month(r["year"], r["period"]), axis=1)
    start = CURRENT_YEAR - ((CURRENT_YEAR - 1) % 4)
    
    hist_data, cur_data = roc_df[roc_df["year"] < start], roc_df[roc_df["year"] >= start]
    return {
        "avg_roc": hist_data.groupby("cycle_month")["roc"].mean(),
        "cur_roc": cur_data.set_index("cycle_month")["roc"] if not cur_data.empty else pd.Series(dtype=float),
        "current_cycle_start": start
    }

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_sector_data() -> pd.DataFrame | None:
    from config import SECTORS
    tickers = list(SECTORS.values()) + ["SPY"]
    try:
        # Fetch 1 year of daily data to compute accurate moving averages
        df = yf.download(tickers, period="1y", interval="1d", auto_adjust=False, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            return df["Close"].dropna()
        return None 
    except Exception as e:
        print(f"Sector Fetch Error: {e}")
        return None

def compute_rrg(df: pd.DataFrame) -> dict | None:
    if df is None or "SPY" not in df.columns: return None
    
    # 1. Calculate Relative Strength (RS) vs SPY
    rs_df = df.div(df["SPY"], axis=0).drop(columns=["SPY"])
    
    # 2. RS-Ratio (X-Axis): Smoothed 14-week (70 trading days) trend, normalized to 100
    rs_ratio = (rs_df / rs_df.rolling(window=70).mean()) * 100
    
    # 3. RS-Momentum (Y-Axis): Smoothed 2-week (10 trading days) speed of the ratio, normalized to 100
    rs_momentum = (rs_ratio / rs_ratio.rolling(window=10).mean()) * 100
    
    rs_ratio, rs_momentum = rs_ratio.dropna(), rs_momentum.dropna()
    if rs_ratio.empty or rs_momentum.empty: return None
    
    # Return the last 15 days to plot the visual "tail" of the rotation
    tail_length = 15
    return {
        "ratio": rs_ratio.tail(tail_length),
        "momentum": rs_momentum.tail(tail_length),
        "current_date": rs_ratio.index[-1].strftime("%b %d, %Y")
    }
