# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calendar
from datetime import datetime, timedelta
import plotly.express as px

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
# Example dataset (replace with real data)
# -----------------------
dates = pd.date_range(start=start_date, end=end_date, freq='D')
values = np.random.randint(0, 100, len(dates))  # Replace with real kWh readings

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
fig, ax = plt.subplots(figsize=(8,4))
ax.bar(last7.index.strftime('%d-%b'), last7['kwh'], width=0.5, color='orange')
ax.set_ylabel('kWh')
ax.set_title('Last 7 Days Solar Generation')
plt.xticks(rotation=45)
st.pyplot(fig)

# -----------------------
# Monthly Comparison (Rolling Average) - Interactive
# -----------------------
st.subheader("Monthly Comparison (Rolling Average)")
current_month = datetime.now().month
current_year = datetime.now().year

st.sidebar.subheader("Compare Past Years")
years_available = [2024, 2023, 2022]
selected_years = st.sidebar.multiselect("Include past years:", years_available)

# Prepare dataframe for Plotly
line_data = pd.DataFrame()
for y in [current_year] + selected_years:
    month_data = data[(data.index.year==y) & (data.index.month==current_month)]
    line_data[f'{y}'] = month_data['kwh'].rolling(window=3).mean()
line_data['date'] = month_data.index  # same index for x-axis
line_data_melt = line_data.reset_index(drop=True).melt(id_vars='date', var_name='Year', value_name='kWh')

fig = px.line(line_data_melt, x='date', y='kWh', color='Year',
              labels={'KWh':'kWh', 'date':'Date'},
              title=f"Rolling Average Solar Generation for Month {current_month}")
fig.update_xaxes(tickformat='%d-%b')
st.plotly_chart(fig, use_container_width=True)

# -----------------------
# Monthly Total Generation - Grouped Bar Chart
# -----------------------
st.subheader("Monthly Total Generation (Grouped by Year)")
monthly_totals = data.groupby([data.index.year, data.index.month])['kwh'].sum().reset_index()
monthly_totals['month_str'] = monthly_totals['date'].dt.month.apply(lambda x: calendar.month_abbr[x])

fig2 = px.bar(monthly_totals, x='month', y='kwh', color='year', barmode='group',
              labels={'kwh':'Total kWh', 'month':'Month', 'year':'Year'},
              text='kwh')
st.plotly_chart(fig2, use_container_width=True)

# -----------------------
# Today's Meter Reading Input
# -----------------------
st.subheader("Today's Meter Reading")

# Default to yesterday's reading
yesterday = pd.to_datetime("today").normalize() - pd.Timedelta(days=1)
default_meter = data.loc[yesterday, 'kwh'] if yesterday in data.index else 0.0

meter_reading = st.number_input("Meter Reading (kWh, cumulative)", value=float(default_meter), step=0.1)
if st.button("Save Today's Reading"):
    today = pd.to_datetime("today").normalize()
    new_row = pd.DataFrame({'kwh':[meter_reading]}, index=[today])
    if today in data.index:
        data.loc[today, 'kwh'] = meter_reading
    else:
        data = pd.concat([data,new_row])
    st.success("Today's meter reading saved!")

# -----------------------
# Weather Info Panel
# -----------------------
st.subheader("Weather Stats (from API)")
col1, col2 = st.columns(2)

with col1:
    # Example static icons; replace with API values later
    weather_icon = "☀️"
    temperature = 21
    sunlight_hours = 6
    wind_speed = 3

    st.write(f"{weather_icon} Temperature: {temperature}°C")
    st.write(f"Sunlight hours: {sunlight_hours}")
    st.write(f"Wind Speed: {wind_speed} m/s")

st.write("Preview of dataset:")
st.dataframe(data.tail(10))
