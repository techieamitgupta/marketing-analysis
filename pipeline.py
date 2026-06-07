# Data pipeline — loads and transforms the three ad platform CSVs.
# Runs on PySpark locally; falls back to Pandas on Streamlit Cloud.

import os
import warnings
import pandas as pd
import numpy as np
from pathlib import Path

warnings.filterwarnings("ignore")

_HERE    = Path(__file__).resolve().parent
DATA_DIR = _HERE


try:
    os.environ.setdefault("PYSPARK_PYTHON",        "python3")
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", "python3")
    from pyspark.sql import SparkSession, functions as F
    from pyspark.sql.types import DoubleType
    from pyspark.sql.window import Window
    SPARK_OK = True
except (ImportError, Exception):
    SPARK_OK = False


def _get_spark():
    return (
        SparkSession.builder
        .appName("MarketingDashboard")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.driver.memory", "1g")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


# ── PySpark path ──────────────────────────────────────────────────────────────
def _spark_pipeline():
    spark = _get_spark()
    spark.sparkContext.setLogLevel("ERROR")

    fb_raw = spark.read.csv(str(DATA_DIR / "01_facebook_ads.csv"), header=True, inferSchema=True)
    g_raw  = spark.read.csv(str(DATA_DIR / "02_google_ads.csv"),   header=True, inferSchema=True)
    tt_raw = spark.read.csv(str(DATA_DIR / "03_tiktok_ads.csv"),   header=True, inferSchema=True)

    # ── Facebook ──
    fb = (
        fb_raw
        .withColumn("platform",       F.lit("Facebook"))
        .withColumn("spend",          F.col("spend").cast(DoubleType()))
        .withColumn("video_views",    F.col("video_views").cast(DoubleType()))
        .withColumn("ctr",            (F.col("clicks") / F.col("impressions")).cast(DoubleType()))
        .withColumn("cpc",            (F.col("spend")  / F.col("clicks")).cast(DoubleType()))
        .withColumn("cpa",            (F.col("spend")  / F.col("conversions")).cast(DoubleType()))
        .withColumn("roas",           F.lit(None).cast(DoubleType()))
        .withColumn("social_eng",     F.lit(0).cast(DoubleType()))
        .withColumn("vid_compl_rate", F.lit(None).cast(DoubleType()))
        .withColumn("conv_value",     F.lit(None).cast(DoubleType()))
        .select("date","campaign_id","campaign_name","platform",
                "impressions","clicks","spend","conversions",
                "video_views","ctr","cpc","cpa","roas",
                "social_eng","vid_compl_rate","conv_value")
    )

    # ── Google ──
    g = (
        g_raw
        .withColumn("platform",       F.lit("Google"))
        .withColumnRenamed("cost",    "spend")
        .withColumn("spend",          F.col("spend").cast(DoubleType()))
        .withColumn("video_views",    F.lit(0).cast(DoubleType()))
        .withColumn("cpc",            F.col("avg_cpc").cast(DoubleType()))
        .withColumn("cpa",            (F.col("spend") / F.col("conversions")).cast(DoubleType()))
        .withColumn("roas",           (F.col("conversion_value") / F.col("spend")).cast(DoubleType()))
        .withColumn("social_eng",     F.lit(0).cast(DoubleType()))
        .withColumn("vid_compl_rate", F.lit(None).cast(DoubleType()))
        .withColumn("conv_value",     F.col("conversion_value").cast(DoubleType()))
        .select("date","campaign_id","campaign_name","platform",
                "impressions","clicks","spend","conversions",
                "video_views","ctr","cpc","cpa","roas",
                "social_eng","vid_compl_rate","conv_value")
    )

    # ── TikTok ──
    tt = (
        tt_raw
        .withColumn("platform",       F.lit("TikTok"))
        .withColumnRenamed("cost",    "spend")
        .withColumn("spend",          F.col("spend").cast(DoubleType()))
        .withColumn("video_views",    F.col("video_views").cast(DoubleType()))
        .withColumn("ctr",            (F.col("clicks") / F.col("impressions")).cast(DoubleType()))
        .withColumn("cpc",            (F.col("spend")  / F.col("clicks")).cast(DoubleType()))
        .withColumn("cpa",            (F.col("spend")  / F.col("conversions")).cast(DoubleType()))
        .withColumn("roas",           F.lit(None).cast(DoubleType()))
        .withColumn("social_eng",     (F.col("likes") + F.col("shares") + F.col("comments")).cast(DoubleType()))
        .withColumn("vid_compl_rate", (F.col("video_watch_100") / F.col("video_views")).cast(DoubleType()))
        .withColumn("conv_value",     F.lit(None).cast(DoubleType()))
        .select("date","campaign_id","campaign_name","platform",
                "impressions","clicks","spend","conversions",
                "video_views","ctr","cpc","cpa","roas",
                "social_eng","vid_compl_rate","conv_value")
    )

    unified = fb.unionByName(g).unionByName(tt)
    unified = unified.withColumn("date", F.to_date("date", "yyyy-MM-dd"))

    # 7-day rolling spend per platform (Spark Window function)
    w = Window.partitionBy("platform").orderBy("date").rowsBetween(-6, 0)
    ts = (
        unified
        .groupBy("date", "platform")
        .agg(
            F.sum("spend").alias("spend"),
            F.sum("conversions").alias("conversions"),
            F.sum("impressions").alias("impressions"),
            F.sum("clicks").alias("clicks"),
        )
        .withColumn("spend_7d_avg", F.avg("spend").over(w))
        .orderBy("date", "platform")
    )

    # TikTok video funnel
    tt_funnel = tt_raw.agg(
        F.sum("video_views").alias("views_total"),
        F.sum("video_watch_25").alias("w25"),
        F.sum("video_watch_50").alias("w50"),
        F.sum("video_watch_75").alias("w75"),
        F.sum("video_watch_100").alias("w100"),
        F.sum("likes").alias("likes"),
        F.sum("shares").alias("shares"),
        F.sum("comments").alias("comments"),
    )

    pdf_unified   = unified.toPandas()
    pdf_ts        = ts.toPandas()
    pdf_tt_funnel = tt_funnel.toPandas()
    spark.stop()
    return pdf_unified, pdf_ts, pdf_tt_funnel


# ── Pure Pandas fallback (used on Streamlit Cloud) ────────────────────────────
def _pandas_pipeline():
    fb = pd.read_csv(DATA_DIR / "01_facebook_ads.csv", parse_dates=["date"])
    g  = pd.read_csv(DATA_DIR / "02_google_ads.csv",   parse_dates=["date"])
    tt = pd.read_csv(DATA_DIR / "03_tiktok_ads.csv",   parse_dates=["date"])

    fb = fb.assign(
        platform="Facebook",
        video_views=fb["video_views"].astype(float),
        ctr=fb["clicks"] / fb["impressions"],
        cpc=fb["spend"]  / fb["clicks"],
        cpa=fb["spend"]  / fb["conversions"],
        roas=np.nan, social_eng=0.0, vid_compl_rate=np.nan, conv_value=np.nan,
    )

    g = g.assign(
        platform="Google",
        spend=g["cost"].astype(float),
        video_views=0.0,
        ctr=g["ctr"],
        cpc=g["avg_cpc"],
        cpa=g["cost"]  / g["conversions"],
        roas=g["conversion_value"] / g["cost"],
        social_eng=0.0, vid_compl_rate=np.nan,
        conv_value=g["conversion_value"],
    )

    tt = tt.assign(
        platform="TikTok",
        spend=tt["cost"].astype(float),
        video_views=tt["video_views"].astype(float),
        ctr=tt["clicks"] / tt["impressions"],
        cpc=tt["cost"]   / tt["clicks"],
        cpa=tt["cost"]   / tt["conversions"],
        roas=np.nan,
        social_eng=tt["likes"] + tt["shares"] + tt["comments"],
        vid_compl_rate=tt["video_watch_100"] / tt["video_views"],
        conv_value=np.nan,
    )

    cols = [
        "date","campaign_id","campaign_name","platform",
        "impressions","clicks","spend","conversions",
        "video_views","ctr","cpc","cpa","roas","social_eng","vid_compl_rate","conv_value",
    ]
    unified = pd.concat([fb[cols], g[cols], tt[cols]], ignore_index=True)

    # 7-day rolling avg per platform (Pandas equivalent of Spark Window)
    ts = (
        unified
        .groupby(["date", "platform"])
        .agg(spend=("spend","sum"), conversions=("conversions","sum"),
             impressions=("impressions","sum"), clicks=("clicks","sum"))
        .reset_index()
        .sort_values(["date", "platform"])
    )
    ts["spend_7d_avg"] = (
        ts.groupby("platform")["spend"]
        .transform(lambda x: x.rolling(7, min_periods=1).mean())
    )

    # TikTok funnel from raw
    tt_raw = pd.read_csv(DATA_DIR / "03_tiktok_ads.csv")
    funnel_row = {
        "views_total": int(tt_raw["video_views"].sum()),
        "w25":  int(tt_raw["video_watch_25"].sum()),
        "w50":  int(tt_raw["video_watch_50"].sum()),
        "w75":  int(tt_raw["video_watch_75"].sum()),
        "w100": int(tt_raw["video_watch_100"].sum()),
        "likes":    int(tt_raw["likes"].sum()),
        "shares":   int(tt_raw["shares"].sum()),
        "comments": int(tt_raw["comments"].sum()),
    }
    pdf_tt_funnel = pd.DataFrame([funnel_row])

    return unified, ts, pdf_tt_funnel


# ── Public API ────────────────────────────────────────────────────────────────
def load_all(use_spark: bool = True):
    """
    Returns (unified, ts, tt_funnel) as Pandas DataFrames.
      unified   — 330-row unified ad table (all platforms)
      ts        — daily time-series with 7-day rolling avg spend
      tt_funnel — 1-row TikTok video funnel summary
    PySpark is attempted first; falls back to pure Pandas automatically.
    """
    if use_spark and SPARK_OK:
        try:
            return _spark_pipeline()
        except Exception:
            pass          # fall through to Pandas
    return _pandas_pipeline()


def build_aggregates(unified: pd.DataFrame):
    """Derive all secondary DataFrames used by charts."""
    plat = (
        unified.groupby("platform")
        .agg(
            impressions  =("impressions","sum"),
            clicks       =("clicks","sum"),
            spend        =("spend","sum"),
            conversions  =("conversions","sum"),
            video_views  =("video_views","sum"),
            social_eng   =("social_eng","sum"),
            conv_value   =("conv_value","sum"),
        )
        .reset_index()
    )
    plat["ctr"] = plat["clicks"] / plat["impressions"]
    plat["cpc"] = plat["spend"]  / plat["clicks"]
    plat["cpa"] = plat["spend"]  / plat["conversions"]

    camp = (
        unified.groupby(["platform", "campaign_name"])
        .agg(
            impressions =("impressions","sum"),
            clicks      =("clicks","sum"),
            spend       =("spend","sum"),
            conversions =("conversions","sum"),
            conv_value  =("conv_value","sum"),
        )
        .reset_index()
    )
    camp["ctr"]  = camp["clicks"] / camp["impressions"]
    camp["cpa"]  = camp["spend"]  / camp["conversions"]
    camp["roas"] = camp["conv_value"] / camp["spend"]

    google_roas = (
        camp[camp["platform"] == "Google"]
        [["campaign_name","spend","conv_value","roas","cpa"]]
        .sort_values("roas", ascending=False)
        .copy()
    )

    return plat, camp, google_roas
