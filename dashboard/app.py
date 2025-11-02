# dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.express as px

CSV_PATH = 'data/solar_readings.csv'

st.title("Solar Energy Dashboard")

df = pd.read_csv(CSV_PATH)
df['Date'] = pd.to_datetime(df['Date'])

# Line chart
st.subheader("Daily Solar Generation")
fig_line = px.line(df, x='Date', y='Daily_kWh', title='Daily Solar Generation')
st.plotly_chart(fig_line)

# Monthly bar chart
st.subheader("Monthly Solar Generation")
df['Month'] = df['Date'].dt.to_period('M')
monthly = df.groupby('Month')['Daily_kWh'].sum().reset_index()
fig_bar = px.bar(monthly, x='Month', y='Daily_kWh', title='Monthly Solar Generation')
st.plotly_chart(fig_bar)

# Show CSV data
st.subheader("Raw Data")
st.dataframe(df)

