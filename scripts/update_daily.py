# scripts/update_daily.py
import pandas as pd

CSV_PATH = 'data/solar_readings.csv'

def compute_daily_kwh():
    df = pd.read_csv(CSV_PATH)
    df['Daily_kWh'] = df['Cumulative_kWh'].diff()
    df.loc[df['Daily_kWh'].isna(), 'Daily_kWh'] = 0  # first day

    # Handle missing data (interpolate)
    missing_mask = df['Data_Flag'] == 'Missing'
    df.loc[missing_mask, 'Daily_kWh'] = df['Daily_kWh'].interpolate(method='linear')

    df.to_csv(CSV_PATH, index=False)
    print("Daily kWh updated.")

if __name__ == '__main__':
    compute_daily_kwh()

