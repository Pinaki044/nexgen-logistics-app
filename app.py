import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="NexGen Cost Intelligence Platform", layout="wide")

st.title("📦 NexGen Logistics – Cost Intelligence Platform")
st.markdown("Identify cost leakages and optimization opportunities across logistics operations.")

# -------------------- Load Data --------------------
orders = pd.read_csv("Case study internship data/orders.csv")
routes = pd.read_csv("Case study internship data/routes_distance.csv")
delivery = pd.read_csv("Case study internship data/delivery_performance.csv")
costs = pd.read_csv("Case study internship data/cost_breakdown.csv")

# -------------------- Merge Data --------------------
df = orders.merge(routes, on="Order_ID", how="left") \
           .merge(delivery, on="Order_ID", how="left") \
           .merge(costs, on="Order_ID", how="left")

df.fillna(0, inplace=True)

# -------------------- Derived Metrics --------------------
df["Total_Cost_INR"] = (
    df["Fuel_Cost"] +
    df["Labor_Cost"] +
    df["Vehicle_Maintenance"] +
    df["Insurance"] +
    df["Packaging_Cost"] +
    df["Technology_Platform_Fee"] +
    df["Other_Overhead"]
)



#df["cost_per_km"] = df["total_cost"] / df["distance_traveled"].replace(0, 1)

# -------------------- Sidebar Filters --------------------
st.sidebar.header("🔍 Filters")

priority_filter = st.sidebar.multiselect(
    "Delivery Priority",
    options=df["Priority"].unique()
)

category_filter = st.sidebar.multiselect(
    "Product Category",
    options=df["Product_Category"].unique()
)

if priority_filter:
    df = df[df["Priority"].isin(priority_filter)]

if category_filter:
    df = df[df["Product_Category"].isin(category_filter)]

# -------------------- KPI Section --------------------
st.subheader("📊 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Operational Cost", f"₹{df['Total_Cost_INR'].sum():,.0f}")
col2.metric("📦 Total Orders", df.shape[0])

df["Cost_per_KM"] = df["Total_Cost_INR"] / df["Distance_KM"]
col3.metric("🚚 Average Cost per KM", f"₹{df['Cost_per_KM'].mean():.2f}")


# -------------------- Visualizations --------------------
st.subheader("📈 Cost Analysis")

col1, col2 = st.columns(2)

with col1:
    st.write("### Total Cost by Route")
    st.bar_chart(df.groupby("Route")["Total_Cost_INR"].sum())

with col2:
    st.write("### Cost vs Distance")
    st.line_chart(df.groupby("Distance_KM")["Total_Cost_INR"].mean())

# Pie chart
st.subheader("💸 Cost Composition")

fig, ax = plt.subplots()
cost_components = df[[
    "Fuel_Cost",
    "Labor_Cost",
    "Vehicle_Maintenance",
    "Other_Overhead"
]].sum()



ax.pie(cost_components, labels=cost_components.index, autopct="%1.1f%%")
ax.set_title("Overall Cost Breakdown")
st.pyplot(fig)

# Scatter plot
st.subheader("⏱ Delay Impact on Cost")
st.scatter_chart(df, x="Traffic_Delay_Minutes", y="Total_Cost_INR")

# -------------------- Cost Leakage Detection --------------------
st.subheader("🚨 High Cost Leakage Orders")

threshold = df["Cost_per_KM"].mean()
leakage_df = df[df["Cost_per_KM"] > threshold]

st.dataframe(
    leakage_df[["Order_ID", "Route", "Cost_per_KM", "Traffic_Delay_Minutes"]]

)

# -------------------- Download Report --------------------
st.subheader("⬇ Download Detailed Cost Report")

st.download_button(
    label="Download CSV",
    data=df.to_csv(index=False),
    file_name="nexgen_cost_analysis_report.csv",
    mime="text/csv"
)
