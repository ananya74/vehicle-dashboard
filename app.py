import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_manufacturer_data, load_vehicle_class_data, load_qoq_data
import altair as alt
# Load data
m2024 = load_manufacturer_data("data/m2024.xlsx", 2024)
m2025 = load_manufacturer_data("data/m2025.xlsx", 2025)

vehicle_2w = load_vehicle_class_data("data/2W.xlsx", 2025, '2W')
vehicle_3w = load_vehicle_class_data("data/3W.xlsx", 2025, '3W')
vehicle_4w = load_vehicle_class_data("data/4W.xlsx", 2025, '4W')


qoq_df = load_qoq_data("data/q2024.xlsx", "data/q2025.xlsx")
#st.dataframe(qoq_df.head())
#st.write("Columns in DataFrame:", qoq_df.columns.tolist())


# Combine manufacturer data
manu_df = pd.concat([m2024, m2025], ignore_index=True)

# Combine vehicle class data
vehicle_df = pd.concat([vehicle_2w, vehicle_3w, vehicle_4w], ignore_index=True)


# App UI
st.set_page_config(page_title="Vehicle Registration Dashboard", layout="wide")
st.title("Vehicle Registration Trends (Investor View)")

# Sidebar filters
st.sidebar.header("Filter Options")
vehicle_type = st.sidebar.selectbox("Vehicle Type", ["2W", "3W", "4W", "All"])
year_range = st.sidebar.slider("Year", 2024, 2025, (2024, 2025))

st.markdown("### Manufacturer-wise Registration Trends")

# Manufacturer Trends
filtered = manu_df[(manu_df["Year"] >= year_range[0]) & (manu_df["Year"] <= year_range[1])]
top_makers = filtered.groupby(["Maker", "Year"])["TOTAL"].sum().reset_index()

fig1 = px.line(top_makers, x="Year", y="TOTAL", color="Maker", markers=True,
               title="Yearly Registration by Manufacturer")
st.plotly_chart(fig1, use_container_width=True)

# YoY % Growth Table
st.markdown("### Year-on-Year Growth (Top Manufacturers)")
pivot = top_makers.pivot(index='Maker', columns='Year', values='TOTAL').fillna(0)

pivot[2024] = pd.to_numeric(pivot[2024], errors='coerce').fillna(0)
pivot[2025] = pd.to_numeric(pivot[2025], errors='coerce').fillna(0)
pivot['YoY Growth %'] = ((pivot[2025] - pivot[2024]) / pivot[2024].replace(0, 1)) * 100

st.dataframe(pivot.sort_values('YoY Growth %', ascending=False).round(2))

# YoY Growth Chart
# Refined YoY Growth Chart
st.markdown("### Top 15 Manufacturers by YoY Growth %")

# Limit to Top 15 by absolute growth % (positive or negative)
pivot_reset = pivot.reset_index()
top_yoy = pivot_reset.copy()
top_yoy["YoY Growth % Abs"] = top_yoy["YoY Growth %"].abs()
top_yoy = top_yoy.sort_values("YoY Growth % Abs", ascending=False).head(15)

fig_yoy = px.bar(
    top_yoy.sort_values("YoY Growth %"),  # sorted for better visual flow
    x="YoY Growth %",
    y="Maker",
    orientation="h",
    color="YoY Growth %",
    color_continuous_scale="RdYlGn",
    text="YoY Growth %"
)

fig_yoy.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig_yoy.update_layout(yaxis_title="", xaxis_title="YoY Growth (%)", height=600)

st.plotly_chart(fig_yoy, use_container_width=True)


top_n = st.sidebar.slider("Top N Manufacturers by 2025 Volume", 5, 20, 10)
top_2025_makers = pivot.sort_values(2025, ascending=False).head(top_n).reset_index()

fig_top = px.bar(top_2025_makers, x="Maker", y=2025, title=f"Top {top_n} Manufacturers in 2025")
st.plotly_chart(fig_top, use_container_width=True)




