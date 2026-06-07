# Multi-Channel Marketing Analytics Dashboard

**Stack**: PySpark (ETL) → Pandas (modeling) → Plotly (charts) → Streamlit (UI)  
**Data**: Facebook Ads · Google Ads · TikTok Ads · January 2024  
**Live URL**: Deploy in 5 minutes on Streamlit Community Cloud (free)

---

## Project structure

```
marketing_app/
├── app.py              ← Streamlit UI (main entry point)
├── pipeline.py         ← PySpark ETL + Pandas data modeling
├── charts.py           ← All Plotly chart functions
├── requirements.txt    ← Python dependencies
├── .streamlit/
│   └── config.toml     ← Theme + server settings
└── data/
    ├── 01_facebook_ads.csv
    ├── 02_google_ads.csv
    └── 03_tiktok_ads.csv
```

---

## Run locally

```bash
# 1. Install dependencies (Python 3.9+, Java 11+ required for PySpark)
pip install -r requirements.txt

# 2. Run
streamlit run app.py
```

App opens at http://localhost:8501

---

## Deploy to Streamlit Community Cloud (free, live URL)

### Step 1 — Push to GitHub
```bash
# Create a new repo on github.com, then:
git init
git add .
git commit -m "Initial commit: marketing analytics dashboard"
git remote add origin https://github.com/YOUR_USERNAME/marketing-analytics.git
git push -u origin main
```

### Step 2 — Connect to Streamlit Cloud
1. Go to **https://share.streamlit.io** and sign in with GitHub
2. Click **"New app"**
3. Select your repository → branch: `main` → main file: `app.py`
4. Click **"Deploy"**

Your live URL will be:  
`https://YOUR_USERNAME-marketing-analytics-app-XXXX.streamlit.app`

### Step 3 — Share
Copy the URL and share — no login required for viewers.

---

## Dashboard features

| Section | Charts | Metrics |
|---|---|---|
| Portfolio KPIs | — | Spend, Conversions, Impressions, CPA, CTR, ROAS |
| Spend & Reach | Daily spend + 7d rolling avg, Donut charts | Budget share, Impression share |
| Efficiency | CPA / CTR / CPC grouped bars | Platform comparison |
| Conversions | Stacked area, CTR trend | Daily volume |
| Campaign Analysis | CPA ranked bars, Spend vs Conv bubble | Cross-campaign comparison |
| Google Deep Dive | ROAS bars + data table | Per-campaign ROAS |
| TikTok Analytics | Video funnel, Social metrics | Completion rate, Engagement |
| Insights | Auto-generated recommendations | Best/worst campaign flagged |
| Unified table | Filterable full dataset | Download as CSV |

### Sidebar filters
- Platform selector (Facebook / Google / TikTok)
- Date range picker
- Campaign selector
- PySpark vs Pandas toggle

---

## Data model (unified schema)

| Column | Type | Description |
|---|---|---|
| date | date | Ad date |
| platform | string | Facebook / Google / TikTok |
| campaign_id | string | Platform campaign ID |
| campaign_name | string | Campaign name |
| impressions | int | Total impressions |
| clicks | int | Total clicks |
| spend | float | Total spend ($) |
| conversions | int | Total conversions |
| video_views | float | Video views (0 for Google) |
| ctr | float | Click-through rate |
| cpc | float | Cost per click |
| cpa | float | Cost per acquisition |
| roas | float | Return on ad spend (Google only) |
| social_eng | float | Likes + shares + comments (TikTok only) |
| vid_compl_rate | float | % watched to 100% (TikTok only) |
| conv_value | float | Conversion value in $ (Google only) |

---

## Key findings (January 2024)

- **Best CPA**: Google Search Brand Terms at $5.10
- **Worst CPA**: Google Search Generic at $24.80 — reallocate budget
- **Best ROAS**: Google Search Brand at 9.81× (target: 4×)
- **Most conversions**: TikTok with 6,750 total
- **Most efficient CPM**: TikTok at $2.59 per 1,000 impressions
- **TikTok completion rate**: 26% watch to 100% — strong content signal
- **Portfolio CPA**: $9.75 blended across all platforms
