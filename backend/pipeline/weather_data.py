"""
weather_data.py
───────────────
Fetches and caches real historical daily meteorological data from the
Open-Meteo Archive API (Copernicus ERA5 / NOAA reanalysis) for the 5
core CPCB cities (2018-01-01 to 2024-12-31).

Parameters fetched:
- temperature_2m_mean (°C)
- relative_humidity_2m_mean (%)
- wind_speed_10m_max (km/h)
- wind_direction_10m_dominant (degrees)
- surface_pressure_mean (hPa)
"""

import os
import time
import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
WEATHER_DIR = os.path.join(BACKEND_DIR, "data", "weather")

CITY_COORDINATES = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
}

WEATHER_COLS = [
    "temperature_2m_mean",
    "relative_humidity_2m_mean",
    "wind_speed_10m_max",
    "wind_direction_10m_dominant",
    "surface_pressure_mean"
]


def fetch_city_historical_weather(city: str, start_date: str = "2018-01-01", end_date: str = "2024-12-31") -> pd.DataFrame:
    """Fetch or load cached daily weather for a city."""
    os.makedirs(WEATHER_DIR, exist_ok=True)
    cache_path = os.path.join(WEATHER_DIR, f"{city.lower()}_weather.csv")

    if os.path.exists(cache_path):
        df = pd.read_csv(cache_path)
        df["Date"] = pd.to_datetime(df["Date"])
        return df

    coords = CITY_COORDINATES.get(city)
    if not coords:
        raise ValueError(f"Unknown city coordinates for {city}")

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={coords['lat']}&longitude={coords['lon']}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&daily={','.join(WEATHER_COLS)}"
        "&timezone=Asia/Kolkata"
    )

    print(f"  [Weather] Fetching Open-Meteo ERA5 weather for {city} ({start_date} to {end_date})...")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    daily = data.get("daily", {})
    df = pd.DataFrame({
        "Date": daily.get("time", []),
        "temp": daily.get("temperature_2m_mean", []),
        "humidity": daily.get("relative_humidity_2m_mean", []),
        "wind_speed": daily.get("wind_speed_10m_max", []),
        "wind_dir": daily.get("wind_direction_10m_dominant", []),
        "pressure": daily.get("surface_pressure_mean", []),
    })

    df["City"] = city
    df["Date"] = pd.to_datetime(df["Date"])

    # Forward/backward fill any isolated missing meteorological values
    for c in ["temp", "humidity", "wind_speed", "wind_dir", "pressure"]:
        df[c] = df[c].ffill().bfill()

    df.to_csv(cache_path, index=False)
    print(f"  [Weather] Cached {len(df)} weather records to {cache_path}")
    time.sleep(1.0)  # Respect rate limits
    return df


def load_all_weather_data() -> pd.DataFrame:
    """Load weather data for all 5 cities combined."""
    dfs = []
    for city in CITY_COORDINATES:
        df = fetch_city_historical_weather(city)
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


if __name__ == "__main__":
    combined = load_all_weather_data()
    print(f"\n[OK] Total weather records fetched: {len(combined)}")
    print(combined.head())
