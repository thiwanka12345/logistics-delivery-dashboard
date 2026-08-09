import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Streamlit Page Setup
st.set_page_config(
    page_title="Logistics & Delivery Performance Dashboard",
    page_icon="🚛",
    layout="wide"
)

# Title & Description
st.title("🚛 Logistics Operations & Delivery Performance Dashboard")
st.markdown("Tracking **62,000+ shipments** across regions, warehouses, and vehicle types.")

# ---------------------------------------------------------
# DATA LOADING / GENERATION
# ---------------------------------------------------------
@st.cache_data
def load_data():
    # If using a CSV file, replace with: df = pd.read_csv("your_file.csv")
    np.random.seed(42)
    n_rows = 62000
    
    dates = pd.date_range(start="2020-01-01", end="2025-12-31", periods=n_rows)
    regions = ["North", "South", "East", "West", "Central"]
    warehouses = ["WH-Alpha", "WH-Beta", "WH-Gamma", "WH-Delta"]
    vehicles = ["Trailer", "Container Truck", "Van", "3-Wheeler"]
    routes = ["Colombo-Kandy", "Madurai Route", "Chennai-Bangalore", "Galle-Matara"]
    categories = ["Electronics", "Apparel", "FMCG", "Industrial Parts"]

    df = pd.DataFrame({
        "Shipment_ID": [f"SHP{100000 + i}" for i in range(n_rows)],
        "Date": dates,
        "Year": dates.year,
        "Quarter": dates.quarter,
        "Month": dates.strftime("%B"),
        "Region": np.random.choice(regions, n_rows),
        "Warehouse": np.random.choice(warehouses, n_rows),
        "Vehicle_Type": np.random.choice(vehicles, n_rows),
        "Route": np.random.choice(routes, n_rows, p=[0.3, 0.2, 0.3, 0.2]),
        "Product_Category": np.random.choice(categories, n_rows),
        "On_Time": np.random.choice([1, 0], n_rows, p=[0.85, 0.15]),
        "Transit_Days": np.random.randint(1, 15, n_rows),
        "Shipping_Cost": np.random.uniform(50, 500, n_rows),
        "Fuel_Cost": np.random.uniform(20, 150, n_rows),
        "Revenue": np.random.uniform(200, 2000, n_rows),
        "Customer_Rating": np.random.uniform(1.0, 5.0, n_rows)
    })
    
    # Custom bottleneck simulation for 'Madurai Route'
    df.loc[df["Route"] == "Madurai Route", "Transit_Days"] = np.random.randint(40, 58, (df["Route"] == "Madurai Route").sum())
    
    return df

df = load_data()

# ---------------------------------------------------------
# SIDEBAR - INTERACTIVE SLICERS / FILTERS
# ---------------------------------------------------------
st.sidebar.header("🔍 Filter Options")

selected_year = st.sidebar.multiselect("Year", options=df["Year"].unique(), default=df["Year"].unique())
selected_region = st.sidebar.multiselect("Region", options=df["Region"].unique(), default=df["Region"].unique())
selected_warehouse = st.sidebar.multiselect("Warehouse", options=df["Warehouse"].unique(), default=df["Warehouse"].unique())
selected_vehicle = st.sidebar.multiselect("Vehicle Type", options=df["Vehicle_Type"].unique(), default=df["Vehicle_Type"].unique())

# Apply Filters
filtered_df = df[
    (df["Year"].isin(selected_year)) &
    (df["Region"].isin(selected_region)) &
    (df["Warehouse"].isin(selected_warehouse)) &
    (df["Vehicle_Type"].isin(selected_vehicle))
]

# ---------------------------------------------------------
# REAL-TIME KPIS
# ---------------------------------------------------------
st.markdown("### 📊 Real-Time Key Performance Indicators (KPIs)")

col1, col2, col3, col4 = st.columns(4)

on_time_rate = (filtered_df["On_Time"].mean() * 100) if not filtered_df.empty else 0
avg_transit = filtered_df["Transit_Days"].mean() if not filtered_df.empty else 0
avg_cost = filtered_df["Shipping_Cost"].mean() if not filtered_df.empty else 0
avg_rating = filtered_df["Customer_Rating"].mean() if not filtered_df.empty else 0

