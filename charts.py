# Plotly chart functions for the marketing dashboard.

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

# ── Design tokens ─────────────────────────────────────────────────────────────
C = {"Facebook": "#2563EB", "Google": "#16A34A", "TikTok": "#E11D48"}
BG      = "rgba(0,0,0,0)"
SURFACE = "#F8FAFC"
MUTED   = "#64748B"
TEXT    = "#0F172A"
GRID    = "#E2E8F0"
FONT    = "Calibri, 'Trebuchet MS', sans-serif"

TOOLTIP = dict(
    bgcolor="#1E293B", bordercolor="#CBD5E1", borderwidth=1,
    font=dict(color="#F8FAFC", family=FONT, size=12),
)

def _base(fig, height=None, **kw):
    layout = dict(
        paper_bgcolor=BG, plot_bgcolor=SURFACE,
        font=dict(family=FONT, color=TEXT, size=12),
        margin=dict(t=36, b=36, l=48, r=24),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT, size=11),
                    orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
    )
    if height:
        layout["height"] = height
    layout.update(kw)
    fig.update_layout(**layout)
    fig.update_xaxes(gridcolor=GRID, color=MUTED, showline=False, zeroline=False,
                     tickfont=dict(family=FONT))
    fig.update_yaxes(gridcolor=GRID, color=MUTED, showline=False, zeroline=False,
                     tickfont=dict(family=FONT))
    return fig


