# scripts/fetch_weather.py
import pandas as pd
import requests
from datetime import datetime

# CONFIG
API_KEY = 'YOUR_VISUAL_CROSSING_API_KEY'  # Replace with your key
LOCATION = 'CO5 8TA, UK'
CSV_PATH = 'data/solar_readings.csv'

def fetch_weather_for_date(date_str):
    """
    Fetch daily weather from Visual Crossing for a given date (YYYY-MM-DD format)
    """
    # Convert to ISO format for API
    date_iso = pd.to_datetime(date_str, format='%d/%m/%Y', errors='coerce')
    if pd.isna(date_iso):
        return None  # Invalid date

    date_iso_str = date_iso.strftime('%Y-%m-%d')
    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{LOCATION}/{date_iso_str}/{date_iso_str}?unitGroup=metric&key={API_KEY}&include=days'
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching {date_str}: {response.status_code}")
        return None

    data = response.json()
    day = data['days'][0]
    return {
        'Temp_Max_C': day.get('tempmax', None),
        'Temp_Min_C': day.get('tempmin', None),
        'CloudCover_Percent': day.get('cloudcover', None),
        'Sun_Hours': day.get('sunHours', None),
        'Condition': day.get('conditions', None)
    }

def update_csv_with_weather():
    df = pd.read_csv(CSV_PATH)

    # Parse dates safely
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    invalid_dates = df['Date'].isna().sum()
    if invalid_dates > 0:
        print(f"Warning: {invalid_dates} invalid date rows removed.")
        df = df.dropna(subset=['Date'])

    # Fill missing weather data
    for idx, row in df.iterrows():
        # Check if weather columns are missing or NaN
        missing_weather = (
            pd.isna(row.get('Temp_Max_C')) or
            pd.isna(row.get('Temp_Min_C')) or
            pd.isna(row.get('CloudCover_Percent')) or
            pd.isna(row.get('Sun_Hours')) or
            pd.isna(row.get('Condition'))
        )
        if missing_weather:
            date_str = row['Date'].strftime('%d/%m/%Y')
            weather = fetch_weather_for_date(date_str)
            if weather:
                for key, value in weather.items():
                    df.at[idx, key] = value

    # Save updated CSV
    df.to_csv(CSV_PATH, index=False)
    print("CSV updated with weather data.")

if __name__ == '__main__':
    update_csv_with_weather()
