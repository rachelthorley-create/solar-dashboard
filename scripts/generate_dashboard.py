# scripts/generate_dashboard.py
import pandas as pd
import plotly.express as px
import calmap
import matplotlib.pyplot as plt

CSV_PATH = 'data/solar_readings.csv'
DASHBOARD_OUTPUT = 'dashboard/plots/'

def generate_line_chart(df):
    fig = px.line(df, x='Date', y='Daily_kWh', title='Daily Solar Generation')
    fig.write_html(DASHBOARD_OUTPUT + 'line_chart.html')

def generate_monthly_bar(df):
    df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M')
    monthly = df.groupby('Month')['Daily_kWh'].sum().reset_index()
    fig = px.bar(monthly, x='Month', y='Daily_kWh', title='Monthly Solar Generation')
    fig.write_html(DASHBOARD_OUTPUT + 'monthly_bar.html')

def generate_calendar_heatmap(df):
    df['Date'] = pd.to_datetime(df['Date'])
    daily_series = pd.Series(df['Daily_kWh'].values, index=df['Date'])
    plt.figure(figsize=(15,5))
    calmap.calendarplot(daily_series, cmap='YlOrRd', fillcolor='lightgrey', linewidth=0.5)
    plt.title('Calendar Heatmap of Daily kWh')
    plt.savefig(DASHBOARD_OUTPUT + 'calendar_heatmap.png')
    plt.close()

def main():
    df = pd.read_csv(CSV_PATH)
    generate_line_chart(df)
    generate_monthly_bar(df)
    generate_calendar_heatmap(df)
    print("Dashboard plots generated.")

if __name__ == '__main__':
    main()