# Normalize month to quarter
month_to_quarter = {
    "JAN": 1, "FEB": 1, "MAR": 1,
    "APR": 2, "MAY": 2, "JUN": 2,
    "JUL": 3, "AUG": 3, "SEP": 3,
    "OCT": 4, "NOV": 4, "DEC": 4
}

# Ensure month is uppercase and clean
qoq_df["Month"] = qoq_df["Month"].str.strip().str.upper()
qoq_df["Quarter"] = qoq_df["Month"].map(month_to_quarter)

# Create Year-Quarter column
qoq_df["Year-Quarter"] = qoq_df["YEAR"].astype(str) + "-Q" + qoq_df["Quarter"].astype(str)

# Calculate QoQ Growth %
qoq_df = qoq_df.sort_values(by=["Maker", "YEAR", "Quarter"])
qoq_df["QoQ Growth %"] = qoq_df.groupby("Maker")["Value"].pct_change() * 100

# --- Streamlit UI ---
st.header("Quarter-on-Quarter (QoQ) Growth Analysis")

# Manufacturer dropdown
selected_makers = st.multiselect(
    "Select Manufacturers to Display:",
    options=qoq_df["Maker"].unique(),
    default=qoq_df["Maker"].unique()[:5]
)

# Filtered data
filtered_df = qoq_df[qoq_df["Maker"].isin(selected_makers)]

# Plot chart
chart = alt.Chart(filtered_df).mark_line(point=True).encode(
    x=alt.X("Year-Quarter:N", sort=None, title="Year-Quarter"),
    y=alt.Y("Value:Q", title="Registrations"),
    color="Maker:N",
    tooltip=["Maker", "Year-Quarter", "Value", alt.Tooltip("QoQ Growth %", format=".2f")]
).properties(width=800, height=400)

st.altair_chart(chart, use_container_width=True)

# Download QoQ CSV
csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download QoQ Data (CSV)", csv_data, file_name="qoq_growth.csv", mime="text/csv")





st.markdown("###  Vehicle Category Overview")

# Vehicle Category Stats
if vehicle_type != "All":
    vehicle_df_filtered = vehicle_df[vehicle_df["category"] == vehicle_type]
else:
    vehicle_df_filtered = vehicle_df

fig2 = px.bar(vehicle_df_filtered, x="Vehicle Class", y="TOTAL", color="category",
              title=f"{vehicle_type if vehicle_type != 'All' else 'All Vehicle Types'} - Category Totals")
st.plotly_chart(fig2, use_container_width=True)



# Ensure TOTAL column is numeric
vehicle_2w["TOTAL"] = pd.to_numeric(vehicle_2w["TOTAL"], errors="coerce").fillna(0)
vehicle_3w["TOTAL"] = pd.to_numeric(vehicle_3w["TOTAL"], errors="coerce").fillna(0)
vehicle_4w["TOTAL"] = pd.to_numeric(vehicle_4w["TOTAL"], errors="coerce").fillna(0)

# Summary Metrics
st.markdown("### Key Stats")
col1, col2, col3 = st.columns(3)
col1.metric("Total 2W Registered", f"{int(vehicle_2w['TOTAL'].sum()):,}")
col2.metric("Total 3W Registered", f"{int(vehicle_3w['TOTAL'].sum()):,}")
col3.metric("Total 4W Registered", f"{int(vehicle_4w['TOTAL'].sum()):,}")


st.markdown("### Category Contribution & Yearly Trends")

col1, col2 = st.columns(2)

# Pie Chart (Left)
with col1:
    category_totals = {
        "2W": vehicle_2w["TOTAL"].sum(),
        "3W": vehicle_3w["TOTAL"].sum(),
        "4W": vehicle_4w["TOTAL"].sum()
    }
    pie_df = pd.DataFrame(list(category_totals.items()), columns=["Category", "Total"])
    fig_pie = px.pie(pie_df, names="Category", values="Total", title="Share of Vehicle Categories")
    st.plotly_chart(fig_pie, use_container_width=True)