# ── 1. Daily spend + 7-day rolling avg ───────────────────────────────────────
def spend_trend(ts: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for p in ["Facebook", "Google", "TikTok"]:
        d = ts[ts["platform"] == p]
        fig.add_trace(go.Scatter(
            x=d["date"], y=d["spend"], name=p, mode="lines",
            line=dict(color=C[p], width=2.5),
            hovertemplate=f"<b>{p}</b>: $%{{y:,.0f}}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=d["date"], y=d["spend_7d_avg"],
            name=f"{p} 7d avg", mode="lines", showlegend=False,
            line=dict(color=C[p], width=1.2, dash="dot"), opacity=0.45,
            hovertemplate=f"<b>{p} 7d avg</b>: $%{{y:,.0f}}<extra></extra>",
        ))
    return _base(fig, height=300,
                 yaxis=dict(tickprefix="$", gridcolor=GRID, color=MUTED, zeroline=False))


# ── 2. Daily conversions stacked area ────────────────────────────────────────
def conversion_area(ts: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for p in ["Facebook", "Google", "TikTok"]:
        d = ts[ts["platform"] == p]
        fig.add_trace(go.Scatter(
            x=d["date"], y=d["conversions"], name=p,
            mode="lines", stackgroup="one",
            line=dict(color=C[p], width=0.5),
            fillcolor=C[p],
            hovertemplate=f"<b>{p}</b>: %{{y:,}}<extra></extra>",
        ))
    return _base(fig, height=260)


# ── 3. Platform KPI bars (CPA / CTR / CPC) ───────────────────────────────────
def platform_kpis(plat: pd.DataFrame) -> go.Figure:
    fig = make_subplots(rows=1, cols=3,
                        subplot_titles=["CPA — Cost per Acquisition",
                                        "CTR — Click-Through Rate",
                                        "CPC — Cost per Click"],
                        horizontal_spacing=0.10)
    colors = [C[p] for p in plat["platform"]]

    def bar(col, fmt, mult, row, ysfx=""):
        vals = plat[col] * mult
        fig.add_trace(go.Bar(
            x=plat["platform"], y=vals,
            marker_color=colors,
            marker_line=dict(color="rgba(0,0,0,0)", width=0),
            marker_pattern_shape="",
            opacity=0.88,
            text=[fmt % v for v in vals], textposition="outside",
            textfont=dict(color=TEXT, size=11, family=FONT), showlegend=False,
            hovertemplate="%{x}<br>"+col.upper()+": %{text}<extra></extra>",
        ), row=1, col=row)
        fig.update_yaxes(ticksuffix=ysfx, gridcolor=GRID, color=MUTED,
                         tickfont=dict(family=FONT), row=1, col=row)
        fig.update_xaxes(showgrid=False, tickfont=dict(family=FONT), row=1, col=row)

    bar("cpa", "$%.2f", 1,   1)
    bar("ctr", "%.2f%%", 100, 2, "%")
    bar("cpc", "$%.3f", 1,   3)

    fig.update_layout(
        height=280, paper_bgcolor=BG, plot_bgcolor=SURFACE,
        font=dict(family=FONT, color=TEXT, size=11),
        margin=dict(t=48, b=24, l=40, r=20),
    )
    fig.update_annotations(font=dict(family=FONT, color=MUTED, size=11))
    return fig


# ── 4. Bubble: spend vs conversions ──────────────────────────────────────────
def spend_vs_conv(camp: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        camp, x="spend", y="conversions",
        size="impressions", color="platform",
        color_discrete_map=C,
        hover_name="campaign_name",
        hover_data={"spend": ":$,.0f", "conversions": ":,",
                    "cpa": ":$.2f", "ctr": ":.2%",
                    "platform": False, "impressions": ":,.0f"},
        size_max=55,
    )
    fig.update_traces(marker=dict(opacity=0.82, line=dict(width=1.5, color="rgba(255,255,255,0.6)")))
    return _base(fig, height=320,
                 xaxis=dict(tickprefix="$", gridcolor=GRID, color=MUTED, zeroline=False),
                 yaxis=dict(gridcolor=GRID, color=MUTED, zeroline=False),
                 hovermode="closest")


# ── 5. Campaign CPA horizontal bar ───────────────────────────────────────────
def campaign_cpa(camp: pd.DataFrame) -> go.Figure:
    d = camp.sort_values("cpa")
    fig = go.Figure(go.Bar(
        y=d["campaign_name"].str.replace("_", " "),
        x=d["cpa"], orientation="h",
        marker_color=[C[p] for p in d["platform"]],
        marker_line=dict(color="rgba(0,0,0,0)", width=0),
        opacity=0.88,
        text=[f"${v:.2f}" for v in d["cpa"]],
        textposition="outside", textfont=dict(color=TEXT, size=11, family=FONT),
        hovertemplate="<b>%{y}</b><br>CPA: $%{x:.2f}<extra></extra>",
    ))
    return _base(fig, height=380,
                 xaxis=dict(tickprefix="$", gridcolor=GRID, color=MUTED, zeroline=False),
                 yaxis=dict(gridcolor=GRID, color=MUTED),
                 hovermode="closest")


# ── 6. Google ROAS bar ────────────────────────────────────────────────────────
def google_roas(google_roas_df: pd.DataFrame) -> go.Figure:
    d = google_roas_df.sort_values("roas", ascending=False)
    bar_colors = ["#16A34A" if v >= 4 else "#E11D48" for v in d["roas"]]
    fig = go.Figure(go.Bar(
        x=d["campaign_name"].str.replace("_", " "),
        y=d["roas"],
        marker_color=bar_colors,
        marker_line=dict(color="rgba(0,0,0,0)", width=0),
        opacity=0.88,
        text=[f"{v:.2f}×" for v in d["roas"]],
        textposition="outside", textfont=dict(color=TEXT, size=12, family=FONT),
        hovertemplate="<b>%{x}</b><br>ROAS: %{y:.2f}×<extra></extra>",
    ))
    fig.add_hline(y=4, line_dash="dot", line_color="#94A3B8",
                  annotation_text="4× target", annotation_font_color=MUTED,
                  annotation_font_family=FONT,
                  annotation_position="top right")
    return _base(fig, height=280,
                 yaxis=dict(ticksuffix="×", gridcolor=GRID, color=MUTED, zeroline=False),
                 hovermode="closest")


# ── 7. TikTok funnel ──────────────────────────────────────────────────────────
def tiktok_funnel(tt_funnel: pd.DataFrame) -> go.Figure:
    row = tt_funnel.iloc[0]
    stages = ["25% view", "50% view", "75% view", "100% complete"]
    vals   = [int(row["w25"]), int(row["w50"]), int(row["w75"]), int(row["w100"])]
    fig = go.Figure(go.Funnel(
        y=stages, x=vals,
        texttemplate="%{label}<br><b>%{value:,.0f}</b> (%{percentInitial:.0%})",
        textfont=dict(color=TEXT, size=12, family=FONT),
        marker=dict(
            color=["#E11D48", "#F43F5E", "#FB7185", "#FECDD3"],
            line=dict(width=1.5, color="#FFFFFF"),
        ),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} views<br>%{percentInitial:.1%} retention<extra></extra>",
    ))
    fig.update_layout(
        height=280, paper_bgcolor=BG,
        font=dict(family=FONT, color=TEXT, size=11),
        margin=dict(t=20, b=20, l=100, r=20),
    )
    return fig


# ── 8. CTR over time ──────────────────────────────────────────────────────────
def ctr_trend(ts: pd.DataFrame) -> go.Figure:
    ts = ts.copy()
    ts["ctr_pct"] = ts["clicks"] / ts["impressions"] * 100
    fig = go.Figure()
    for p in ["Facebook", "Google", "TikTok"]:
        d = ts[ts["platform"] == p]
        fig.add_trace(go.Scatter(
            x=d["date"], y=d["ctr_pct"], name=p, mode="lines+markers",
            line=dict(color=C[p], width=2),
            marker=dict(size=4, color=C[p]),
            hovertemplate=f"<b>{p}</b>: %{{y:.2f}}%<extra></extra>",
        ))
    return _base(fig, height=260,
                 yaxis=dict(ticksuffix="%", gridcolor=GRID, color=MUTED, zeroline=False))


# ── 9. Spend share donut ──────────────────────────────────────────────────────
def spend_donut(plat: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=plat["platform"], values=plat["spend"],
        hole=0.68,
        marker=dict(colors=[C[p] for p in plat["platform"]],
                    line=dict(color="#FFFFFF", width=3)),
        textfont=dict(color=TEXT, size=12, family=FONT),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    total = plat["spend"].sum()
    fig.add_annotation(
        text=f"<b>${total/1000:.1f}K</b><br><span style='font-size:11px'>Total spend</span>",
        showarrow=False, font=dict(color=TEXT, size=14, family=FONT),
    )
    fig.update_layout(
        height=260, paper_bgcolor=BG,
        font=dict(family=FONT, color=TEXT, size=11),
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT, size=11, family=FONT),
                    orientation="v", x=0.85, y=0.5),
        showlegend=True,
    )
    return fig


# ── 10. Impressions share donut ───────────────────────────────────────────────
def impressions_donut(plat: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=plat["platform"], values=plat["impressions"],
        hole=0.68,
        marker=dict(colors=[C[p] for p in plat["platform"]],
                    line=dict(color="#FFFFFF", width=3)),
        textfont=dict(color=TEXT, size=12, family=FONT),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    total = plat["impressions"].sum()
    fig.add_annotation(
        text=f"<b>{total/1e6:.1f}M</b><br><span style='font-size:11px'>Impressions</span>",
        showarrow=False, font=dict(color=TEXT, size=14, family=FONT),
    )
    fig.update_layout(
        height=260, paper_bgcolor=BG,
        font=dict(family=FONT, color=TEXT, size=11),
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT, size=11, family=FONT),
                    orientation="v", x=0.85, y=0.5),
        showlegend=True,
    )
    return fig
