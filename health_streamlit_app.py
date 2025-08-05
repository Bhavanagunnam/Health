
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Generate synthetic healthcare data
np.random.seed(123)
n = 1000
df = pd.DataFrame({
    "Age": np.random.randint(18, 90, n),
    "Gender": np.random.choice(["Male", "Female"], n),
    "Medical_Condition": np.random.choice(
        ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "Arthritis", "Cancer", "Depression"], n),
    "Billing_Amount": np.round(np.random.uniform(100, 5000, n), 2),
    "Date_of_Admission": pd.to_datetime("2023-01-01") + pd.to_timedelta(np.random.randint(0, 1000, n), unit="D")
})
df["Discharge_Date"] = df["Date_of_Admission"] + pd.to_timedelta(np.random.randint(1, 15, n), unit="D")

# Sidebar filters
st.sidebar.title("Filters")
gender = st.sidebar.selectbox("Gender", ["All"] + list(df["Gender"].unique()))
age_range = st.sidebar.slider("Age Range", int(df["Age"].min()), int(df["Age"].max()), (int(df["Age"].min()), int(df["Age"].max())))
date_range = st.sidebar.date_input("Date Range", [df["Date_of_Admission"].min(), df["Discharge_Date"].max()])
condition = st.sidebar.selectbox("Medical Condition", ["All"] + list(df["Medical_Condition"].unique()))
download = st.sidebar.button("Download Filtered Data")

# Apply filters
dff = df.copy()
if gender != "All":
    dff = dff[dff["Gender"] == gender]
if condition != "All":
    dff = dff[dff["Medical_Condition"] == condition]
dff = dff[dff["Age"].between(age_range[0], age_range[1])]
dff = dff[
    (dff["Date_of_Admission"] >= pd.to_datetime(date_range[0])) &
    (dff["Discharge_Date"] <= pd.to_datetime(date_range[1]))
]

# Tab selection
tab = st.selectbox("Select Visualization", [
    "Age Distribution", "Gender Distribution", "Top Conditions", "Billing by Condition",
    "Age vs Billing", "Age by Gender", "Billing by Gender", "Billing Trend", "Summary"
])

# Plotting
if tab == "Age Distribution":
    fig = px.histogram(dff, x="Age", nbins=20, title="Age Distribution")
elif tab == "Gender Distribution":
    fig = px.histogram(dff, x="Gender", title="Gender Distribution")
elif tab == "Top Conditions":
    top = dff["Medical_Condition"].value_counts().nlargest(10).reset_index()
    top.columns = ["Condition", "Count"]
    fig = px.bar(top, y="Condition", x="Count", orientation="h", title="Top Medical Conditions")
elif tab == "Billing by Condition":
    fig = px.box(dff, x="Medical_Condition", y="Billing_Amount", title="Billing by Condition")
elif tab == "Age vs Billing":
    fig = px.scatter(dff, x="Age", y="Billing_Amount", color="Medical_Condition", title="Age vs Billing Amount")
elif tab == "Age by Gender":
    fig = px.histogram(dff, x="Age", color="Gender", barmode="overlay", nbins=20, title="Age by Gender")
elif tab == "Billing by Gender":
    fig = px.histogram(dff, x="Billing_Amount", color="Gender", barmode="overlay", nbins=50, title="Billing by Gender")
elif tab == "Billing Trend":
    trend = dff.groupby("Date_of_Admission")["Billing_Amount"].sum().reset_index()
    fig = px.line(trend, x="Date_of_Admission", y="Billing_Amount", title="Billing Amount Trend Over Time")
elif tab == "Summary":
    st.subheader("Summary Statistics")
    st.text(dff.describe(include="all", datetime_is_numeric=True).to_string())
    fig = None

if tab != "Summary" and fig:
    st.plotly_chart(fig)

# Download CSV
if download:
    st.download_button(
        label="Download CSV",
        data=dff.to_csv(index=False),
        file_name="filtered_healthcare_data.csv",
        mime="text/csv"
    )
