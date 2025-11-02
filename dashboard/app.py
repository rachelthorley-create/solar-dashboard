# dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.express as px

CSV_PATH = 'data/solar_readings.csv'

st.title("Solar Energy Dashboard")

# Load CSV
try:
    df = pd.read_csv(CSV_PATH)
except FileNotFoundError:
    st.error(f"CSV file not found at {CSV_PATH}. Please upload it.")
    st.stop()

# Parse dates safely
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # invalid dates become NaT
invalid_dates = df['Date'].isna().sum()
if invalid_dates > 0:
    st.warning(f"{invalid_dates} invalid date rows found and removed.")
    df = df.dropna(subset=['Date'])

# Ensure data is sorted by date
df = df.sort_values('Date')

# Line chart for daily kWh
st.subheader("Daily Solar Generation")
if 'Daily_kWh' in df.columns:
    fig_line = px.line(df, x='Date', y='Daily_kWh', title='Daily Solar Generation')
    st.plotly_chart(fig_line)
else:
    st.info("Daily_kWh column not found in CSV.")

# Monthly bar chart
st.subheader("Monthly Solar Generation")
if 'Daily_kWh' in df.columns:
    df['Month'] = df['Date'].dt.to_period('M')
    monthly = df.groupby('Month')['Daily_kWh'].sum().reset_index()
    fig_bar = px.bar(monthly, x='Month', y='Daily_kWh', title='Monthly Solar Generation')
    st.plotly_chart(fig_bar)
else:
    st.info("Daily_kWh column not found in CSV.")

# Display raw CSV data
st.subheader("Raw Data")
st.dataframe(df)
