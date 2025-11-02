# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calendar
from datetime import datetime, timedelta

st.set_page_config(page_title="Solar Dashboard", layout="wide")
st.title("Solar Dashboard - Calendar Heatmap")

# --- Generate Example Data ---
st.sidebar.header("Settings")
start_date = st.sidebar.date_input("Start Date", datetime(2025, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime(2025, 12, 31))

if start_date > end_date:
    st.sidebar.error("Start date must be before end date")

# Create date range
dates = pd.date_range(start=start_date, end=end_date, freq='D')
# Random example values
values = np.random.randint(0, 100, len(dates))

data = pd.DataFrame({'date': dates, 'value': values})
data.set_index('date', inplace=True)

# --- Function to plot calendar heatmap ---
def plot_calendar_heatmap(df):
    # Pivot data to month x day-of-week
    df['month'] = df.index.month
    df['dow'] = df.index.weekday  # Monday=0
    df['week'] = df.index.isocalendar().week

    months = df['month'].unique()
    fig, axes = plt.subplots(len(months), 1, figsize=(15, len(months)*1.5))
    
    if len(months) == 1:
        axes = [axes]

    for ax, month in zip(axes, months):
        month_data = df[df['month'] == month]
        pivot = month_data.pivot(index='dow', columns='week', values='value')
        im = ax.imshow(pivot, cmap='YlGn', aspect='auto', origin='lower')
        ax.set_yticks(range(7))
        ax.set_yticklabels(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
        ax.set_title(calendar.month_name[month])
    fig.colorbar(im, ax=axes, orientation='vertical', label='Value')
    plt.tight_layout()
    return fig

# --- Plot heatmap ---
fig = plot_calendar_heatmap(data)
st.pyplot(fig)

