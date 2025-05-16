import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page config
st.set_page_config(page_title="Sales Dashboard", layout="wide", page_icon="📊")

# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data
def load_data():
    file = "sales_data.csv"
    if not os.path.exists(file):
        st.error("❌ 'sales_data.csv' not found. Please add it to the Task_4 folder.")
        return None
    
    df = pd.read_csv(file, encoding="ISO-8859-1")
    df.columns = df.columns.str.upper()  # Normalize columns to uppercase

    # Parse ORDERDATE safely
    if 'ORDERDATE' in df.columns:
        df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], errors='coerce')
        df['MONTH'] = df['ORDERDATE'].dt.to_period("M").astype(str)
    else:
        st.warning("⚠️ 'ORDERDATE' column not found — Month-wise charts will be skipped.")
        df['MONTH'] = 'Unknown'
    
    return df

df = load_data()
if df is None:
    st.stop()

# -------------------------
# SIDEBAR FILTERS
# -------------------------
with st.sidebar:
    st.header("📋 Filter Data")
    countries = st.multiselect("Select Country", df['COUNTRY'].dropna().unique(), default=df['COUNTRY'].dropna().unique())
    categories = st.multiselect("Select Product Line", df['PRODUCTLINE'].dropna().unique(), default=df['PRODUCTLINE'].dropna().unique())

filtered_df = df[df['COUNTRY'].isin(countries) & df['PRODUCTLINE'].isin(categories)]

# -------------------------
# KPI SECTION
# -------------------------
st.title("📊 Sales Performance Dashboard")
st.markdown("Interactive dashboard to explore international product sales.")

total_sales = filtered_df['SALES'].sum()
total_quantity = filtered_df['QUANTITYORDERED'].sum()
avg_price = filtered_df['PRICEEACH'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Sales", f"${total_sales:,.2f}")
col2.metric("📦 Units Sold", f"{total_quantity:,}")
col3.metric("🏷️ Avg. Price Each", f"${avg_price:.2f}")

# -------------------------
# CHARTS
# -------------------------
# Monthly Sales
st.subheader("📅 Monthly Sales Trend")
monthly_sales = filtered_df.groupby('MONTH')['SALES'].sum().reset_index()
monthly_sales = monthly_sales.sort_values(by='MONTH')
if not monthly_sales.empty:
    fig1 = px.line(monthly_sales, x="MONTH", y="SALES", markers=True, template="plotly_white")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("No data for selected filters.")

# Sales by Product Line
st.subheader("📦 Sales by Product Line")
if not filtered_df.empty:
    cat_sales = filtered_df.groupby('PRODUCTLINE')['SALES'].sum().reset_index()
    fig2 = px.bar(cat_sales, x="PRODUCTLINE", y="SALES", color="PRODUCTLINE", template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No data for selected filters.")

# Sales by Country
st.subheader("🌍 Sales by Country")
if not filtered_df.empty:
    country_sales = filtered_df.groupby('COUNTRY')['SALES'].sum().reset_index()
    fig3 = px.pie(country_sales, names='COUNTRY', values='SALES', template="plotly_white", hole=0.4)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("No data for selected filters.")

# -------------------------
# RAW DATA EXPANDER
# -------------------------
with st.expander("🔍 View Raw Data"):
    st.dataframe(filtered_df)
