# app.py
# The web dashboard. Run locally with: streamlit run app.py
# Reads prices directly from GitHub so it always shows the latest scraper data.

import streamlit as st
import pandas as pd

# After pushing to GitHub, replace YOUR_GITHUB_USERNAME below with your actual username.
GITHUB_RAW_URL = (
    "https://raw.githubusercontent.com/krishgopalan62-rgb/material-tracker/main/data/prices.csv"
)

st.set_page_config(page_title="Material Price Tracker", layout="wide")
st.title("Material Price Tracker — White N Gold Construction Ltd.")


@st.cache_data(ttl=3600)  # Re-fetches from GitHub every 60 minutes
def load_data():
    try:
        df = pd.read_csv(GITHUB_RAW_URL)
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["date"]  = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"Data load failed: {e}")
        return pd.DataFrame()


df = load_data()

if df.empty:
    st.warning("No data yet. Run `python scraper.py` locally, commit `data/prices.csv` to GitHub, then reload.")
    st.stop()

# ── SIDEBAR FILTERS ────────────────────────────────────────────────────────
st.sidebar.header("Filters")

all_categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Category", all_categories)

date_options = ["Latest prices only"] + sorted(df["date"].dt.strftime("%Y-%m-%d").unique().tolist(), reverse=True)
selected_date = st.sidebar.selectbox("Date", date_options)

# ── FILTER ─────────────────────────────────────────────────────────────────
filtered = df.copy()

if selected_category != "All":
    filtered = filtered[filtered["category"] == selected_category]

if selected_date == "Latest prices only":
    # One row per supplier+item combo — the most recent date wins
    filtered = (
        filtered.sort_values("date")
        .drop_duplicates(subset=["supplier", "standard_name"], keep="last")
    )
else:
    filtered = filtered[filtered["date"].dt.strftime("%Y-%m-%d") == selected_date]

# ── METRICS ROW ────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Total Records",      len(df))
col2.metric("Suppliers Tracked",  df["supplier"].nunique())
col3.metric("Last Updated",       df["date"].max().strftime("%Y-%m-%d"))

# ── PRICE COMPARISON TABLE ─────────────────────────────────────────────────
st.subheader("Price Comparison by Supplier")
st.caption("Bold green cell = lowest price for that item. Use this to select your cheapest source per line item.")

if not filtered.empty:
    pivot = filtered.pivot_table(
        index=["category", "standard_name"],
        columns="supplier",
        values="price",
        aggfunc="min"
    ).round(2)

    styled = pivot.style.highlight_min(
        axis=1,
        color="#c6efce",
        props="color: #276221; font-weight: bold;"
    )
    st.dataframe(styled, use_container_width=True, height=500)
else:
    st.info("No data matches the selected filters.")

# ── RAW DATA ───────────────────────────────────────────────────────────────
with st.expander("View raw data"):
    st.dataframe(
        filtered[["date", "supplier", "raw_description", "standard_name", "category", "price", "unit"]]
        .sort_values("date", ascending=False),
        use_container_width=True
    )

# ── UNCATEGORIZED REVIEW ───────────────────────────────────────────────────
uncategorized = df[df["category"] == "Uncategorized"]
if not uncategorized.empty:
    with st.expander(f"Uncategorized items ({len(uncategorized)} rows) — add rules for these in normalizer.py"):
        st.dataframe(uncategorized[["supplier", "raw_description"]].drop_duplicates(), use_container_width=True)