# Trend Chart (Right)
with col2:
    combined = pd.concat([vehicle_2w, vehicle_3w, vehicle_4w])
    combined["TOTAL"] = pd.to_numeric(combined["TOTAL"], errors="coerce").fillna(0)
    category_trend = combined.groupby(["Year", "category"])["TOTAL"].sum().reset_index()

    fig_cat_trend = px.bar(category_trend, x="Year", y="TOTAL", color="category", barmode="group",
                           title="Yearly Total by Vehicle Category")
    st.plotly_chart(fig_cat_trend, use_container_width=True)


from streamlit.components.v1 import html


# Ensure 'TOTAL' is numeric
manu_df["TOTAL"] = pd.to_numeric(manu_df["TOTAL"], errors="coerce")

# Calculate top/bottom growth
top_growth = pivot.sort_values('YoY Growth %', ascending=False).head(1)
bottom_growth = pivot.sort_values('YoY Growth %', ascending=True).head(1)

top_name = top_growth.index[0]
top_growth_pct = top_growth['YoY Growth %'].values[0]

bottom_name = bottom_growth.index[0]
bottom_growth_pct = bottom_growth['YoY Growth %'].values[0]

# Total growth
total_2024 = manu_df[manu_df['Year'] == 2024]['TOTAL'].sum()
total_2025 = manu_df[manu_df['Year'] == 2025]['TOTAL'].sum()
overall_growth = total_2025 - total_2024
overall_growth_pct = ((overall_growth / total_2024) * 100) if total_2024 else 0

# Header
st.markdown("###  **Key Insights**")

# Styled markdown layout
html(f"""
    <style>
        .insight-box {{
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        .insight {{
            background-color: #f1f3f5;
            padding: 1rem;
            border-radius: 8px;
            width: 32%;
            min-width: 200px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .label {{
            font-size: 1rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}
        .value {{
            font-size: 0.9rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
        }}
        .delta {{
            font-size: 0.85rem;
            color: #28a745;
        }}
        .delta-negative {{
            color: #d33c3c;
        }}
    </style>

    

    <div class="insight-box">
        <div class="insight" title="{top_name}">
            <div class="label"> Top Growing Manufacturer</div>
            <div class="value">{top_name}</div>
            <div class="delta">{top_growth_pct:.2f}%</div>
        </div>

        <div class="insight" title="{bottom_name.replace('"', '&quot;')}">
            <div class="label"> Lowest Growth Manufacturer</div>
            <div class="value">{bottom_name}</div>
            <div class="delta delta-negative">{bottom_growth_pct:.2f}%</div>
        </div>

        <div class="insight">
            <div class="label"> Overall Registration Growth</div>
            <div class="value">{overall_growth:,.0f} units</div>
            <div class="delta">{overall_growth_pct:.2f}%</div>
        </div>
    </div>
""", height=300)

# Create a DataFrame for export
insights_df = pd.DataFrame({
    "Metric": [
        "Top Growing Manufacturer",
        "Top Growth %",
        "Lowest Growth Manufacturer",
        "Lowest Growth %",
        "Overall Growth Units",
        "Overall Growth %"
    ],
    "Value": [
        top_name,
        f"{top_growth_pct:.2f}%",
        bottom_name,
        f"{bottom_growth_pct:.2f}%",
        f"{overall_growth:,} units",
        f"{overall_growth_pct:.2f}%"
    ]
})

# Convert to CSV
csv_data = insights_df.to_csv(index=False).encode("utf-8")

# Download button
st.download_button(
    label="Download Key Insights (CSV)",
    data=csv_data,
    file_name="key_insights.csv",
    mime="text/csv"
)
