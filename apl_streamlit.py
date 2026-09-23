import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset with encoding fix
df = pd.read_csv("APL_Logistics_clean.csv")


st.set_page_config(page_title="Supply Chain Dashboard", layout="wide")

st.title("📊 Customer, Product & Profitability Analysis")
st.subheader("Supply Chain Operations – APL Logistics")

# ---------------- KPIs ----------------
total_revenue = df['Sales'].sum()
total_profit = df['Order Profit Per Order'].sum()
profit_margin = (total_profit / total_revenue) * 100
late_delivery = df['Late_delivery_risk'].mean() * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${total_revenue:,.0f}")
col2.metric("Total Profit", f"${total_profit:,.0f}")
col3.metric("Profit Margin %", f"{profit_margin:.2f}%")
col4.metric("Late Delivery %", f"{late_delivery:.2f}%")

st.markdown("---")

# ---------------- Sidebar Filters ----------------
st.sidebar.header("🔧 Filters")
selected_region = st.sidebar.selectbox("Select Region", options=df['Order Region'].unique())
selected_market = st.sidebar.selectbox("Select Market", options=df['Market'].unique())
selected_segment = st.sidebar.selectbox("Select Customer Segment", options=df['Customer Segment'].unique())

filtered_df = df[(df['Order Region'] == selected_region) & 
                 (df['Market'] == selected_market) & 
                 (df['Customer Segment'] == selected_segment)]

# ---------------- Revenue & Profit Overview ----------------
st.subheader("💰 Revenue & Profit Overview")
fig_rev = px.bar(df.groupby('Order Region')[['Sales','Order Profit Per Order']].sum().reset_index(),
                 x='Order Region', y=['Sales','Order Profit Per Order'],
                 title="Revenue vs Profit by Region", barmode='group')
st.plotly_chart(fig_rev, use_container_width=True)

# ---------------- Customer Value Dashboard ----------------
st.subheader("👥 Customer Value Dashboard")
customer_summary = filtered_df.groupby('Customer Id')[['Sales','Order Profit Per Order']].sum().reset_index()
customer_summary['Profit Margin %'] = (customer_summary['Order Profit Per Order'] / customer_summary['Sales']) * 100
customer_summary['Customer Value Index'] = customer_summary['Order Profit Per Order'] / customer_summary['Sales']

top_customers = customer_summary.sort_values(by='Order Profit Per Order', ascending=False).head(10)
bottom_customers = customer_summary.sort_values(by='Order Profit Per Order', ascending=True).head(10)

fig_top_cust = px.bar(top_customers, x='Customer Id', y='Order Profit Per Order',
                      title="Top 10 Profitable Customers", text_auto=True)
fig_bottom_cust = px.bar(bottom_customers, x='Customer Id', y='Order Profit Per Order',
                         title="Bottom 10 Loss-Making Customers", text_auto=True)

st.plotly_chart(fig_top_cust, use_container_width=True)
st.plotly_chart(fig_bottom_cust, use_container_width=True)

# ---------------- Product & Category Performance ----------------
st.subheader("📦 Product & Category Performance")
category_summary = df.groupby('Category Name')[['Sales','Order Profit Per Order']].sum().reset_index()
category_summary['Category Margin %'] = (category_summary['Order Profit Per Order'] / category_summary['Sales']) * 100

fig_category = px.treemap(category_summary, path=['Category Name'], values='Order Profit Per Order',
                          color='Category Margin %', title="Category Profitability Heatmap",
                          color_continuous_scale='RdYlGn')
st.plotly_chart(fig_category, use_container_width=True)

product_summary = filtered_df.groupby('Product Name')[['Sales','Order Profit Per Order']].sum().reset_index()
product_summary['Profit Margin %'] = (product_summary['Order Profit Per Order'] / product_summary['Sales']) * 100
top_products = product_summary.sort_values(by='Order Profit Per Order', ascending=False).head(10)

fig_products = px.bar(top_products, x='Product Name', y='Order Profit Per Order',
                      title="Top 10 Profitable Products", text_auto=True)
st.plotly_chart(fig_products, use_container_width=True)

# ---------------- Discount Impact Analyzer ----------------
st.subheader("💸 Discount Impact Analyzer")
df['Discount Bucket'] = pd.cut(df['Order Item Discount Rate'],
                               bins=[0,0.1,0.2,0.3,0.5,1],
                               labels=['0-10%','10-20%','20-30%','30-50%','50-100%'])
discount_summary = df.groupby('Discount Bucket')['Order Item Profit Ratio'].mean().reset_index()

fig_discount = px.bar(discount_summary, x='Discount Bucket', y='Order Item Profit Ratio',
                      title="Average Profit Ratio by Discount Bucket", text_auto=True)
st.plotly_chart(fig_discount, use_container_width=True)

fig_scatter = px.scatter(df, x='Order Item Discount Rate', y='Order Item Profit Ratio',
                         title="Discount Rate vs Profit Ratio", opacity=0.5)
st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------- Market & Regional Profit Analysis ----------------
st.subheader("🌍 Market & Regional Profit Analysis")
market_summary = df.groupby('Market')[['Sales','Order Profit Per Order']].sum().reset_index()
market_summary['Profit Margin %'] = (market_summary['Order Profit Per Order'] / market_summary['Sales']) * 100

fig_market = px.bar(market_summary, x='Market', y='Order Profit Per Order',
                    title="Profit by Market", text_auto=True)
st.plotly_chart(fig_market, use_container_width=True)

country_summary = df.groupby('Order Country')[['Sales','Order Profit Per Order']].sum().reset_index()
country_summary['Profit Margin %'] = (country_summary['Order Profit Per Order'] / country_summary['Sales']) * 100

fig_country = px.choropleth(country_summary, locations='Order Country', locationmode='country names',
                            color='Profit Margin %', hover_name='Order Country',
                            title="Profit Margin by Country", color_continuous_scale='RdYlGn')
st.plotly_chart(fig_country, use_container_width=True)

# ---------------- Supply Chain Performance ----------------
st.subheader("🚚 Supply Chain Performance")
df['Delay_Days'] = df['Days for shipping (real)'] - df['Days for shipment (scheduled)']
delay_summary = df.groupby('Order Region')['Delay_Days'].mean().reset_index()

fig_delay = px.bar(delay_summary, x='Order Region', y='Delay_Days',
                   title="Average Delay Days by Region", text_auto=True)
st.plotly_chart(fig_delay, use_container_width=True)

risk_summary = df.groupby('Market')['Late_delivery_risk'].mean().reset_index()
risk_summary['Late %'] = risk_summary['Late_delivery_risk'] * 100

fig_risk = px.bar(risk_summary, x='Market', y='Late %',
                  title="Late Delivery % by Market", text_auto=True)
st.plotly_chart(fig_risk, use_container_width=True)

st.markdown("---")
st.success("✅ Dashboard Ready: KPIs, Revenue & Profit, Customer Value, Product & Category, Discount Impact, Market & Regional, and Supply Chain modules integrated.")
