# scripts/update_daily.py
import pandas as pd

CSV_PATH = 'data/solar_readings.csv'

def compute_daily_kwh():
    # Load CSV
    df = pd.read_csv(CSV_PATH)

    # Parse dates safely in DD/MM/YYYY format
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    invalid_dates = df['Date'].isna().sum()
    if invalid_dates > 0:
        print(f"Warning: {invalid_dates} invalid date rows removed.")
        df = df.dropna(subset=['Date'])

    # Sort by date
    df = df.sort_values('Date')

    # Calculate Daily_kWh from Cumulative_kWh
    df['Daily_kWh'] = df['Cumulative_kWh'].diff()
    df.loc[df['Daily_kWh'].isna(), 'Daily_kWh'] = 0  # first day

    # Interpolate missing daily values (for missing readings)
    missing_mask = df['Data_Flag'].str.lower() == 'missing'
    df.loc[missing_mask, 'Daily_kWh'] = df['Daily_kWh'].interpolate(method='linear')

    # Calculate cloud-adjusted sun hours if columns exist
    if 'Sun_Hours' in df.columns and 'CloudCover_Percent' in df.columns:
        df['Sun_Hours_Cloud_Adjusted'] = (df['Sun_Hours'] * (1 - df['CloudCover_Percent']/100)).round(1)

    # Save updated CSV
    df.to_csv(CSV_PATH, index=False)
    print("Daily kWh and cloud-adjusted sun hours updated.")

if __name__ == '__main__':
    compute_daily_kwh()


