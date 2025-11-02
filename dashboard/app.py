# app.py (in dashboard/)

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calendar
from datetime import datetime, timedelta
import plotly.express as px
import requests
from pathlib import Path

st.set_page_config(page_title="Solar Dashboard", layout="wide")
st.title("Solar Dashboard")

# -----------------------
# 1. Load CSV data
# -----------------------
@st.cache_data
def load_data():
    BASE_DIR = Path(__file__).parent
    CSV_PATH = BASE_DIR.parent / "data" / "solar_data.csv"
    df = pd.read_csv(CSV_PATH, parse_dates=['date'])
    df = df.rename(columns={'Cumulative_kWh':'kwh'})
    df = df.drop_duplicates(subset='date', keep='last')
    df = df.set_index('date').sort_index()
    return df

data = load_data()

# -----------------------
# 2. Fill missing days and calculate daily_kwh
# -----------------------
all_dates = pd.date_range(data.index.min(), data.index.max())
data = data.reindex(all_dates)

# Initialize daily_kwh column
data['daily_kwh'] = 0.0
prev_idx = None
prev_reading = None

for idx, row in data.iterrows():
    curr_reading = row['kwh']
    if pd.notna(curr_reading):
        if prev_idx is not None:
            days_gap = (idx - prev_idx).days
            if days_gap > 0:
                daily_value = max(curr_reading - prev_reading, 0) / days_gap
                for i in range(1, days_gap + 1):
                    data.loc[prev_idx + pd.Timedelta(days=i), 'daily_kwh'] = daily_value
        prev_idx = idx
        prev_reading = curr_reading

# First day daily_kwh
if pd.notna(data['kwh'].iloc[0]):
    data['daily_kwh'].iloc[0] = 0

# -----------------------
# 3. Today's Meter Reading
# -----------------------
st.subheader("Today's Meter Reading")
yesterday = pd.to_datetime("today").normalize() - pd.Timedelta(days=1)
default_meter = data.loc[yesterday, 'kwh'] if yesterday in data.index else 0.0
meter_reading = st.number_input("Meter Reading (kWh, cumulative)", value=float(default_meter), step=0.1)

if st.button("Save Today's Reading"):
    today = pd.to_datetime("today").normalize()
    prev_reading_for_today = data['kwh'].iloc[-1] if len(data)>0 else meter_reading
    daily_gen = max(meter_reading - prev_reading_for_today, 0)
    new_row = pd.DataFrame({'kwh':[meter_reading], 'daily_kwh':[daily_gen]}, index=[today])
    data.update(new_row)
    if today not in data.index:
        data = pd.concat([data, new_row])
    st.success("Today's meter reading saved!")

# -----------------------
# 4. Today's Weather
# -----------------------
st.subheader("Today's Weather")
today_str = pd.to_datetime("today").strftime("%A, %d %B %Y")
st.write(f"**Date:** {today_str}")

VC_API_KEY = "YOUR_VISUALCROSSING_KEY"  # Replace with your key
POSTCODE = "CO5 8TA,UK"
URL = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{POSTCODE}/today?unitGroup=metric&key={VC_API_KEY}&include=current"

try:
    response = requests.get(URL)
    response.raise_for_status()
    weather = response.json()
    current = weather['currentConditions']
    temp = current['temp']
    wind = current['windspeed']
    conditions = current['conditions']
    sunhours = current.get('sunhours', None)

    condition_icon_map = {
        "Clear": "☀️",
        "Partially cloudy": "⛅",
        "Cloudy": "☁️",
        "Rain": "🌧️",
        "Snow": "❄️",
        "Fog": "🌫️"
    }
    icon = condition_icon_map.get(conditions, "🌡️")

    col1, col2 = st.columns([1,2])
    with col1:
        st.write(icon)
    with col2:
        st.write(f"**Condition:** {conditions}")
        st.write(f"**Temperature:** {temp} °C")
        st.write(f"**Wind speed:** {wind} m/s")
        if sunhours is not None:
            st.write(f"**Sunlight hours:** {sunhours:.1f} h")
except Exception as e:
    st.write("Unable to fetch today's weather. Showing placeholder values.")
    st.write(f"Error: {e}")
    st.write("☀️ Temperature: 21°C")
    st.write("Sunlight hours: 6")
    st.write("Wind Speed: 3 m/s")

