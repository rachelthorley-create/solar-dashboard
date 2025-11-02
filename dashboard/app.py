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

# Parse dates in DD/MM/YYYY format safely
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
invalid_dates = df['Date'].isna().sum()
if invalid_dates > 0:
    st.warning(f"{invalid_dates} invalid date rows found and removed.")
    df = df.dropna(subset=['Date'])

# Sort by date
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

# Calendar heatmap (requires cloud-adjusted sun hours or Daily_kWh)
st.subheader("Calendar Heatmap (Daily kWh)")
if 'Daily_kWh' in df.columns:
    import matplotlib.pyplot as plt
    import calmap
    import io

    df.set_index('Date', inplace=True)
    daily_series = df['Daily_kWh']
    fig, ax = plt.subplots(figsize=(15, 5))
    calmap.calendarplot(daily_series, cmap='YlOrRd', fillcolor='lightgrey', linewidth=0.5, ax=ax)
    st.pyplot(fig)
else:
    st.info("Daily_kWh column not found for heatmap.")

# Display raw CSV data
st.subheader("Raw Data")
st.dataframe(df)
