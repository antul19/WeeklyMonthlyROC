import plotly.graph_objects as go
import pandas as pd
import numpy as np
from config import COLORS, PLOTLY_TEMPLATE, CURRENT_YEAR

def _base_layout(title: str, height: int = 380) -> dict:
    return dict(
        template=PLOTLY_TEMPLATE, paper_bgcolor=COLORS["bg"], plot_bgcolor=COLORS["bg"],
        title=dict(text=title, font=dict(family="IBM Plex Mono", size=13, color="#8d9ab0"), x=0.01),
        height=height, margin=dict(l=50, r=20, t=40, b=50),
        xaxis=dict(gridcolor=COLORS["grid"], linecolor=COLORS["border"], showline=True),
        yaxis=dict(gridcolor=COLORS["grid"], linecolor=COLORS["border"], zeroline=True, zerolinecolor="#2a3045"),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.08, x=0), hovermode="x unified"
    )

def make_bar_chart(data: dict, window_key: str, show_winrate: bool, timeframe: str, title: str) -> go.Figure:
    avg, wr, cur, periods, cur_p = data[f"avg_{window_key}"], data[f"wr_{window_key}"], data["cur_roc"], data["periods"], data["current_period"]
    bar_colors = [COLORS["pos_bar"] if v >= 0 else COLORS["neg_bar"] for v in avg.reindex(periods).fillna(0)]
    wr_text = [f"{wr.get(p, np.nan):.0f}%" if show_winrate and not pd.isna(wr.get(p, np.nan)) else "" for p in periods]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=periods, y=avg.reindex(periods).values, text=wr_text, textposition='outside', marker_color=bar_colors, name="Hist. Avg"))
    cur_x = [p for p in periods if p in cur.index]
    if cur_x:
        fig.add_trace(go.Scatter(x=cur_x, y=[cur[p] for p in cur_x], mode="lines+markers", line=dict(color=COLORS["cur_year_bar"], width=2), marker=dict(size=7, color="#FFFFFF", line=dict(color="#000000", width=1.5)), name=f"{CURRENT_YEAR} Actual"))
    
    if cur_p in periods: fig.add_vline(x=cur_p, line_dash="dash", line_color=COLORS["vline"])
    
    layout = _base_layout(title)
    layout["xaxis"].update(title="Week" if timeframe == "Weekly" else "Month", dtick=1, range=[0.5, (52 if timeframe=="Weekly" else 12) + 0.5])
    layout["yaxis"]["ticksuffix"] = "%"
    fig.update_layout(**layout)
    return fig

