import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NovaRetail Dashboard", layout="wide")

# Title
st.title("NovaRetail Customer Intelligence Dashboard")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_excel("NR_dataset.xlsx")
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"])

    # --- CLEAN segment labels (removes real NaN AND string "nan") ---
    df["label"] = df["label"].astype(str).str.strip()
    df.loc[df["label"].str.lower().isin(["nan", "none", "null", "na", ""]), "label"] = pd.NA
    df = df.dropna(subset=["label"])
    # ---------------------------------------------------------------

    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("Filters")

segment_filter = st.sidebar.multiselect(
    "Select Segment",
    options=df["label"].unique(),
    default=df["label"].unique()
)

region_filter = st.sidebar.multiselect(
    "Select Region",
    options=df["CustomerRegion"].unique(),
    default=df["CustomerRegion"].unique()
)

category_filter = st.sidebar.multiselect(
    "Select Product Category",
    options=df["ProductCategory"].unique(),
    default=df["ProductCategory"].unique()
)

channel_filter = st.sidebar.multiselect(
    "Select Retail Channel",
    options=df["RetailChannel"].unique(),
    default=df["RetailChannel"].unique()
)

# Filter Data
filtered_df = df[
    (df["label"].isin(segment_filter)) &
    (df["CustomerRegion"].isin(region_filter)) &
    (df["ProductCategory"].isin(category_filter)) &
    (df["RetailChannel"].isin(channel_filter))
]

# KPIs
total_revenue = filtered_df["PurchaseAmount"].sum()
avg_revenue_per_customer = filtered_df.groupby("CustomerID")["PurchaseAmount"].sum().mean()
total_customers = filtered_df["CustomerID"].nunique()
decline_percentage = (filtered_df["label"] == "Decline").mean() * 100
avg_satisfaction = filtered_df["CustomerSatisfaction"].mean()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Revenue", f"${total_revenue:,.0f}")
col2.metric("Avg Revenue / Customer", f"${avg_revenue_per_customer:,.0f}")
col3.metric("Total Customers", total_customers)
col4.metric("% Decline Customers", f"{decline_percentage:.1f}%")
col5.metric("Avg Satisfaction", f"{avg_satisfaction:.2f}")

st.divider()

# Revenue by Segment
fig_segment = px.bar(
    filtered_df.groupby("label")["PurchaseAmount"].sum().reset_index(),
    x="label",
    y="PurchaseAmount",
    title="Revenue by Customer Segment"
)
st.plotly_chart(fig_segment, use_container_width=True)

# Revenue by Region
fig_region = px.bar(
    filtered_df.groupby("CustomerRegion")["PurchaseAmount"].sum().reset_index(),
    x="CustomerRegion",
    y="PurchaseAmount",
    title="Revenue by Region"
)
st.plotly_chart(fig_region, use_container_width=True)

# Revenue by Category
fig_category = px.bar(
    filtered_df.groupby("ProductCategory")["PurchaseAmount"].sum().reset_index(),
    x="ProductCategory",
    y="PurchaseAmount",
    title="Revenue by Product Category"
)
st.plotly_chart(fig_category, use_container_width=True)

# Revenue by Channel
fig_channel = px.bar(
    filtered_df.groupby("RetailChannel")["PurchaseAmount"].sum().reset_index(),
    x="RetailChannel",
    y="PurchaseAmount",
    title="Revenue by Sales Channel"
)
st.plotly_chart(fig_channel, use_container_width=True)

# Revenue Trend Over Time
trend = filtered_df.groupby(filtered_df["TransactionDate"].dt.to_period("M"))["PurchaseAmount"].sum().reset_index()
trend["TransactionDate"] = trend["TransactionDate"].astype(str)

fig_trend = px.line(
    trend,
    x="TransactionDate",
    y="PurchaseAmount",
    title="Monthly Revenue Trend"
)
st.plotly_chart(fig_trend, use_container_width=True)

# Satisfaction by Segment
fig_satisfaction = px.bar(
    filtered_df.groupby("label")["CustomerSatisfaction"].mean().reset_index(),
    x="label",
    y="CustomerSatisfaction",
    title="Average Satisfaction by Segment"
)
st.plotly_chart(fig_satisfaction, use_container_width=True)