col1.metric("On-Time Delivery Rate", f"{on_time_rate:.1f}%")
col2.metric("Avg Transit Time", f"{avg_transit:.1f} Days")
col3.metric("Avg Shipping Cost", f"${avg_cost:.2f}")
col4.metric("Customer Rating", f"⭐ {avg_rating:.1f} / 5.0")

st.divider()

# ---------------------------------------------------------
# NEW: AUTOMATED KEY INSIGHTS SECTION
# ---------------------------------------------------------
st.markdown("### 💡 Key Dynamic Insights & Actionable Takeaways")

if not filtered_df.empty:
    # Calculations for automated insights
    worst_route = filtered_df.groupby("Route")["Transit_Days"].mean().idxmax()
    worst_route_days = filtered_df.groupby("Route")["Transit_Days"].mean().max()
    
    best_category = filtered_df.groupby("Product_Category")["Revenue"].sum().idxmax()
    best_cat_rev = filtered_df.groupby("Product_Category")["Revenue"].sum().max()
    
    highest_fuel_vehicle = filtered_df.groupby("Vehicle_Type")["Fuel_Cost"].sum().idxmax()
    highest_fuel_cost = filtered_df.groupby("Vehicle_Type")["Fuel_Cost"].sum().max()
    
    delayed_shipments = (filtered_df["On_Time"] == 0).sum()
    total_shipments = len(filtered_df)

    insight_col1, insight_col2 = st.columns(2)

    with insight_col1:
        st.warning(f"⚠️ **Route Bottleneck:** The **{worst_route}** has the highest average transit time (**{worst_route_days:.1f} days**). Operational review recommended.")
        st.info(f"⛽ **Fuel Consumption:** **{highest_fuel_vehicle}** vehicles consumed the highest total fuel cost (**${highest_fuel_cost:,.2f}**).")

    with insight_col2:
        st.success(f"💰 **Top Revenue Driver:** **{best_category}** generated the highest overall revenue (**${best_cat_rev:,.2f}**).")
        st.error(f"🚨 **Delayed Shipments:** **{delayed_shipments:,}** out of **{total_shipments:,}** shipments experienced delays ({100 - on_time_rate:.1f}% delay rate).")
else:
    st.info("No data available for the selected filters.")

st.divider()

# ---------------------------------------------------------
# CHARTS & VISUALIZATIONS
# ---------------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    # 📈 Shipment Trend
    st.subheader("📈 Monthly Shipment Volume Trend")
    trend_data = filtered_df.groupby(filtered_df["Date"].dt.to_period("M")).size().reset_index(name="Shipments")
    trend_data["Date"] = trend_data["Date"].astype(str)
    fig_trend = px.line(trend_data, x="Date", y="Shipments", markers=True, color_discrete_sequence=["#1f77b4"])
    st.plotly_chart(fig_trend, use_container_width=True)

    # 🗺️ Route Bottlenecks Analysis
    st.subheader("🗺️ Avg Transit Time by Route (Bottlenecks)")
    route_data = filtered_df.groupby("Route")["Transit_Days"].mean().reset_index().sort_values("Transit_Days", ascending=False)
    fig_route = px.bar(route_data, x="Transit_Days", y="Route", orientation="h", color="Transit_Days", color_continuous_scale="Reds")
    st.plotly_chart(fig_route, use_container_width=True)

with col_right:
    # 💰 Revenue by Product Category
    st.subheader("💰 Revenue by Product Category")
    rev_data = filtered_df.groupby("Product_Category")["Revenue"].sum().reset_index()
    fig_rev = px.pie(rev_data, names="Product_Category", values="Revenue", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig_rev, use_container_width=True)

    # ⛽ Fuel Cost Tracking by Vehicle Type
    st.subheader("⛽ Fuel Cost Tracking by Vehicle Type")
    fuel_data = filtered_df.groupby("Vehicle_Type")["Fuel_Cost"].sum().reset_index()
    fig_fuel = px.bar(fuel_data, x="Vehicle_Type", y="Fuel_Cost", color="Vehicle_Type", color_discrete_sequence=px.colors.qualitative.Bold)
    st.plotly_chart(fig_fuel, use_container_width=True)

# ---------------------------------------------------------
# DATA TABLE VIEW
# ---------------------------------------------------------
with st.expander("📄 View Filtered Raw Data (First 100 records)"):
    st.dataframe(filtered_df.head(100))