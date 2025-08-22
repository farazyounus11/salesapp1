import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

st.set_page_config(page_title="Multi Dataset Dashboard", layout="wide")
st.title("📊 Multi-Dataset E-commerce Dashboard")

# --- Sidebar selector ---
dataset_choice = st.sidebar.radio(
    "Choose Dataset:",
    ("Sales Data (sales_data.csv)", "E-Comm Transactions (ecomm1.csv)")
)

# ================================================================
# 1. --- SALES DATASET DASHBOARD ---
# ================================================================
if dataset_choice == "Sales Data (sales_data.csv)":
    # Load dataset
    data = pd.read_csv("sales_data.csv", encoding="latin1")

    # --- Filters ---
    st.sidebar.header("Filters")
    year_filter = st.sidebar.multiselect(
        "Select Year:",
        options=sorted(data["YEAR"].unique()),
        default=sorted(data["YEAR"].unique())
    )

    productline_filter = st.sidebar.multiselect(
        "Select Product Line:",
        options=data["PRODUCTLINE"].unique(),
        default=data["PRODUCTLINE"].unique()
    )

    country_filter = st.sidebar.multiselect(
        "Select Country:",
        options=data["COUNTRY"].unique(),
        default=data["COUNTRY"].unique()
    )

    filtered_data = data[
        (data["YEAR"].isin(year_filter)) &
        (data["PRODUCTLINE"].isin(productline_filter)) &
        (data["COUNTRY"].isin(country_filter))
    ]

    # --- KPIs ---



        # --- KPIs ---
    total_sales = data["SALES"].sum()
    total_orders = data["ORDER_NUMBER"].nunique()
    total_quantity = data["QUANTITY_ORDERED"].sum()
    avg_order_value = round(total_sales / total_orders, 2)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales ($)", f"{total_sales:,.2f}")
    col2.metric("Total Orders", total_orders)
    col3.metric("Total Quantity", total_quantity)
    col4.metric("Avg Order Value ($)", f"{avg_order_value:,.2f}")

    # --- Average Sales by Product Line / City / Country ---
    st.subheader("📊 Average Sales Insights")

    avg_by_productline = (
        filtered_data.groupby("PRODUCTLINE")["SALES"].mean().reset_index().sort_values("SALES", ascending=False).head(3)
    )
    avg_by_city = (
        filtered_data.groupby("CITY")["SALES"].mean().reset_index().sort_values("SALES", ascending=False).head(3)
    )
    avg_by_country = (
        filtered_data.groupby("COUNTRY")["SALES"].mean().reset_index().sort_values("SALES", ascending=False).head(3)
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Top Avg Sales by Product Line**")
        for _, row in avg_by_productline.iterrows():
            st.metric(row["PRODUCTLINE"], f"{row['SALES']:,.2f}")

    with col2:
        st.markdown("**Top Avg Sales by City**")
        for _, row in avg_by_city.iterrows():
            st.metric(row["CITY"], f"{row['SALES']:,.2f}")

    with col3:
        st.markdown("**Top Avg Sales by Country**")
        for _, row in avg_by_country.iterrows():
            st.metric(row["COUNTRY"], f"{row['SALES']:,.2f}")
    
    st.subheader("Largest Deal Size Analysis")

    # Filter only Large deals
    large_deals = filtered_data[filtered_data["DEALSIZE"] == "Large"]

    # Most Large deals by Product Line
    top_productline_large = (
        large_deals.groupby("PRODUCTLINE")["DEALSIZE"]
        .count()
        .reset_index(name="Large Deals")
        .sort_values("Large Deals", ascending=False)
        .head(1)
    )

    # Most Large deals by City
    top_city_large = (
        large_deals.groupby("CITY")["DEALSIZE"]
        .count()
        .reset_index(name="Large Deals")
        .sort_values("Large Deals", ascending=False)
        .head(1)
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Product Line with Most Large Deals",
            f"{top_productline_large.iloc[0]['PRODUCTLINE']} ({top_productline_large.iloc[0]['Large Deals']})"
        )

    with col2:
        st.metric(
            "City with Most Large Deals",
            f"{top_city_large.iloc[0]['CITY']} ({top_city_large.iloc[0]['Large Deals']})"
        )


    # --- Sales Over Time ---
    st.subheader("📈 Sales Trend Over Time")
    filtered_data["ORDER_DATE"] = pd.to_datetime(filtered_data["ORDER_DATE"])
    time_sales = filtered_data.groupby(filtered_data["ORDER_DATE"].dt.to_period("M"))["SALES"].sum().reset_index()
    time_sales["ORDER_DATE"] = time_sales["ORDER_DATE"].astype(str)
    fig_time = px.line(time_sales, x="ORDER_DATE", y="SALES", title="Monthly Sales Trend")
    st.plotly_chart(fig_time, use_container_width=True)

    # --- Sales Trend by Top 5 Product Lines ---
    st.subheader("📈 Sales Trend: Top 5 Product Lines")
    top5_products = (
        filtered_data.groupby("PRODUCTLINE")["SALES"]
        .sum()
        .nlargest(5)
        .index
    )
    product_trend = (
        filtered_data[filtered_data["PRODUCTLINE"].isin(top5_products)]
        .groupby([filtered_data["ORDER_DATE"].dt.to_period("M"), "PRODUCTLINE"])["SALES"]
        .sum()
        .reset_index()
    )
    product_trend["ORDER_DATE"] = product_trend["ORDER_DATE"].astype(str)
    fig_prod_trend = px.line(
        product_trend,
        x="ORDER_DATE",
        y="SALES",
        color="PRODUCTLINE",
        title="Monthly Sales Trend by Top 5 Product Lines"
    )
    st.plotly_chart(fig_prod_trend, use_container_width=True)

    # --- Sales Trend by Top 5 Countries ---
    st.subheader("📈 Sales Trend: Top 5 Countries")
    top5_countries = (
        filtered_data.groupby("COUNTRY")["SALES"]
        .sum()
        .nlargest(5)
        .index
    )
    country_trend = (
        filtered_data[filtered_data["COUNTRY"].isin(top5_countries)]
        .groupby([filtered_data["ORDER_DATE"].dt.to_period("M"), "COUNTRY"])["SALES"]
        .sum()
        .reset_index()
    )
    country_trend["ORDER_DATE"] = country_trend["ORDER_DATE"].astype(str)
    fig_country_trend = px.line(
        country_trend,
        x="ORDER_DATE",
        y="SALES",
        color="COUNTRY",
        title="Monthly Sales Trend by Top 5 Countries"
    )
    st.plotly_chart(fig_country_trend, use_container_width=True)

    # --- 3 Charts in Columns ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📊 Sales by Product Line")
        product_sales = filtered_data.groupby("PRODUCTLINE")["SALES"].sum().reset_index().sort_values("SALES", ascending=False)
        fig_prod = px.bar(product_sales, x="PRODUCTLINE", y="SALES", title="Sales by Product Line")
        st.plotly_chart(fig_prod, use_container_width=True)

    with col2:
        st.subheader("🌍 Sales by Country (Top 5)")
        country_sales = filtered_data.groupby("COUNTRY")["SALES"].sum().reset_index().sort_values("SALES", ascending=False).head(5)
        fig_country = px.bar(country_sales, x="COUNTRY", y="SALES", title="Top 5 Countries")
        st.plotly_chart(fig_country, use_container_width=True)

    with col3:
        st.subheader("📦 Deal Size Distribution")
        deals = filtered_data["DEALSIZE"].value_counts().reset_index()
        deals.columns = ["Deal Size", "Count"]
        fig_deals = px.pie(deals, values="Count", names="Deal Size", title="Deal Size Breakdown")
        st.plotly_chart(fig_deals, use_container_width=True)

    # --- Top Customers ---
    st.subheader("👤 Top Customers by Sales")
    top_customers = filtered_data.groupby("CUSTOMER_NAME")["SALES"].sum().reset_index().sort_values("SALES", ascending=False).head(10)
    fig_customers = px.bar(top_customers, x="CUSTOMER_NAME", y="SALES", title="Top 10 Customers")
    st.plotly_chart(fig_customers, use_container_width=True)

    # --- Show Data Table ---
    st.subheader("📋 Filtered Sales Data")
    st.dataframe(filtered_data)


# ================================================================
# 2. --- ECOMM1 TRANSACTIONS DASHBOARD ---
# ================================================================
elif dataset_choice == "E-Comm Transactions (ecomm1.csv)":
    # Load dataset
    data = pd.read_csv("ecomm1.csv", encoding="latin1")
    data["Transaction Date"] = pd.to_datetime(data["Transaction Date"])

    # --- Filters ---
    st.sidebar.header("Filters")
    category_filter = st.sidebar.multiselect(
        "Select Product Category:",
        options=data["Product Category"].unique(),
        default=data["Product Category"].unique()
    )

    status_filter = st.sidebar.multiselect(
        "Select Purchase Status:",
        options=data["Purchase Completed"].unique(),
        default=data["Purchase Completed"].unique()
    )

    filtered_data = data[
        (data["Product Category"].isin(category_filter)) &
        (data["Purchase Completed"].isin(status_filter))
    ]

    # --- KPIs ---
    total_transactions = len(filtered_data)
    completed_transactions = (filtered_data["Purchase Completed"] == "Completed").sum()
    canceled_transactions = (filtered_data["Purchase Completed"] == "Canceled").sum()
    unique_categories = filtered_data["Product Category"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Transactions", total_transactions)
    col2.metric("Completed", completed_transactions)
    col3.metric("Canceled", canceled_transactions)
    col4.metric("Unique Categories", unique_categories)

    # --- Transactions Over Time ---
    st.subheader("📈 Transactions Over Time")
    time_trend = filtered_data.groupby(filtered_data["Transaction Date"].dt.to_period("M")).size().reset_index(name="Count")
    time_trend["Transaction Date"] = time_trend["Transaction Date"].astype(str)
    fig_time = px.line(time_trend, x="Transaction Date", y="Count", title="Monthly Transactions Trend")
    st.plotly_chart(fig_time, use_container_width=True)

    # --- Category + Status ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Transactions by Product Category")
        category_sales = filtered_data["Product Category"].value_counts().reset_index()
        category_sales.columns = ["Category", "Transactions"]
        fig_category = px.bar(category_sales, x="Category", y="Transactions", title="By Category")
        st.plotly_chart(fig_category, use_container_width=True)

    with col2:
        st.subheader("✅ Purchase Status Breakdown")
        status_counts = filtered_data["Purchase Completed"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_status = px.pie(status_counts, values="Count", names="Status", title="Completed vs Canceled")
        st.plotly_chart(fig_status, use_container_width=True)

    # --- Map of Transactions ---
    st.subheader("🌍 Transaction Locations")

    # Rename for pydeck
    map_data = filtered_data.rename(columns={"Latitude": "lat", "Longitude": "lon"})

    # Compute the center of the map
    midpoint = (map_data["lat"].mean(), map_data["lon"].mean())

    # Define the hexagon layer for density
    hex_layer = pdk.Layer(
        "HexagonLayer",
        data=map_data,
        get_position='[lon, lat]',
        radius=300,        # radius in meters
        elevation_scale=50,
        elevation_range=[0, 1000],
        pickable=True,
        extruded=True,
    )

    # Set the view
    view_state = pdk.ViewState(
        latitude=midpoint[0],
        longitude=midpoint[1],
        zoom=9,           # adjust zoom level
        pitch=50,
    )

    # Render the map
    r = pdk.Deck(layers=[hex_layer], initial_view_state=view_state)
    st.pydeck_chart(r)

    # --- Show Data Table ---
    st.subheader("📋 Filtered Transaction Data")
    st.dataframe(filtered_data)
