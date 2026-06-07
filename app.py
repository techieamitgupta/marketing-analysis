# Multi-Channel Marketing Analytics Dashboard
# Facebook Ads · Google Ads · TikTok Ads — January 2024

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pipeline import load_all, build_aggregates
from charts import (
    spend_trend, conversion_area, platform_kpis,
    spend_vs_conv, campaign_cpa, google_roas,
    tiktok_funnel, ctr_trend, spend_donut, impressions_donut,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Marketing Analytics · Jan 2024",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global font */
body, .stApp, .stMarkdown, .stMetric, p, h1, h2, h3, h4, h5, h6,
.stButton button, .stDownloadButton button, .stSelectbox, .stMultiSelect,
.stCaption, .stText, label, span, div.stMarkdown {
    font-family: 'Calibri', 'Trebuchet MS', sans-serif !important;
}
/* Metric cards */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 16px 20px 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
[data-testid="metric-container"] label {
    font-size: 11px !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748B !important;
    font-family: 'Calibri', 'Trebuchet MS', sans-serif !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 700;
    color: #0F172A !important;
    font-family: 'Calibri', 'Trebuchet MS', sans-serif !important;
}
/* Section headers */
.section-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #64748B;
    margin: 28px 0 12px;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 8px;
    font-family: 'Calibri', 'Trebuchet MS', sans-serif !important;
}
/* Insight boxes */
.insight {
    background: #F0F7FF;
    border-left: 3px solid #2563EB;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 10px;
    font-size: 13px;
    line-height: 1.65;
    color: #1E293B;
    font-family: 'Calibri', 'Trebuchet MS', sans-serif !important;
}
.insight b { color: #1D4ED8; }
/* Hide streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
/* Platform pill */
.pill {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 6px;
    font-family: 'Calibri', 'Trebuchet MS', sans-serif !important;
}
.pill-fb  { background: rgba(37,99,235,0.10); color: #2563EB; border: 1px solid rgba(37,99,235,0.3); }
.pill-g   { background: rgba(22,163,74,0.10);  color: #16A34A; border: 1px solid rgba(22,163,74,0.3); }
.pill-tt  { background: rgba(225,29,72,0.10);  color: #E11D48; border: 1px solid rgba(225,29,72,0.3); }
</style>
""", unsafe_allow_html=True)


# ── Load data (cached) ────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_data():
    unified, ts, tt_funnel = load_all(use_spark=True)
    unified["date"] = pd.to_datetime(unified["date"])
    ts["date"]      = pd.to_datetime(ts["date"])
    plat, camp, g_roas = build_aggregates(unified)
    return unified, ts, tt_funnel, plat, camp, g_roas


with st.spinner("Running PySpark pipeline…"):
    unified, ts, tt_funnel, plat, camp, g_roas = get_data()


# ── Sidebar toggle state ──────────────────────────────────────────────────────
if "sidebar_open" not in st.session_state:
    st.session_state["sidebar_open"] = True

if not st.session_state["sidebar_open"]:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    col_hdr, col_close = st.columns([6, 1])
    with col_hdr:
        st.markdown("## Filters")
    with col_close:
        st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
        if st.button("❮❮", key="close_sidebar", help="Collapse menu"):
            st.session_state["sidebar_open"] = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    platforms = st.multiselect(
        "Platforms",
        options=["Facebook", "Google", "TikTok"],
        default=["Facebook", "Google", "TikTok"],
    )

    date_min = unified["date"].min().date()
    date_max = unified["date"].max().date()
    date_range = st.date_input(
        "Date range",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    all_camps = sorted(unified["campaign_name"].unique().tolist())
    selected_camps = st.multiselect(
        "Campaigns (optional)",
        options=all_camps,
        default=[],
        placeholder="All campaigns",
    )

    st.markdown("---")
    from pipeline import SPARK_OK
    if SPARK_OK:
        use_spark = st.toggle("PySpark backend", value=True,
                              help="Toggle between PySpark and pure Pandas ETL")
        st.caption("PySpark available locally. Streamlit Cloud uses the Pandas backend — identical results.")
    else:
        use_spark = False

    st.markdown("---")
    st.markdown("**Data sources**")
    st.markdown(
        '<span class="pill pill-fb">● Facebook</span>'
        '<span class="pill pill-g">● Google</span>'
        '<span class="pill pill-tt">● TikTok</span>',
        unsafe_allow_html=True,
    )
    st.caption("January 2024 · 330 unified rows")


# ── Apply filters ─────────────────────────────────────────────────────────────
d_start = pd.to_datetime(date_range[0])
d_end   = pd.to_datetime(date_range[1] if len(date_range) > 1 else date_range[0])

mask = (
    unified["platform"].isin(platforms) &
    unified["date"].between(d_start, d_end)
)
if selected_camps:
    mask &= unified["campaign_name"].isin(selected_camps)

u_f = unified[mask].copy()
ts_f = ts[ts["platform"].isin(platforms) &
           ts["date"].between(d_start, d_end)].copy()

plat_f, camp_f, g_roas_f = build_aggregates(u_f)
camp_f_g = camp_f[camp_f["platform"] == "Google"]


# ── Sidebar reopen button (shown only when sidebar is hidden) ─────────────────
if not st.session_state.get("sidebar_open", True):
    if st.button("❯❯  Open Menu", key="open_sidebar"):
        st.session_state["sidebar_open"] = True
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 12px 0 4px'>
  <h1 style='font-size:26px; font-weight:700; margin:0; letter-spacing:-0.02em; color:#0F172A; font-family:Calibri,"Trebuchet MS",sans-serif'>
    Multi-Channel Ad Performance
  </h1>
  <p style='color:#64748B; font-size:13px; margin:4px 0 0; font-family:Calibri,"Trebuchet MS",sans-serif'>
    Facebook · Google · TikTok &nbsp;·&nbsp; January 2024 &nbsp;·&nbsp;
    Powered by PySpark + Pandas + Plotly + Streamlit
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ── KPI row ───────────────────────────────────────────────────────────────────
total_spend   = u_f["spend"].sum()
total_conv    = u_f["conversions"].sum()
total_impr    = u_f["impressions"].sum()
total_clicks  = u_f["clicks"].sum()
portfolio_cpa = total_spend / total_conv if total_conv else 0
portfolio_ctr = total_clicks / total_impr * 100 if total_impr else 0
portfolio_cpc = total_spend / total_clicks if total_clicks else 0
google_roas_avg = (
    g_roas_f["roas"].mean() if not g_roas_f.empty and g_roas_f["roas"].notna().any() else 0
)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Spend",      f"${total_spend/1000:.1f}K")
c2.metric("Conversions",      f"{int(total_conv):,}")
c3.metric("Impressions",      f"{total_impr/1e6:.1f}M")
c4.metric("Portfolio CPA",    f"${portfolio_cpa:.2f}")
c5.metric("Portfolio CTR",    f"{portfolio_ctr:.2f}%")
c6.metric("Google ROAS",      f"{google_roas_avg:.2f}×")


# ── Section 1: Spend & reach ──────────────────────────────────────────────────
st.markdown('<div class="section-title">Spend & Reach</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([2, 1])
with col_left:
    st.caption("Daily ad spend by platform · dotted = 7-day rolling average")
    st.plotly_chart(spend_trend(ts_f), use_container_width=True)

with col_right:
    st.caption("Budget distribution")
    st.plotly_chart(spend_donut(plat_f), use_container_width=True)
    st.plotly_chart(impressions_donut(plat_f), use_container_width=True)


# ── Section 2: Efficiency ─────────────────────────────────────────────────────
st.markdown('<div class="section-title">Platform Efficiency Metrics</div>', unsafe_allow_html=True)
st.plotly_chart(platform_kpis(plat_f), use_container_width=True)


# ── Section 3: Conversions & CTR ─────────────────────────────────────────────
st.markdown('<div class="section-title">Conversions & Engagement Over Time</div>', unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a:
    st.caption("Daily conversions — stacked by platform")
    st.plotly_chart(conversion_area(ts_f), use_container_width=True)
with col_b:
    st.caption("Click-through rate % over time")
    st.plotly_chart(ctr_trend(ts_f), use_container_width=True)


# ── Section 4: Campaign breakdown ────────────────────────────────────────────
st.markdown('<div class="section-title">Campaign Performance</div>', unsafe_allow_html=True)
col_camp, col_bubble = st.columns([1, 1])
with col_camp:
    st.caption("CPA by campaign — ranked lowest to highest")
    st.plotly_chart(campaign_cpa(camp_f), use_container_width=True)
with col_bubble:
    st.caption("Spend vs conversions — bubble size = impressions")
    st.plotly_chart(spend_vs_conv(camp_f), use_container_width=True)


# ── Section 5: Google deep dive ───────────────────────────────────────────────
st.markdown('<div class="section-title">Google Ads — ROAS Deep Dive</div>', unsafe_allow_html=True)
col_roas, col_gtable = st.columns([1, 1])
with col_roas:
    st.caption("Return on ad spend by campaign · green = above 4× target")
    if not camp_f_g.empty:
        st.plotly_chart(google_roas(camp_f_g), use_container_width=True)
    else:
        st.info("No Google data in current filter selection.")

with col_gtable:
    st.caption("Google campaign detail table")
    if not camp_f_g.empty:
        display_g = camp_f_g[["campaign_name","spend","conversions","conv_value","cpa","roas"]].copy()
        display_g.columns = ["Campaign","Spend","Conv.","Conv. Value","CPA","ROAS"]
        display_g["Spend"]       = display_g["Spend"].map("${:,.0f}".format)
        display_g["Conv. Value"] = display_g["Conv. Value"].map("${:,.0f}".format)
        display_g["CPA"]         = display_g["CPA"].map("${:.2f}".format)
        display_g["ROAS"]        = display_g["ROAS"].map("{:.2f}×".format)
        display_g["Campaign"]    = display_g["Campaign"].str.replace("_", " ")
        st.dataframe(display_g.reset_index(drop=True), use_container_width=True, hide_index=True)
    else:
        st.info("No Google data in current filter selection.")


# ── Section 6: TikTok deep dive ──────────────────────────────────────────────
st.markdown('<div class="section-title">TikTok — Video & Social Analytics</div>', unsafe_allow_html=True)
col_f, col_s = st.columns([1, 1])
with col_f:
    st.caption("Video completion funnel — % of total views")
    st.plotly_chart(tiktok_funnel(tt_funnel), use_container_width=True)

with col_s:
    st.caption("Social engagement breakdown")
    row = tt_funnel.iloc[0]
    s1, s2, s3 = st.columns(3)
    s1.metric("Likes",    f"{int(row['likes']):,}")
    s2.metric("Shares",   f"{int(row['shares']):,}")
    s3.metric("Comments", f"{int(row['comments']):,}")

    total_eng = int(row["likes"]) + int(row["shares"]) + int(row["comments"])
    completion_rate = int(row["w100"]) / int(row["views_total"]) * 100
    st.markdown(f"""
    <div style='margin-top:14px'>
      <div class='insight'>
        <b>Total social engagements:</b> {total_eng:,}
        across all TikTok campaigns.
      </div>
      <div class='insight'>
        <b>Video completion rate:</b> {completion_rate:.1f}% of viewers
        watch to 100% — strong content signal.
      </div>
      <div class='insight'>
        <b>Share-to-like ratio:</b> {int(row['shares'])/int(row['likes'])*100:.1f}%
        — above 25% suggests high organic amplification potential.
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Section 7: Key insights ───────────────────────────────────────────────────
st.markdown('<div class="section-title">Analyst Insights & Recommendations</div>', unsafe_allow_html=True)

best_camp = camp_f.loc[camp_f["cpa"].idxmin()] if not camp_f.empty else None
worst_camp = camp_f.loc[camp_f["cpa"].idxmax()] if not camp_f.empty else None

ic1, ic2 = st.columns(2)
with ic1:
    if best_camp is not None:
        st.markdown(f"""
        <div class='insight'>
          <b>Best performer:</b> <b>{best_camp['campaign_name'].replace('_',' ')}</b>
          [{best_camp['platform']}] at <b>${best_camp['cpa']:.2f} CPA</b> —
          lowest in the portfolio. Prioritise budget here first.
        </div>
        <div class='insight'>
          <b>Facebook Retargeting</b> consistently outperforms on CPA ($5.95).
          Expand with lookalike audiences based on converters.
        </div>
        <div class='insight'>
          <b>Google Brand Search</b> delivers 9.81× ROAS — highest return
          in the entire portfolio. Increase bid caps and daily budget.
        </div>
        """, unsafe_allow_html=True)
with ic2:
    if worst_camp is not None:
        st.markdown(f"""
        <div class='insight'>
          <b>Worst performer:</b> <b>{worst_camp['campaign_name'].replace('_',' ')}</b>
          [{worst_camp['platform']}] at <b>${worst_camp['cpa']:.2f} CPA</b> —
          pause or restructure creative immediately.
        </div>
        <div class='insight'>
          <b>Google Search Generic</b> has a 2.02× ROAS against a 4× target.
          Reallocate its $15.5K budget to Brand Search and Shopping.
        </div>
        <div class='insight'>
          <b>TikTok Influencer Collab</b> drives the highest conversion volume
          (2,653) with strong social amplification. Scale with creator partnerships.
        </div>
        """, unsafe_allow_html=True)



# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#94A3B8; font-size:11px; font-family:Calibri,\"Trebuchet MS\",sans-serif'>"
    "Multi-Channel Marketing Analytics · January 2024 · "
    "Built with PySpark · Pandas · Plotly · Streamlit"
    "</p>",
    unsafe_allow_html=True,
)