def make_cumulative_chart(data: dict, window: str, show_spaghetti: bool, timeframe: str, title: str) -> go.Figure:
    """Renders the compounding historical trajectory, highlighting best/worst years."""
    fig = go.Figure()
    
    # ─────────────────────────────────────────────
    # Pull colors from config.py
    # ─────────────────────────────────────────────
    COLOR_CURRENT = COLORS["trend_current"]
    COLOR_AVG = COLORS["trend_avg"]
    COLOR_BEST = COLORS["trend_best"]
    COLOR_WORST = COLORS["trend_worst"]
    COLOR_SPAGHETTI = COLORS["trend_spaghetti"]

    # --- NEW: Calculate cumulative paths directly from the pivot table ---
    yearly_cum = {}
    if "pivot" in data:
        for yr in data["pivot"].columns:
            # Drop empty weeks/months so the math works perfectly
            s = data["pivot"][yr].dropna()
            # Calculate the compounding return: (1 + ROC) * (1 + ROC) ...
            yearly_cum[yr] = (1 + s / 100).cumprod() * 100 - 100

    # 1. Determine which years are included in this specific lookback window
    included_years = []
    if window == "5":
        included_years = [y for y in data["completed_years"] if y >= CURRENT_YEAR - 5]
    elif window == "10":
        included_years = [y for y in data["completed_years"] if y >= CURRENT_YEAR - 10]
    else:
        included_years = data["completed_years"]

    # 2. Find the "Best" and "Worst" year based on final cumulative return
    best_year = None
    worst_year = None
    best_return = -float('inf')
    worst_return = float('inf')

    for yr in included_years:
        if yr in yearly_cum:
            final_val = yearly_cum[yr].iloc[-1]
            if final_val > best_return:
                best_return = final_val
                best_year = yr
            if final_val < worst_return:
                worst_return = final_val
                worst_year = yr

    # 3. Plot the Spaghetti Lines (Background Years)
    if show_spaghetti:
        for yr in included_years:
            if yr in yearly_cum and yr not in [best_year, worst_year]:
                fig.add_trace(go.Scatter(
                    x=yearly_cum[yr].index, 
                    y=yearly_cum[yr].values,
                    mode='lines', 
                    line=dict(color=COLOR_SPAGHETTI, width=1), 
                    opacity=0.3,  # <--- ADD OPACITY HERE
                    name=str(yr), 
                    showlegend=False, 
                    hoverinfo="skip"
                ))

    # 4. Plot the "Worst" Year (Lower Bound)
    if worst_year in yearly_cum:
        fig.add_trace(go.Scatter(
            x=yearly_cum[worst_year].index, 
            y=yearly_cum[worst_year].values,
            mode='lines', line=dict(color=COLOR_WORST, width=2, dash='dot'), 
            name=f"Worst Year ({worst_year})",
            hovertemplate=f"Worst ({worst_year}): %{{y:.2f}}%<extra></extra>"
        ))

    # 5. Plot the "Best" Year (Upper Bound)
    if best_year in yearly_cum:
        fig.add_trace(go.Scatter(
            x=yearly_cum[best_year].index, 
            y=yearly_cum[best_year].values,
            mode='lines', line=dict(color=COLOR_BEST, width=2, dash='dot'), 
            name=f"Best Year ({best_year})",
            hovertemplate=f"Best ({best_year}): %{{y:.2f}}%<extra></extra>"
        ))

    # 6. Plot the Historical Average Line
    avg_key = f"avg_{window}"
    if len(data[avg_key]) > 0:
        s = pd.Series(data[avg_key])
        comp = (1 + s / 100).cumprod() * 100 - 100
        fig.add_trace(go.Scatter(
            x=comp.index, y=comp.values, 
            mode='lines', line=dict(color=COLOR_AVG, width=3), 
            name=f"Historical Average",
            hovertemplate="Average: %{y:.2f}%<extra></extra>"
        ))

    # 7. Plot the Current Year (Front & Center)
    if len(data["cur_roc"]) > 0:
        s = pd.Series(data["cur_roc"])
        comp = (1 + s / 100).cumprod() * 100 - 100
        fig.add_trace(go.Scatter(
            x=comp.index, y=comp.values, 
            mode='lines+markers', line=dict(color=COLOR_CURRENT, width=4), 
            marker=dict(size=6), name=str(CURRENT_YEAR),
            hovertemplate=f"{CURRENT_YEAR}: %{{y:.2f}}%<extra></extra>"
        ))

    # 8. Apply Layout Formatting
    layout = _base_layout(title)
    layout["xaxis"].update(title="Period", dtick=4 if timeframe == "Weekly" else 1)
    layout["yaxis"]["ticksuffix"] = "%"
    layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    
    fig.update_layout(**layout)
    return fig
    
def make_presidential_cycle_chart(cycle_data: dict) -> go.Figure:
    avg_roc, cur_roc, start_yr = cycle_data["avg_roc"], cycle_data["cur_roc"], cycle_data["current_cycle_start"]
    periods, x_anchor = list(range(1, 49)), [0] + list(range(1, 49))
    
    def _cum(s):
        c, r = [0.0], 100.0
        for p in periods:
            v = s.get(p, np.nan)
            if pd.isna(v): c.append(c[-1])
            else: r *= (1 + v/100); c.append(r - 100.0)
        return c

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_anchor, y=_cum(avg_roc), mode="lines", line=dict(color=COLORS["avg_line"], width=3.5), name="Hist. Avg"))
    if [p for p in periods if p in cur_roc.index]:
        n = len([p for p in periods if p in cur_roc.index]) + 1
        fig.add_trace(go.Scatter(x=x_anchor[:n], y=_cum(pd.Series({p: cur_roc.get(p, np.nan) for p in periods}))[:n], mode="lines+markers", line=dict(color=COLORS["cur_year"], width=3.5), name=f"Current ({start_yr})"))

    for m, label in [(12, "Yr 1"), (24, "Yr 2"), (36, "Yr 3")]: fig.add_vline(x=m, line_dash="dot", line_color="#4a5568")

    layout = _base_layout("S&P 500: 48-Month Presidential Cycle (Since 1981)", height=550)
    
    # --- ADD THESE TWO LINES TO ADJUST SPACING ---
    layout["margin"]["t"] = 100    # Increases the top margin (pushes the chart down)
    layout["legend"]["y"] = 1.05   # Adjusts the vertical position of the legend
    # ---------------------------------------------
    
    layout["xaxis"].update(title="Months Since Cycle Start", dtick=4, range=[-0.5, 48.5])
    layout["yaxis"]["ticksuffix"] = "%"
    
    fig.update_layout(**layout)
    return fig

