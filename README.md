# 📈 Quantitative ETF & Macro Seasonality Dashboard

An institutional-grade, web-based financial dashboard built with Python, Streamlit, and Plotly. This tool provides deep quantitative insights into historical market seasonality, the US Presidential Cycle, and global macroeconomic resilience.

Built for traders and analysts looking for a statistical edge in options trading, sector rotation, and macro-trend identification.

## ✨ Features

The dashboard is split into four highly focused analytical modules:

### 1. 📊 Average Returns & Win Rates (The Micro Edge)
* Analyze the historical seasonality of **any** ticker available on Yahoo Finance (Equities, ETFs, Indices).
* Toggle between **Weekly** or **Monthly** timeframes.
* Calculates the historical **Win Rate** (percentage of time a period closes positive) and average return for 5-Year, 10-Year, and Maximum Lookback windows.
* Overlays the current year's actual performance against historical averages.

### 2. 〰️ Cumulative Trend Paths (The Trend Edge)
* Visualizes the compounding historical trajectory of an asset over a calendar year.
* Displays "spaghetti" plots of all past years to visualize variance and volatility.
* Tracks the current year's cumulative return in real-time to identify if an asset is front-running or lagging its historical baseline.

### 3. 🇺🇸 48-Month Presidential Cycle (The Macro Edge)
* A fixed, unrolled 48-month timeline tracking the S&P 500 (`^GSPC`) since 1981.
* Maps the exact historical average path of the Post-Election, Midterm, Pre-Election, and Election years.
* Overlays the current administration's exact performance to visualize broader macroeconomic flows and typical midterm drawdowns.

### 4. 🌍 Global Macro Resilience (The Crisis Edge)
* A dynamic, interactive Logarithmic-scale chart tracking asset classes through a century of macroeconomic shocks.
* Automatically rebases selected assets to 100 at their earliest shared date to create a fair percentage-growth race.
* **Includes assets:** S&P 500 (US), TSX Composite (Canada), Nifty 50 (India), Gold, Bitcoin, Crude Oil, 10-Year Treasury Yield, and the VIX.
* Features historical shaded zones for major crises: *The Great Depression, WWII, 1970s Inflation, Dot-Com Crash, 2008 Financial Crisis, and the COVID-19 Crash.*

### 5. Stramlit link
 * https://neveapqwhvsq7hthmce4ib.streamlit.app/