# -----------------------
# 5. Last 7 Days Data & Info Panel
# -----------------------
st.subheader("Last 7 Days Data & Summary")
last7 = data.tail(7).copy()
last7_display = last7[['kwh','daily_kwh']].copy()
last7_display.rename(columns={'kwh':'Meter Reading (kWh)', 'daily_kwh':'Daily Generation (kWh)'}, inplace=True)
st.dataframe(last7_display)

# Info Panel
today_dt = pd.to_datetime("today").normalize()
this_week = data.last('7D')
this_month = data[data.index.month == today_dt.month]
this_year = data[data.index.year == today_dt.year]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Today", f"{data['daily_kwh'].iloc[-1]:.1f} kWh")
col2.metric("This Week", f"{this_week['daily_kwh'].sum():.1f} kWh")
col3.metric("This Month", f"{this_month['daily_kwh'].sum():.1f} kWh")
col4.metric("Year to Date", f"{this_year['daily_kwh'].sum():.1f} kWh")

# Last 7 days bar chart
fig, ax = plt.subplots(figsize=(8,4))
ax.bar(last7.index.strftime('%d-%b'), last7['daily_kwh'], width=0.5, color='orange')
ax.set_ylabel('kWh')
ax.set_title('Last 7 Days Solar Generation')
plt.xticks(rotation=45)
st.pyplot(fig)

# -----------------------
# 6. Monthly Comparison (Rolling Average)
# -----------------------
st.subheader("Monthly Comparison (Rolling Average)")
current_month = datetime.now().month
current_year = datetime.now().year

st.sidebar.subheader("Compare Past Years")
years_available = [2024, 2023, 2022]
selected_years = st.sidebar.multiselect("Include past years:", years_available)

line_rows = []
for y in [current_year] + selected_years:
    month_data = data[(data.index.year==y) & (data.index.month==current_month)].copy()
    if not month_data.empty:
        month_data['rolling_kwh'] = month_data['daily_kwh'].rolling(window=3).mean()
        for idx, row in month_data.iterrows():
            line_rows.append({'date': idx, 'Year': y, 'KWh': row['rolling_kwh']})

line_df = pd.DataFrame(line_rows)
if not line_df.empty:
    fig1 = px.line(line_df, x='date', y='KWh', color='Year',
                   labels={'KWh':'kWh', 'date':'Date'},
                   title=f"Rolling Average Daily Generation - Month {current_month}")
    fig1.update_xaxes(tickformat='%d-%b')
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.write("No data available for selected months/years.")

# -----------------------
# 7. Monthly Total Generation
# -----------------------
st.subheader("Monthly Total Generation (Grouped by Year)")
monthly_totals = data.assign(year=data.index.year, month=data.index.month)
monthly_totals = monthly_totals.groupby(['month','year'])['daily_kwh'].sum().reset_index()
monthly_totals['month_str'] = monthly_totals['month'].apply(lambda x: calendar.month_abbr[x])

fig2 = px.bar(monthly_totals, x='month_str', y='daily_kwh', color='year', barmode='group',
              labels={'daily_kwh':'Total kWh', 'month_str':'Month', 'year':'Year'},
              text='daily_kwh')
fig2.update_layout(showlegend=False)
st.plotly_chart(fig2, use_container_width=True)

# -----------------------
# 8. Calendar Heatmap
# -----------------------
st.subheader("Calendar Heatmap")
def plot_calendar_heatmap(df):
    df['month'] = df.index.month
    df['dow'] = df.index.weekday
    df['week'] = df.index.isocalendar().week
    months = df['month'].unique()
    fig, axes = plt.subplots(len(months), 1, figsize=(15, len(months)*1.5))
    if len(months) == 1:
        axes = [axes]
    for ax, month in zip(axes, months):
        month_data = df[df['month']==month]
        pivot = month_data.pivot(index='dow', columns='week', values='daily_kwh')
        im = ax.imshow(pivot, cmap='Oranges', aspect='auto', origin='lower', vmin=0, vmax=df['daily_kwh'].max())
        ax.set_yticks(range(7))
        ax.set_yticklabels(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
        ax.set_title(calendar.month_name[month])
    fig.colorbar(im, ax=axes, orientation='vertical', label='kWh')
    plt.tight_layout()
    return fig

fig_heatmap = plot_calendar_heatmap(data)
st.pyplot(fig_heatmap)