def make_rebased_macro_chart(data_dict: dict, events_list: list, zone_color: str, title: str) -> go.Figure:
    fig = go.Figure()
    df_combined = pd.DataFrame(data_dict).dropna()
    if df_combined.empty: return fig
    df_rebased = df_combined / df_combined.iloc[0] * 100
    
    for col in df_rebased.columns:
        fig.add_trace(go.Scatter(x=df_rebased.index, y=df_rebased[col], mode="lines", line=dict(color=COLORS.get(col.split(" ")[0].lower(), "#FFFFFF"), width=2), name=col))

    for ev in events_list:
        fig.add_vrect(x0=ev["start"], x1=ev["end"], fillcolor=zone_color, opacity=0.8, line_width=0, annotation_text=ev["name"], annotation_position="top left", annotation_textangle=-90)

    layout = _base_layout(title, height=450)
    layout["yaxis"].update(type="log", title="Index/Asset Value (Log)")
    fig.update_layout(**layout)
    return fig

def make_rrg_chart(rrg_data: dict) -> go.Figure:
    from config import SECTOR_COLORS
    fig = go.Figure()
    ratio, momentum = rrg_data["ratio"], rrg_data["momentum"]
    
    # Draw Quadrant Crosshairs at the 100/100 baseline
    fig.add_hline(y=100, line_dash="solid", line_color="#2a3045", line_width=2)
    fig.add_vline(x=100, line_dash="solid", line_color="#2a3045", line_width=2)
    
    # Calculate chart boundaries to keep the 100/100 crosshair perfectly centered
    max_dev = max(abs(ratio.min().min()-100), abs(ratio.max().max()-100), 
                  abs(momentum.min().min()-100), abs(momentum.max().max()-100)) * 1.15
    b_min, b_max = 100 - max_dev, 100 + max_dev

    # Background Labels
    lbl_font = dict(family="IBM Plex Mono", color="#3a4258", size=24)
    fig.add_annotation(x=b_max-0.5, y=b_max-0.5, text="LEADING", showarrow=False, font=lbl_font, xanchor="right", yanchor="top")
    fig.add_annotation(x=b_max-0.5, y=b_min+0.5, text="WEAKENING", showarrow=False, font=lbl_font, xanchor="right", yanchor="bottom")
    fig.add_annotation(x=b_min+0.5, y=b_min+0.5, text="LAGGING", showarrow=False, font=lbl_font, xanchor="left", yanchor="bottom")
    fig.add_annotation(x=b_min+0.5, y=b_max-0.5, text="IMPROVING", showarrow=False, font=lbl_font, xanchor="left", yanchor="top")

    for col in ratio.columns:
        color = SECTOR_COLORS.get(col, "#FFFFFF")
        # Plot the tail ending in a large dot for the current day
        fig.add_trace(go.Scatter(
            x=ratio[col], y=momentum[col], mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=[4]*(len(ratio)-1) + [14], color=color, line=dict(color="#000", width=1)),
            name=col, hovertemplate=f"<b>{col}</b><br>Strength (X): %{{x:.2f}}<br>Momentum (Y): %{{y:.2f}}<extra></extra>"
        ))

    layout = _base_layout(f"Sector Rotation Graph (vs SPY) • {rrg_data['current_date']}", height=700)
    # --- ADD THESE TWO LINES TO FIX THE SPACING ---
    layout["margin"]["t"] = 100    # Pushes the entire chart down to give the title room
    layout["legend"]["y"] = 1.05   # Nudges the horizontal legend safely below the title
    # ----------------------------------------------
    layout["xaxis"].update(title="Relative Strength (RS-Ratio) ➔", range=[b_min, b_max], zeroline=False)
    layout["yaxis"].update(title="Relative Momentum (RS-Momentum) ➔", range=[b_min, b_max], zeroline=False)
    fig.update_layout(**layout)
    return fig
# --- ADD THIS TO THE BOTTOM OF plot_engine.py ---


