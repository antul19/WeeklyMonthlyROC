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

def make_cumulative_chart(data: dict, window_key: str, show_spaghetti: bool, timeframe: str, title: str) -> go.Figure:
    avg, cur, pivot, periods, cur_p = data[f"avg_{window_key}"], data["cur_roc"], data["pivot"], data["periods"], data["current_period"]
    
    def _cum(s):
        c, r = [0.0], 100.0
        for p in periods:
            v = s.get(p, np.nan)
            if pd.isna(v): c.append(c[-1])
            else: r *= (1 + v/100); c.append(r - 100.0)
        return c
        
    fig, x_anchor = go.Figure(), [0] + periods
    if show_spaghetti:
        yrs = sorted(pivot.index.tolist())[-5:] if window_key == "5" else (sorted(pivot.index.tolist())[-10:] if window_key == "10" else sorted(pivot.index.tolist()))
        for i, yr in enumerate(yrs):
            fig.add_trace(go.Scatter(x=x_anchor, y=_cum(pivot.loc[yr] if yr in pivot.index else pd.Series(dtype=float)), mode="lines", line=dict(color=COLORS["spaghetti"]), showlegend=(i==0), name="Past Years" if i==0 else None))
            
    fig.add_trace(go.Scatter(x=x_anchor, y=_cum(avg), mode="lines", line=dict(color=COLORS["avg_line"], width=3.5), name="Hist. Avg"))
    cur_x = [p for p in periods if p in cur.index]
    if cur_x:
        fig.add_trace(go.Scatter(x=x_anchor[:len(cur_x)+1], y=_cum(pd.Series({p: cur.get(p, np.nan) for p in periods}))[:len(cur_x)+1], mode="lines+markers", line=dict(color=COLORS["cur_year"], width=3), name=f"{CURRENT_YEAR} Actual"))

    if cur_p in x_anchor: fig.add_vline(x=cur_p, line_dash="dash", line_color=COLORS["vline"])
    
    layout = _base_layout(title)
    layout["xaxis"].update(title="Week" if timeframe == "Weekly" else "Month", dtick=1, range=[-0.5, (52 if timeframe=="Weekly" else 12) + 0.5])
    layout["yaxis"]["ticksuffix"] = "%"
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
