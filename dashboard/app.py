# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calendar
from datetime import datetime, timedelta

st.set_page_config(page_title="Solar Dashboard", layout="wide")
st.title("Solar Dashboard")

# -----------------------
# Sidebar: Settings
# -----------------------
st.sidebar.header("Settings")
start_date = st.sidebar.date_input("Start Date", datetime(2025, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime(2025, 12, 31))

if start_date > end_date:
    st.sidebar.error("Start date must be before end date")

# -----------------------
# Generate example data
# -----------------------
dates = pd.date_range(start=start_date, end=end_date, freq='D')
values = np.random.randint(0, 100, len(dates))  # Replace with real kWh data

data = pd.DataFrame({'date': dates, 'kwh': values})
data.set_index('date', inplace=True)

# -----------------------
# Calendar Heatmap
# -----------------------
def plot_calendar_heatmap(df):
    df['month'] = df.index.month
    df['dow'] = df.index.weekday
    df['week'] = df.index.isocalendar().week
    
    months = df['month'].unique()
    fig, axes = plt.subplots(len(months), 1, figsize=(15, len(months)*1.5))
    
    if len(months) == 1:
        axes = [axes]
        
    for ax, month in zip(axes, months):
        month_data = df[df['month'] == month]
        pivot = month_data.pivot(index='dow', columns='week', values='kwh')
        im = ax.imshow(pivot, cmap='Oranges', aspect='auto', origin='lower', vmin=0, vmax=df['kwh'].max())
        ax.set_yticks(range(7))
        ax.set_yticklabels(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
        ax.set_title(calendar.month_name[month])
        
    fig.colorbar(im, ax=axes, orientation='vertical', label='kWh')
    plt.tight_layout()
    return fig

st.subheader("Calendar Heatmap")
fig_heatmap = plot_calendar_heatmap(data)
st.pyplot(fig_heatmap)

# -----------------------
# Last 7 Days Bar Chart
# -----------------------
st.subheader("Last 7 Days Generation")
last7 = data.tail(7)
st.bar_chart(last7['kwh'])

# -----------------------
# Rolling Average Line Chart
# -----------------------
st.subheader("Monthly Comparison with Rolling Average")
current_month = datetime.now().month
current_year = datetime.now().year

# Checkbox to include past years
st.sidebar.subheader("Compare Past Years")
years_available = [2024, 2023, 2022]
selected_years = st.sidebar.multiselect("Include past years:", years_available)

line_data = pd.DataFrame()
# Current month this year
this_month_data = data[(data.index.month == current_month) & (data.index.year == current_year)]
line_data[f'{current_year}'] = this_month_data['kwh'].rolling(window=3).mean()

# Add past years if selected
for y in selected_years:
    past_data = data[(data.index.month == current_month) & (data.index.year == y)]
    line_data[f'{y}'] = past_data['kwh'].rolling(window=3).mean()

st.line_chart(line_data)

# -----------------------
# Data Input Section
# -----------------------
st.subheader("Today's Data Input")
col1, col2 = st.columns(2)

with col1:
    temperature = st.number_input("Temperature (°C)", value=20.0)
    sunlight = st.number_input("Sunlight (hours)", value=5.0)
    wind_speed = st.number_input("Wind Speed (m/s)", value=3.0)

with col2:
    kwh_today = st.number_input("Cumulative kWh today", value=0.0)

if st.button("Save Today's Data"):
    today = pd.to_datetime("today").normalize()
    new_row = pd.DataFrame({'kwh': [kwh_today]}, index=[today])
    data = pd.concat([data, new_row])
    st.success("Today's data added!")

st.write("Preview of dataset:")
st.dataframe(data.tail(10))
