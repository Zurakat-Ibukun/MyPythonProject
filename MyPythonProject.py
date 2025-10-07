import pandas as pd
import streamlit as st
import altair as alt

# Load Data
def load_data():
    df = pd.read_csv("Aircrashes.csv")

    # Replace NaN with 'Unknown'
    df = df.fillna({"Country/Region": "Unspecified",
                    "Operator": "Unspecified",
                    "Aircraft": "Unspecified",
                    "Location": "Unspecified"})
    
    st.write("Columns in dataset:", df.columns.tolist())

     # Make sure fatality columns exist
    if "Fatalities (air)" in df.columns:
        df.rename(columns={"Fatalities (air)": "Air"}, inplace=True)
    else:
        df["Air"] = 0   # fallback if column missing

    if "Ground" not in df.columns:
        df["Ground"] = 0  # fallback if missing

    # Create new Fatalities column = Air + Ground
    df["Fatalities"] = df["Air"].fillna(0) + df["Ground"].fillna(0)

    # Convert Date
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month_name()
    return df

try:
    df = load_data()

    # Title
    st.title("Aircrash Analysis Dashboard")

    
    # Filters
    filters = {
        "Country/Region": df["Country/Region"].unique(),
        "Aircraft": df["Aircraft"].unique(),
        "Operator": df["Operator"].unique(),
        "Year": df["Year"].dropna().unique() if "Year" in df else []
    }

    selected_filters = {}
    for key, options in filters.items():
        selected_filters[key] = st.sidebar.multiselect(key, options)

    # Apply filters
    filtered_df = df.copy()
    for key, selected_values in selected_filters.items():
        if selected_values:
            filtered_df = filtered_df[filtered_df[key].isin(selected_values)]

    # Quick KPIs
    st.write("### Quick Overview")

    total_crashes = len(filtered_df)
    total_fatalities = filtered_df["Fatalities"].sum()
    total_aboard = filtered_df["Aboard"].sum()
    avg_fatalities = filtered_df["Fatalities"].mean()
    percent_fatalities = f"{(total_fatalities / df['Fatalities'].sum()) * 100:,.2f}%" if df["Fatalities"].sum() > 0 else "0%"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Crashes", total_crashes)
    col2.metric("Total Fatalities", int(total_fatalities))
    col3.metric("Avg Fatalities", f"{avg_fatalities:,.2f}")
    col4.metric("Fatalities Contribution", percent_fatalities)

    # =======================
    # Research Questions
    # =======================

    st.write("## Research Questions")

    # 1. Which country/region has the highest number of crashes by aircraft?
    st.write("### Q1: Highest Number of Crashes by Country & Aircraft")
    q1 = filtered_df.groupby(["Country/Region", "Aircraft"]).size().reset_index(name="Crashes")
    q1_top = q1.sort_values(by="Crashes", ascending=False).head(10)
    st.dataframe(q1_top)
    st.altair_chart(alt.Chart(q1_top).mark_bar().encode(x="Crashes:Q", y="Country/Region:N", color="Aircraft:N", tooltip=["Country/Region","Aircraft","Crashes"]), use_container_width=True)

    # 2. Top 6 aircraft manufacturers by crashes
    st.write("### Q2: Top 6 Aircraft Manufacturers")
    q2 = filtered_df["Aircraft"].value_counts().reset_index().head(6)
    q2.columns = ["Aircraft", "Crashes"]
    st.dataframe(q2)
    st.altair_chart(alt.Chart(q2).mark_bar().encode(x="Crashes:Q", y="Aircraft:N", color="Aircraft:N"), use_container_width=True)

    # 3. Top 5 Operators with crashes
    st.write("### Q3: Top 5 Operators by Crashes")
    q3 = filtered_df["Operator"].value_counts().reset_index().head(5)
    q3.columns = ["Operator", "Crashes"]
    st.dataframe(q3)
    st.altair_chart(alt.Chart(q3).mark_bar().encode(x="Crashes:Q", y="Operator:N", color="Operator:N"), use_container_width=True)

    # 4. Top 10 crash distribution by year
    if "Year" in filtered_df.columns:
        st.write("### Q4: Top 10 Years by Number of Crashes")
        q4 = filtered_df["Year"].value_counts().reset_index().head(10)
        q4.columns = ["Year", "Crashes"]
        st.dataframe(q4.sort_values("Year"))
        st.altair_chart(alt.Chart(q4).mark_line(point=True).encode(x="Year:O", y="Crashes:Q"), use_container_width=True)

    # 5. Top 5 patterns in fatalities based on location
    st.write("### Q5: Top 5 Locations by Fatalities")
    q5 = filtered_df.groupby("Location")["Fatalities"].sum().reset_index().sort_values(by="Fatalities", ascending=False).head(5)
    st.dataframe(q5)
    st.altair_chart(alt.Chart(q5).mark_bar().encode(x="Fatalities:Q", y="Location:N", color="Location:N"), use_container_width=True)

    # 6. Top 5 countries by passengers aboard & fatalities
    st.write("### Q6: Top 5 Countries by Passengers Aboard & Fatalities")
    q6 = filtered_df.groupby("Country/Region")[["Aboard","Fatalities"]].sum().reset_index().sort_values(by="Aboard", ascending=False).head(5)
    st.dataframe(q6)
    st.altair_chart(alt.Chart(q6).mark_bar().encode(x="Country/Region:N", y="Aboard:Q", color="Country/Region:N"), use_container_width=True)

    # 7. Average number of fatalities
    st.write("### Q7: Average Number of Fatalities")
    st.metric("Average Fatalities per Crash", f"{avg_fatalities:,.2f}")

    # 8. Total number of fatalities
    st.write("### Q8: Total Fatalities")
    st.metric("Total Fatalities", int(total_fatalities))

    # 9. Total number of passengers aboard
    st.write("### Q9: Total Passengers Aboard")
    st.metric("Total Aboard", int(total_aboard))

    # 10. Number of fatalities by month
    if "Month" in filtered_df.columns:
        st.write("### Q10: Fatalities by Month")
        q10 = filtered_df.groupby("Month")["Fatalities"].sum().reset_index().sort_values(by="Fatalities", ascending=False)
        st.dataframe(q10)
        st.altair_chart(alt.Chart(q10).mark_bar().encode(x="Month:N", y="Fatalities:Q", color="Month:N"), use_container_width=True)

except Exception as e:
    st.error("Error: check error details")

    with st.expander("Error Details"):
        st.code(str(e))
