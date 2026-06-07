# Multi-Channel Marketing Analytics Dashboard

An interactive analytics dashboard built with PySpark, Pandas, Plotly, and Streamlit.
Covers Facebook Ads, Google Ads, and TikTok Ads data for January 2024.

---

## Project structure

```
marketing-analysis/
├── app.py                  ← Streamlit app (main entry point)
├── pipeline.py             ← Data loading and transformation
├── charts.py               ← Plotly chart functions
├── requirements.txt        ← Python dependencies
├── config.toml             ← Streamlit theme and server config
├── 01_facebook_ads.csv
├── 02_google_ads.csv
└── 03_tiktok_ads.csv
```

---

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at http://localhost:8501

> PySpark requires Java 11+. Without it the app falls back to Pandas automatically — results are identical.

---

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in
3. Click **New app** → select repo → set main file to `app.py` → Deploy

---

## Dashboard sections

- **KPI summary** — Total spend, conversions, impressions, CPA, CTR, ROAS
- **Spend & Reach** — Daily spend trends with 7-day rolling average, budget and impression share
- **Platform Efficiency** — CPA, CTR, CPC comparison across platforms
- **Conversions & Engagement** — Stacked conversion area, CTR over time
- **Campaign Performance** — CPA ranking, spend vs conversions bubble chart
- **Google Ads deep dive** — ROAS by campaign with 4× target benchmark
- **TikTok Analytics** — Video completion funnel, social engagement metrics
- **Analyst Insights** — Best and worst performing campaigns with recommendations

## Sidebar filters

- Platform (Facebook / Google / TikTok)
- Date range
- Campaign selector
