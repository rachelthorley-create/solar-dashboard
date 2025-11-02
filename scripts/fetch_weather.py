# scripts/fetch_weather.py
import pandas as pd
import requests
from datetime import datetime, timedelta

# Config
API_KEY = 'Q53AVJQ9AAU3A9YEMGJXNU5NW'  # replace with your key
LOCATION = 'CO5 8TA, UK'
CSV_PATH = 'data/solar_readings.csv'

def fetch_weather_for_date(date):
    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{LOCATION}/{date}/{date}?unitGroup=metric&key={API_KEY}&include=days'
    response = requests.get(url)
    data = response.json()
    day = data['days'][0]
    return {
        'Temp_Max_C': day['tempmax'],
        'Temp_Min_C': day['tempmin'],
        'CloudCover_Percent': day.get('cloudcover', 0),
        'Sun_Hours': day.get('sunHours', 10),  # fallback to 10
        'Condition': day['conditions']
    }

def update_csv_with_weather():
    df = pd.read_csv(CSV_PATH)
    df['Date'] = pd.to_datetime(df['Date'])
    today = datetime.today().date()

    # Get dates that need weather filled
    missing_weather = df[df['Temp_Max_C'].isna() | df['Temp_Min_C'].isna()]

    for idx, row in missing_weather.iterrows():
        date_str = row['Date'].strftime('%Y-%m-%d')
        weather = fetch_weather_for_date(date_str)
        for key, value in weather.items():
            df.at[idx, key] = value

    df.to_csv(CSV_PATH, index=False)
    print("Weather updated.")

if __name__ == '__main__':
    update_csv_with_weather()

